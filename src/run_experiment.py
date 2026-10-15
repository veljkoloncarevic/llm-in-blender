"""
Main entry point.

  python -m src.run_experiment                 # full run (asks for confirmation)
  python -m src.run_experiment --yes           # no confirmation prompt
  python -m src.run_experiment --smoke         # no API calls: hand-written reference scripts
  python -m src.run_experiment --limit 8       # only the first 8 attempts (cheap pilot)
  python -m src.run_experiment --report-only   # recompute metrics + report from saved data

The run is resumable: finished attempts are stored in results/records.jsonl and
skipped on restart (API errors are retried). Ctrl+C is safe.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from tqdm import tqdm

from . import checks as checks_mod
from .llm_client import Budget, BudgetExceeded, GatewayClient, extract_code, fetch_gateway_models

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "src" / "blender_harness.py"
RETRY_STATUSES = {"api_error"}


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def load_records(path):
    recs = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    return recs


def run_blender(cfg, script_path, out_dir, threads):
    settings = {"render": cfg["blender"]["render"], "threads": threads}
    sp = out_dir / "settings.json"
    sp.write_text(json.dumps(settings))
    for f in ("result.json", "exec_done"):
        (out_dir / f).unlink(missing_ok=True)
    cmd = [cfg["blender"]["executable"], "-b", "--factory-startup", "-noaudio",
           "-P", str(HARNESS), "--", "--script", str(script_path), "--out", str(out_dir),
           "--settings", str(sp)]
    timed_out = False
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace",
                              timeout=cfg["blender"]["timeout_s"])
        log = proc.stdout + "\n--- stderr ---\n" + proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired as e:
        timed_out, rc = True, None
        log = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
    (out_dir / "blender_log.txt").write_text(log[-200000:], encoding="utf-8")

    rp = out_dir / "result.json"
    if rp.exists() and not timed_out:
        return json.loads(rp.read_text())
    phase = "render" if (out_dir / "exec_done").exists() else "exec"
    if timed_out:
        return {"status": f"timeout_{phase}", "error_type": "Timeout",
                "error_message": f"Blender exceeded {cfg['blender']['timeout_s']} s during {phase}"}
    tail = "\n".join(log.strip().splitlines()[-15:])
    return {"status": f"crash_{phase}", "error_type": "BlenderCrash",
            "error_message": f"return code {rc}: {tail[-1500:]}"}


def code_features(code):
    return {
        "code_lines": len(code.splitlines()),
        "n_bpy_ops_calls": len(re.findall(r"bpy\.ops\.", code)),
        "uses_bmesh": "bmesh" in code,
        "uses_geometry_nodes": "GeometryNodeTree" in code or "'NODES'" in code or '"NODES"' in code,
        "uses_shader_nodes": "node_tree" in code,
    }


def attempt(task, cfg, client, prompts_by_id, run_root, threads, smoke):
    model, pid, rep = task
    p = prompts_by_id[pid]
    out_dir = run_root / "runs" / slug(model["id"]) / pid / f"rep{rep}"
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"model_id": model["id"], "model_label": model["label"], "family": model.get("family"),
           "prompt_id": pid, "tier": p["tier"], "tier_name": p["tier_name"], "rep": rep,
           "dir": str(out_dir.relative_to(run_root)), "timestamp": dt.datetime.now().isoformat()}

    if smoke:
        code = (ROOT / "prompts" / "reference" / f"{pid}.py").read_text()
        rec.update({"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
                    "cost_usd_est": 0.0, "latency_s": 0.0, "finish_reason": "reference"})
    else:
        try:
            g = client.generate(model, p["prompt"])
        except BudgetExceeded:
            raise
        except Exception as e:  # network / provider error -> retried on next run
            rec.update({"status": "api_error", "error_type": type(e).__name__,
                        "error_message": str(e)[:1500]})
            return rec
        (out_dir / "response.json").write_text(json.dumps(g, indent=2), encoding="utf-8")
        rec.update({k: g[k] for k in ("prompt_tokens", "completion_tokens", "reasoning_tokens",
                                      "cost_usd_est", "latency_s", "finish_reason", "served_model")})
        if g["finish_reason"] == "length":
            # reply hit max_output_tokens: the code is incomplete, so do not execute it
            (out_dir / "script_truncated.txt").write_text(g["text"] or "", encoding="utf-8")
            rec.update({"status": "truncated", "error_type": "Truncated",
                        "error_message": f"reply cut at max_output_tokens "
                                         f"({g['completion_tokens']} completion tokens, "
                                         f"{g['reasoning_tokens']} reasoning)"})
            return rec
        code = extract_code(g["text"])
        if code is None:
            rec.update({"status": "no_code", "error_type": "NoCode",
                        "error_message": f"no python code block (finish_reason={g['finish_reason']})"})
            return rec

    script = out_dir / "script.py"
    script.write_text(code, encoding="utf-8")
    rec.update(code_features(code))
    res = run_blender(cfg, script, out_dir, threads)
    rec.update({k: res.get(k) for k in ("status", "error_type", "error_message", "error_line",
                                        "exec_time_s", "render_time_s", "views", "blender_version")})
    sc = res.get("scene")
    if sc:
        rec.update({"faces": sc["faces"], "triangles": sc["triangles"],
                    "n_geometry_objects": sc["n_geometry_objects"],
                    "modifier_types": sc["modifier_types"],
                    "n_materials_created": len(sc["materials"]),
                    "n_materials_assigned": sc["n_materials_assigned"],
                    "startup_objects_left": sc.get("startup_objects_left", []),
                    "startup_geometry_left": any(n == "Cube" for n in sc.get("startup_objects_left", [])),
                    "n_unconnected_nodes": sum(m.get("n_unconnected_nodes", 0) for m in sc["materials"])})
        rec.update(checks_mod.evaluate(p, res))
    return rec


def preflight(cfg, api_key, models, n_tasks_per_model):
    print("Checking models on the gateway ...")
    try:
        available = fetch_gateway_models(cfg["gateway"]["base_url"], api_key)
    except Exception as e:
        sys.exit(f"Could not reach the gateway / list models: {e}\nIs AI_GATEWAY_API_KEY correct?")
    missing = [m["id"] for m in models if m["id"] not in available]
    if missing:
        print("\nThese model IDs are not on the gateway:")
        for mid in missing:
            fam = mid.split("/")[0]
            alts = sorted(k for k in available if k.startswith(fam + "/"))[:25]
            print(f"  - {mid}\n    available from '{fam}': {', '.join(alts) or '(none)'}")
        sys.exit("\nEdit config.yaml -> models and run again.")
    rows, total_typ, total_worst = [], 0.0, 0.0
    for m in models:
        gp = available[m["id"]]
        for k, gk in (("price_in", "in"), ("price_out", "out")):
            if gp[gk] is not None:
                m[k] = max(m[k], gp[gk])  # guard always uses the higher price
        typ = n_tasks_per_model * (900 * m["price_in"] + 3500 * m["price_out"]) / 1e6
        worst = n_tasks_per_model * (1500 * m["price_in"]
                                     + cfg["generation"]["max_output_tokens"] * m["price_out"]) / 1e6
        total_typ += typ
        total_worst += worst
        rows.append((m["label"], m["id"], m["price_in"], m["price_out"], typ, worst))
    print(f"\n{'model':24} {'id':34} {'$/1M in':>8} {'$/1M out':>9} {'typical':>9} {'worst':>9}")
    for r in rows:
        print(f"{r[0]:24} {r[1]:34} {r[2]:8.2f} {r[3]:9.2f} {r[4]:9.2f} {r[5]:9.2f}")
    print(f"{'TOTAL':24} {'':34} {'':8} {'':9} {total_typ:9.2f} {total_worst:9.2f}")
    print(f"Hard budget limit: ${cfg['budget']['hard_limit_usd']:.2f} (run stops before exceeding it)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    ap.add_argument("--out", default="/work/results")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()

    cfg = yaml.safe_load(open(a.config))
    bench = json.load(open(ROOT / "prompts" / "benchmark.json"))
    prompts = bench["prompts"]
    prompts_by_id = {p["id"]: p for p in prompts}

    run_root = Path(a.out) / ("smoke" if a.smoke else "main")
    run_root.mkdir(parents=True, exist_ok=True)
    shutil.copy(a.config, run_root / "config_used.yaml")
    shutil.copy(ROOT / "prompts" / "benchmark.json", run_root / "benchmark_used.json")
    rec_path = run_root / "records.jsonl"

    if not a.report_only:
        if a.smoke:
            models = [{"id": "reference", "label": "Reference (hand-written)", "family": "Human"}]
            ref_ids = sorted(f.stem for f in (ROOT / "prompts" / "reference").glob("*.py"))
            tasks_all = [(models[0], pid, 1) for pid in ref_ids]
            client, budget = None, None
        else:
            api_key = os.environ.get(cfg["gateway"]["api_key_env"], "").strip()
            if not api_key:
                sys.exit(f"Set {cfg['gateway']['api_key_env']} (see README).")
            models = cfg["models"]
            reps = cfg["generation"]["repetitions"]
            preflight(cfg, api_key, models, len(prompts) * reps)
            # rep-major order: a stopped run still has balanced data across models and tiers
            tasks_all = [(m, p["id"], r) for r in range(1, reps + 1) for p in prompts for m in models]

        old = load_records(rec_path)
        done = {(r["model_id"], r["prompt_id"], r["rep"]) for r in old if r["status"] not in RETRY_STATUSES}
        spent = sum(r.get("cost_usd_est") or 0 for r in old)
        tasks = [t for t in tasks_all if (t[0]["id"], t[1], t[2]) not in done]
        if a.limit:
            tasks = tasks[: a.limit]
        print(f"\n{len(tasks_all)} attempts in plan, {len(done)} already done, {len(tasks)} to run now. "
              f"Spent so far: ${spent:.4f}")

        if tasks and not a.smoke:
            budget = Budget(cfg["budget"]["hard_limit_usd"], spent)
            client = GatewayClient(cfg, api_key, budget)
            if not a.yes and input("Start? [y/N] ").strip().lower() != "y":
                sys.exit("Aborted.")

        if tasks:
            workers = 1 if a.smoke else cfg["blender"]["workers"]
            threads = max(1, (os.cpu_count() or 2) // workers)
            stop = threading.Event()
            lock = threading.Lock()
            counts = {"ok": 0, "fail": 0}
            bar = tqdm(total=len(tasks), unit="attempt", dynamic_ncols=True, smoothing=0.05)

            def job(t):
                if stop.is_set():
                    return None
                return attempt(t, cfg, client, prompts_by_id, run_root, threads, a.smoke)

            ex = ThreadPoolExecutor(max_workers=workers)
            futs = [ex.submit(job, t) for t in tasks]
            try:
                for f in as_completed(futs):
                    try:
                        rec = f.result()
                    except BudgetExceeded as e:
                        if not stop.is_set():
                            tqdm.write(f"\nBUDGET GUARD: {e}. Stopping after running attempts finish.")
                        stop.set()
                        rec = None
                    except Exception as e:  # unexpected harness bug: log, keep going
                        tqdm.write(f"internal error: {type(e).__name__}: {e}")
                        rec = None
                    if rec is not None:
                        with lock:
                            with open(rec_path, "a", encoding="utf-8") as fh:
                                fh.write(json.dumps(rec) + "\n")
                        counts["ok" if rec["status"] == "ok" else "fail"] += 1
                    bar.update(1)
                    post = {"ok": counts["ok"], "fail": counts["fail"]}
                    if budget:
                        post["spent"] = f"${budget.spent:.3f}"
                    bar.set_postfix(post)
            except KeyboardInterrupt:
                stop.set()
                tqdm.write("\nInterrupted - finishing running attempts, then writing the report. "
                           "Re-run the same command to resume.")
                for f in futs:
                    f.cancel()
            finally:
                ex.shutdown(wait=True, cancel_futures=True)
                bar.close()
            if client and client.dropped_params:
                (run_root / "dropped_params.json").write_text(json.dumps(client.dropped_params, indent=2))

    from . import metrics, report
    print("\nComputing CLIP metrics ...")
    metrics.compute(run_root, cfg, prompts)
    print("Writing report ...")
    report.build(run_root, cfg, prompts)
    print(f"\nDone. Open {run_root / 'report' / 'report.md'}")


if __name__ == "__main__":
    main()
