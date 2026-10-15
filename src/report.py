"""Aggregates records + CLIP scores into tables, figures, galleries and a paper brief."""
import json
import math
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from scipy.stats import chi2_contingency  # noqa: E402

from .llm_client import SYSTEM_PROMPT  # noqa: E402

EXEC_FAIL = {"no_code", "truncated", "exec_error", "timeout_exec", "crash_exec"}
DRIFT_MARKERS = [
    "use_auto_smooth", "auto_smooth_angle",                 # removed in 4.1
    '"diameter1"', '"diameter2"',                            # bmesh create_cone -> radius1/2 (4.0)
    'key "specular" not found', 'key "clearcoat" not found',  # Principled BSDF renames (4.0)
    'key "clearcoat roughness" not found', 'key "sheen" not found',
    'key "subsurface" not found', 'key "transmission" not found',
    'key "emission" not found', 'key "subsurface color" not found',
    "blender_eevee'", "'blender_eevee'",                    # engine id renamed in 4.2
    "use_ssr", "use_bloom", "use_gtao",                      # EEVEE Legacy settings removed in 4.2
    "shadow_soft_size'",
]
TIER_SHORT = {1: "T1 Low-poly", 2: "T2 Procedural", 3: "T3 Materials"}


def classify(r):
    s = r.get("status")
    if s == "ok":
        return None
    if s == "no_code":
        return "No code returned"
    if s == "truncated":
        return "Output truncated (token limit)"
    if s and s.startswith("timeout"):
        return "Timeout (" + s.split("_")[1] + ")"
    if s and s.startswith("crash"):
        return "Blender crash"
    if s == "empty_scene":
        return "Ran, but empty scene"
    if s in ("render_error", "analysis_error"):
        return "Render/analysis error"
    et, msg = r.get("error_type") or "", (r.get("error_message") or "")
    low = msg.lower()
    # Names that existed in older Blender releases but were removed/renamed by 4.x
    # (training-data staleness rather than pure invention)
    if any(k in low for k in DRIFT_MARKERS):
        return "Outdated API (pre-4.x)"
    if et in ("SyntaxError", "IndentationError", "TabError"):
        return "Syntax error"
    if "poll()" in low or "context is incorrect" in low or "context missing" in low:
        return "Operator context error"
    if "converting py args to operator properties" in low:
        return "Wrong argument or type"
    if "enum" in low and "not found in" in low:
        return "Invalid enum value"
    if "not found" in low and ("bpy_prop_collection" in low or "key" in low):
        return "Invalid node/socket name"
    if et == "AttributeError":
        return "Nonexistent API attribute"
    if et == "TypeError":
        return "Wrong argument or type"
    if et in ("NameError", "ImportError", "ModuleNotFoundError"):
        return "Name/import error"
    if et in ("KeyError", "IndexError"):
        return "Key/index error"
    if et == "ValueError":
        return "Value error"
    return "Other runtime error"


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0, c - h), min(1, c + h))


