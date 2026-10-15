"""OpenAI-compatible client for Vercel AI Gateway with a hard spending guard."""
import re
import threading
import time

import requests
from openai import OpenAI, APIStatusError, APIConnectionError, APITimeoutError, RateLimitError

SYSTEM_PROMPT = (
    "You are an expert Blender technical artist. Write one self-contained Python script for "
    "Blender {version} (bpy) that builds the requested scene from scratch.\n"
    "Rules:\n"
    "- Start by removing all existing objects.\n"
    "- Do not create cameras or lights, do not render and do not save or export files; "
    "the evaluation harness handles that.\n"
    "- Use only bpy, bmesh, mathutils and the Python standard library; no add-ons, "
    "external files or network access.\n"
    "- Reply with exactly one ```python code block and nothing else."
)


class BudgetExceeded(Exception):
    pass


class Budget:
    """Reserve worst-case cost before a call, settle with the real cost afterwards."""

    def __init__(self, limit_usd, already_spent=0.0):
        self.limit = limit_usd
        self.spent = already_spent
        self.reserved = 0.0
        self.lock = threading.Lock()

    def reserve(self, amount):
        with self.lock:
            if self.spent + self.reserved + amount > self.limit:
                raise BudgetExceeded(
                    f"next call could cost up to ${amount:.4f}; spent ${self.spent:.4f} "
                    f"of ${self.limit:.2f}")
            self.reserved += amount

    def settle(self, reserved, actual):
        with self.lock:
            self.reserved -= reserved
            self.spent += actual


def fetch_gateway_models(base_url, api_key):
    """Returns {model_id: {"in": usd_per_1M, "out": usd_per_1M}} (pricing may be missing)."""
    r = requests.get(f"{base_url}/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    r.raise_for_status()
    out = {}
    for m in r.json().get("data", []):
        p = m.get("pricing") or {}

        def per_million(key):
            try:
                return float(p[key]) * 1e6  # gateway reports USD per token
            except (KeyError, TypeError, ValueError):
                return None

        out[m["id"]] = {"in": per_million("input"), "out": per_million("output")}
    return out


def extract_code(text):
    if not text:
        return None
    blocks = re.findall(r"```(?:python|py)?[ \t]*\n(.*?)```", text, flags=re.S | re.I)
    if blocks:
        return max(blocks, key=len).strip() + "\n"
    if "import bpy" in text:  # model ignored the format but wrote raw code
        return text.strip() + "\n"
    return None


class GatewayClient:
    def __init__(self, cfg, api_key, budget):
        g = cfg["gateway"]
        self.client = OpenAI(base_url=g["base_url"], api_key=api_key,
                             timeout=g["request_timeout_s"], max_retries=0)
        self.max_retries = g["max_retries"]
        self.gen = cfg["generation"]
        self.budget = budget
        self.system = SYSTEM_PROMPT.format(version=self.gen["blender_version_in_prompt"])
        self.dropped_params = {}  # model -> params removed after a 400 (logged for the paper)

    def _est_input_tokens(self, user):
        return int((len(self.system) + len(user)) / 3) + 50  # deliberately pessimistic

    def generate(self, model, user_prompt):
        mid = model["id"]
        max_out = self.gen["max_output_tokens"]
        worst = (self._est_input_tokens(user_prompt) * model["price_in"]
                 + max_out * model["price_out"]) / 1e6
        self.budget.reserve(worst)
        actual = 0.0
        try:
            params = dict(model.get("extra_params") or {})
            if model.get("send_temperature", True):
                params["temperature"] = self.gen["temperature"]
            params["max_tokens"] = max_out
            for p in self.dropped_params.get(mid, []):
                params.pop(p, None)

            attempt, t0 = 0, time.time()
            while True:
                try:
                    resp = self.client.chat.completions.create(
                        model=mid,
                        messages=[{"role": "system", "content": self.system},
                                  {"role": "user", "content": user_prompt}],
                        **params)
                    break
                except APIStatusError as e:
                    msg = str(e).lower()
                    if e.status_code == 400:
                        bad = [p for p in list(params) if p in msg and p != "max_tokens"]
                        if "max_tokens" in msg and "max_tokens" in params:
                            params["max_completion_tokens"] = params.pop("max_tokens")
                            continue
                        if bad:
                            for p in bad:
                                params.pop(p)
                            self.dropped_params.setdefault(mid, []).extend(bad)
                            continue
                    retriable = isinstance(e, RateLimitError) or e.status_code >= 500
                    if not retriable or attempt >= self.max_retries:
                        raise
                except (APIConnectionError, APITimeoutError):
                    if attempt >= self.max_retries:
                        raise
                attempt += 1
                time.sleep(min(60, 5 * 2 ** attempt))
            latency = time.time() - t0

            u = resp.usage
            pt = getattr(u, "prompt_tokens", 0) or 0
            ct = getattr(u, "completion_tokens", 0) or 0
            details = getattr(u, "completion_tokens_details", None)
            rt = (getattr(details, "reasoning_tokens", 0) or 0) if details else 0
            actual = (pt * model["price_in"] + ct * model["price_out"]) / 1e6
            text = resp.choices[0].message.content if resp.choices else None
            return {
                "text": text,
                "finish_reason": resp.choices[0].finish_reason if resp.choices else None,
                "prompt_tokens": pt, "completion_tokens": ct, "reasoning_tokens": rt,
                "cost_usd_est": actual, "latency_s": round(latency, 2),
                "served_model": getattr(resp, "model", None),
                "params_sent": params,
            }
        finally:
            self.budget.settle(worst, actual)