def load(run_root):
    recs = [json.loads(l) for l in (run_root / "records.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(recs)
    df = df[df["status"] != "api_error"].copy()
    cp = run_root / "clip_scores.jsonl"
    if cp.exists():
        clip = pd.DataFrame([json.loads(l) for l in cp.read_text(encoding="utf-8").splitlines() if l.strip()])
        clip = clip.drop_duplicates("dir", keep="last")
        df = df.merge(clip, on="dir", how="left")
    for c in ("clip_score", "clip_cos", "clip_rank_tier", "clip_rank_all", "blank_render",
              "all_checks_pass", "poly_budget_ok", "material_checks_ok", "faces", "cost_usd_est",
              "completion_tokens", "reasoning_tokens", "latency_s", "code_lines", "n_bpy_ops_calls",
              "n_unconnected_nodes", "error_line"):
        if c not in df:
            df[c] = np.nan
    df["exec_fail"] = df["status"].isin(EXEC_FAIL)
    df["rendered"] = (df["status"] == "ok") & (df["blank_render"] != True)  # noqa: E712
    df["task_success"] = df["rendered"] & (df["all_checks_pass"] == True)  # noqa: E712
    df["clip_top1_tier"] = np.where(df["rendered"], df["clip_rank_tier"] == 1, np.nan)
    df["failure_category"] = df.apply(classify, axis=1)
    df["tier_label"] = df["tier"].map(TIER_SHORT)
    return df


def summarize(g):
    n = len(g)
    ef = wilson(int(g["exec_fail"].sum()), n)
    ts = wilson(int(g["task_success"].sum()), n)
    executed = g[g["status"].isin(["ok", "empty_scene", "render_error", "timeout_render", "crash_render"])]
    pb = g["poly_budget_ok"].dropna()
    mc = g["material_checks_ok"].dropna()
    rend = g[g["rendered"]]
    return pd.Series({
        "n": n,
        "exec_failure_rate": ef[0], "exec_failure_ci_lo": ef[1], "exec_failure_ci_hi": ef[2],
        "empty_scene_rate": (g["status"] == "empty_scene").mean(),
        "truncated_rate": (g["status"] == "truncated").mean(),
        "default_cube_left_rate": g["startup_geometry_left"].dropna().astype(float).mean()
        if "startup_geometry_left" in g and g["startup_geometry_left"].notna().any() else np.nan,
        "rendered_rate": g["rendered"].mean(),
        "task_success_rate": ts[0], "task_success_ci_lo": ts[1], "task_success_ci_hi": ts[2],
        "check_pass_fraction_mean": g["check_pass_fraction"].mean() if "check_pass_fraction" in g else np.nan,
        "poly_budget_adherence": pb.astype(float).mean() if len(pb) else np.nan,
        "material_checks_rate": mc.astype(float).mean() if len(mc) else np.nan,
        "clip_score_mean": rend["clip_score"].mean(),
        "clip_score_sd": rend["clip_score"].std(),
        "clip_top1_in_tier": rend["clip_top1_tier"].astype(float).mean() if len(rend) else np.nan,
        "n_executed": len(executed),
        "mean_completion_tokens": g["completion_tokens"].mean(),
        "mean_reasoning_tokens": g["reasoning_tokens"].mean(),
        "mean_latency_s": g["latency_s"].mean(),
        "mean_code_lines": g["code_lines"].mean(),
        "cost_usd": g["cost_usd_est"].sum(),
    })


def fmt_pct(x):
    return "–" if pd.isna(x) else f"{100 * x:.1f}%"


def fmt_num(x, d=1):
    return "–" if pd.isna(x) else f"{x:.{d}f}"


# ------------------------------------------------------------------ figures
def grouped_bar(tab, value, lo, hi, title, ylabel, path, models, tiers):
    fig, ax = plt.subplots(figsize=(7.5, 4))
    w = 0.8 / max(1, len(models))
    x = np.arange(len(tiers))
    for i, m in enumerate(models):
        sub = tab[tab["model_label"] == m].set_index("tier").reindex(tiers)
        y = sub[value].values
        err = None
        if lo:
            err = np.vstack([y - sub[lo].values, sub[hi].values - y])
        ax.bar(x + (i - (len(models) - 1) / 2) * w, y, w, label=m, yerr=err, capsize=3)
    ax.set_xticks(x, [TIER_SHORT[t] for t in tiers])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if value.endswith("rate"):
        ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figures(df, by_mt, fig_dir, models, tiers):
    grouped_bar(by_mt, "exec_failure_rate", "exec_failure_ci_lo", "exec_failure_ci_hi",
                "Execution failure rate by tier (95% Wilson CI)", "failure rate",
                fig_dir / "fig1_exec_failure_by_tier.png", models, tiers)
    grouped_bar(by_mt, "task_success_rate", "task_success_ci_lo", "task_success_ci_hi",
                "Task success (executed, rendered, all checks pass)", "success rate",
                fig_dir / "fig2_task_success_by_tier.png", models, tiers)

    fig, ax = plt.subplots(figsize=(7.5, 4))
    data, pos, labels, k = [], [], [], 0
    for t in tiers:
        for m in models:
            v = df[(df["tier"] == t) & (df["model_label"] == m) & df["rendered"]]["clip_score"].dropna()
            data.append(v.values if len(v) else [np.nan])
            pos.append(k)
            k += 1
        k += 1
    bp = ax.boxplot(data, positions=pos, widths=0.7, patch_artist=True, showfliers=False)
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, b in enumerate(bp["boxes"]):
        b.set_facecolor(colors[i % len(models)])
        b.set_alpha(0.7)
    centers = [np.mean(pos[i * len(models):(i + 1) * len(models)]) for i in range(len(tiers))]
    ax.set_xticks(centers, [TIER_SHORT[t] for t in tiers])
    ax.set_ylabel("CLIPScore (rendered attempts)")
    ax.set_title("Image-text alignment by tier")
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(len(models))], models,
              fontsize=8, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig3_clipscore_by_tier.png", dpi=200)
    plt.close(fig)

    fails = df[df["failure_category"].notna()]
    if len(fails):
        ct = pd.crosstab(fails["tier_label"], fails["failure_category"])
        ct = ct[ct.sum().sort_values(ascending=False).index]
        ax = ct.plot(kind="barh", stacked=True, figsize=(8, 3.8), colormap="tab20")
        ax.set_xlabel("number of failed attempts")
        ax.set_ylabel("")
        ax.set_title("Failure taxonomy by tier")
        ax.legend(fontsize=7, frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(fig_dir / "fig4_failure_taxonomy.png", dpi=200)
        plt.close()

    by_m = df.groupby("model_label").agg(cost=("cost_usd_est", "sum"),
                                         tokens=("completion_tokens", "mean")).reindex(models)
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    axs[0].bar(range(len(models)), by_m["cost"], color=colors[:len(models)])
    axs[0].set_title("Total cost (USD, estimated)")
    axs[1].bar(range(len(models)), by_m["tokens"], color=colors[:len(models)])
    axs[1].set_title("Mean output tokens / attempt")
    for a in axs:
        a.set_xticks(range(len(models)), models, rotation=20, ha="right", fontsize=8)
        a.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig5_cost_tokens.png", dpi=200)
    plt.close(fig)


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def galleries(df, run_root, gal_dir, prompts, models, cell=256):
    f_head, f_cell = font(18), font(15)
    for tier in sorted({p["tier"] for p in prompts}):
        tp = [p for p in prompts if p["tier"] == tier]
        left, top = 210, 40
        W, H = left + cell * len(models), top + cell * len(tp)
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        for j, m in enumerate(models):
            d.text((left + j * cell + 6, 10), m, fill="black", font=f_head)
        for i, p in enumerate(tp):
            d.text((6, top + i * cell + cell // 2 - 10), f"{p['id']} {p['title']}", fill="black", font=f_cell)
            for j, m in enumerate(models):
                sub = df[(df["prompt_id"] == p["id"]) & (df["model_label"] == m)].sort_values("rep")
                x0, y0 = left + j * cell, top + i * cell
                ok = sub[sub["rendered"]]
                if len(ok):
                    r = ok.iloc[0]
                    tile = Image.open(run_root / r["dir"] / "view_0.png").convert("RGB").resize((cell - 4, cell - 4))
                    img.paste(tile, (x0 + 2, y0 + 2))
                    d.text((x0 + 8, y0 + cell - 24), f"rep{r['rep']}  {len(ok)}/{len(sub)} ok",
                           fill="black", font=f_cell)
                else:
                    d.rectangle([x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2], fill=(235, 225, 225))
                    cats = sub["failure_category"].dropna().value_counts()
                    txt = "no attempts" if not len(sub) else "\n".join(
                        f"{c} x{n}" for c, n in cats.head(3).items())
                    d.multiline_text((x0 + 10, y0 + 10), txt, fill=(150, 0, 0), font=f_cell)
                d.rectangle([x0, y0, x0 + cell, y0 + cell], outline=(200, 200, 200))
        img.save(gal_dir / f"gallery_tier{tier}.png")


def md_table(df_, cols, headers):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for _, r in df_.iterrows():
        lines.append("| " + " | ".join(str(f(r[c])) if f else str(r[c]) for c, f in cols) + " |")
    return "\n".join(lines)


def build(run_root, cfg, prompts):
    run_root = Path(run_root)
    if not (run_root / "records.jsonl").exists():
        print("No records yet.")
        return
    out = run_root / "report"
    fig_dir, gal_dir = out / "figures", out / "galleries"
    for p in (fig_dir, gal_dir):
        p.mkdir(parents=True, exist_ok=True)
    df = load(run_root)
    if df.empty:
        print("No completed attempts yet.")
        return
    df.to_csv(out / "attempts.csv", index=False)

    models = list(dict.fromkeys(df["model_label"]))
    tiers = sorted(df["tier"].unique())
    by_mt = df.groupby(["model_label", "tier"]).apply(summarize, include_groups=False).reset_index()
    by_t = df.groupby("tier").apply(summarize, include_groups=False).reset_index()
    by_m = df.groupby("model_label").apply(summarize, include_groups=False).reindex(models).reset_index()
    by_p = df.groupby(["tier", "prompt_id"]).apply(summarize, include_groups=False).reset_index()
    for name, t in (("by_model_tier", by_mt), ("by_tier", by_t), ("by_model", by_m), ("by_prompt", by_p)):
        t.to_csv(out / f"summary_{name}.csv", index=False)

    figures(df, by_mt, fig_dir, models, tiers)
    galleries(df, run_root, gal_dir, prompts, models)

    # ---- significance: does execution failure depend on tier?
    tests = []
    def chi(sub, label):
        ct = pd.crosstab(sub["tier"], sub["exec_fail"])
        if ct.shape == (len(tiers), 2) and len(tiers) > 1:
            chi2, p, dof, _ = chi2_contingency(ct)
            v = math.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
            tests.append(f"- {label}: χ²({dof}) = {chi2:.2f}, p = {p:.4g}, Cramér's V = {v:.2f}")
        else:
            tests.append(f"- {label}: not testable (a tier has no failures or no successes)")
    chi(df, "All models pooled")
    for m in models:
        chi(df[df["model_label"] == m], m)

    fails = df[df["failure_category"].notna()]
    tax = pd.crosstab(fails["failure_category"], fails["tier_label"], margins=True, margins_name="Total") \
        if len(fails) else pd.DataFrame()
    examples = []
    for cat, g in fails.groupby("failure_category"):
        for _, r in g.head(2).iterrows():
            msg = (r.get("error_message") or "").replace("\n", " ")[:220]
            examples.append(f"- **{cat}** ({r['model_label']}, {r['prompt_id']}): `{msg}`")

    std_cols = [("model_label", None), ("tier", lambda t: TIER_SHORT[t]), ("n", lambda x: int(x)),
                ("exec_failure_rate", fmt_pct), ("truncated_rate", fmt_pct), ("empty_scene_rate", fmt_pct),
                ("poly_budget_adherence", fmt_pct), ("material_checks_rate", fmt_pct),
                ("task_success_rate", fmt_pct), ("clip_score_mean", fmt_num),
                ("clip_top1_in_tier", fmt_pct)]
    std_head = ["Model", "Tier", "n", "Exec. fail", "of which truncated", "Empty scene", "Poly budget OK",
                "Material checks OK", "Task success", "CLIPScore", "CLIP top-1 (tier)"]

    dropped = run_root / "dropped_params.json"
    gen = cfg["generation"]
    blender_ver = df["blender_version"].dropna().iloc[0] if df["blender_version"].notna().any() else "n/a"
    dates = pd.to_datetime(df["timestamp"])
    total_cost = df["cost_usd_est"].sum()

    md = [f"# Report: {cfg['experiment_name']}", "",
          f"Attempts analysed: **{len(df)}** · Models: **{len(models)}** · Prompts: **{df['prompt_id'].nunique()}** · "
          f"Estimated API cost: **${total_cost:.3f}**", "",
          "## Results by model and tier", md_table(by_mt, std_cols, std_head), "",
          "## Results by tier (all models pooled)",
          md_table(by_t.assign(model_label="all"), std_cols, std_head), "",
          "## Results by model (all tiers)",
          md_table(by_m, [c for c in std_cols if c[0] != "tier"],
                   [h for h in std_head if h != "Tier"]), "",
          "## Does execution failure depend on tier? (χ² test of independence)", *tests, "",
          "## Failure taxonomy (counts)", tax.to_markdown() if len(tax) else "No failures.", "",
          "## Example error messages", *(examples or ["None."]), "",
          "## Figures",
          *[f"![{p.stem}](figures/{p.name})" for p in sorted(fig_dir.glob("*.png"))], "",
          "## Galleries (first successful repetition, view 0)",
          *[f"![{p.stem}](galleries/{p.name})" for p in sorted(gal_dir.glob("*.png"))], ""]
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")

    brief = [
        "# Paper brief (feed this file + figures/galleries to the writing assistant)", "",
        "## Setup (auto-collected)",
        f"- Run window: {dates.min():%Y-%m-%d %H:%M} – {dates.max():%Y-%m-%d %H:%M}",
        f"- Blender version (headless, containerised): {blender_ver}; host: {platform.platform()}",
        f"- Render: {cfg['blender']['render']['engine']}, {cfg['blender']['render']['samples']} samples, "
        f"{cfg['blender']['render']['resolution']} px, views (azimuth, elevation) = {cfg['blender']['render']['views']}; "
        "LLM-created cameras/lights removed and replaced with an identical camera auto-framed to the "
        "evaluated bounding box, two sun lights and a grey world.",
        f"- Script timeout: {cfg['blender']['timeout_s']} s per attempt (execution + rendering).",
        f"- Generation: single pass, {gen['repetitions']} independent samples per model-prompt pair, "
        f"temperature {gen['temperature']} (where accepted), max output tokens {gen['max_output_tokens']}.",
        "- Models (via Vercel AI Gateway, OpenAI-compatible Chat Completions):",
        *[f"  - {m['label']} (`{m['id']}`), extra params {m.get('extra_params') or {}}, "
          f"temperature sent: {m.get('send_temperature', True)}" for m in cfg["models"]],
        f"- Parameters removed automatically after provider rejection: "
        f"{dropped.read_text() if dropped.exists() else 'none'}",
        "- Benchmark: 30 prompts, 10 per tier "
        "(T1 low-poly primitives and modifiers; T2 medium-poly procedural geometry; T3 shader-node materials), "
        "each with explicit structural checks (face-count budget, required modifiers, required connected "
        "shader nodes, Principled BSDF input values, material assignment).",
        "- Metrics: execution failure = no code, reply truncated at the output-token limit (not executed), Python exception, script timeout or crash before the script "
        "finished; poly-budget adherence = evaluated face count (modifiers and instances included) inside the "
        "prompt's range; material checks evaluate only nodes reachable from the active Material Output of "
        "materials assigned to visible objects; CLIPScore = 100·2.5·max(cos,0) with "
        f"{cfg['metrics']['clip_model']}/{cfg['metrics']['clip_pretrained']}, averaged over views; CLIP top-1 = "
        "the prompt's own caption is the best match among the 10 captions of its tier; task success = "
        "executed + non-blank render + all checks pass. Scripts start from Blender's default "
        "startup scene (cube, camera, light), as a user would run them; default cube left = the "
        "script did not remove the startup cube despite the instruction (it is then counted in "
        "faces and renders).",
        "", "## System prompt", "```", SYSTEM_PROMPT.format(version=gen["blender_version_in_prompt"]), "```", "",
        "## Headline numbers by model and tier", md_table(by_mt, std_cols, std_head), "",
        "## Pooled by tier", md_table(by_t.assign(model_label="all"), std_cols, std_head), "",
        "## Statistical tests", *tests, "",
        "## Failure taxonomy", tax.to_markdown() if len(tax) else "No failures.", "",
        "## Example errors", *(examples or ["None."]), "",
        "## Per-model efficiency",
        md_table(by_m, [("model_label", None), ("default_cube_left_rate", fmt_pct),
                        ("mean_completion_tokens", lambda x: fmt_num(x, 0)),
                        ("mean_reasoning_tokens", lambda x: fmt_num(x, 0)),
                        ("mean_latency_s", fmt_num), ("mean_code_lines", lambda x: fmt_num(x, 0)),
                        ("cost_usd", lambda x: f"${x:.3f}")],
                 ["Model", "Default cube left", "Output tokens", "Reasoning tokens", "Latency (s)", "Code lines", "Cost"]), "",
        "## Hardest prompts (lowest task success, pooled)",
        md_table(by_p.sort_values("task_success_rate").head(8),
                 [("prompt_id", None), ("tier", None), ("exec_failure_rate", fmt_pct),
                  ("task_success_rate", fmt_pct), ("clip_score_mean", fmt_num)],
                 ["Prompt", "Tier", "Exec. fail", "Task success", "CLIPScore"]), "",
        "## Files", "- figures/: " + ", ".join(p.name for p in sorted(fig_dir.glob("*.png"))),
        "- galleries/: " + ", ".join(p.name for p in sorted(gal_dir.glob("*.png"))),
        "- attempts.csv (one row per attempt), summary_*.csv",
    ]
    (out / "paper_brief.md").write_text("\n".join(brief), encoding="utf-8")
