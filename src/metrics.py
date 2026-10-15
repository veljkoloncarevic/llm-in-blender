"""
Image metrics for every successfully rendered attempt.

- CLIPScore (Hessel et al., 2021): 100 * 2.5 * max(cos(image, caption), 0), averaged over views.
- CLIP retrieval: the render is compared with all 30 benchmark captions; we store the rank
  of the correct caption (rank 1 = best match). Less sensitive to CLIP's absolute-score bias.
- Blank-render flag: pixel standard deviation below a threshold (nothing visible).
Results are cached in clip_scores.jsonl, so reruns only score new renders.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image


def compute(run_root, cfg, prompts):
    run_root = Path(run_root)
    rec_path = run_root / "records.jsonl"
    cache_path = run_root / "clip_scores.jsonl"
    if not rec_path.exists():
        return
    recs = [json.loads(l) for l in rec_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    cache = {}
    if cache_path.exists():
        for l in cache_path.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                cache[d["dir"]] = d
    todo = [r for r in recs if r.get("status") == "ok" and r["dir"] not in cache]
    if not todo:
        return

    import torch
    import open_clip
    from tqdm import tqdm

    m = cfg["metrics"]
    model, _, preprocess = open_clip.create_model_and_transforms(m["clip_model"], pretrained=m["clip_pretrained"])
    tok = open_clip.get_tokenizer(m["clip_model"])
    model.eval()
    ids = [p["id"] for p in prompts]
    with torch.no_grad():
        tf = model.encode_text(tok([p["caption"] for p in prompts]))
        tf = tf / tf.norm(dim=-1, keepdim=True)

    with open(cache_path, "a", encoding="utf-8") as out:
        for r in tqdm(todo, unit="render", desc="CLIP"):
            d = run_root / r["dir"]
            imgs, stds = [], []
            for v in r.get("views") or []:
                im = Image.open(d / v).convert("RGB")
                stds.append(float(np.asarray(im, dtype=np.float32).std()))
                imgs.append(preprocess(im))
            if not imgs:
                continue
            with torch.no_grad():
                f = model.encode_image(torch.stack(imgs))
                f = f / f.norm(dim=-1, keepdim=True)
                sims = (f @ tf.T).numpy()          # views x captions
            mean_sims = sims.mean(axis=0)
            j = ids.index(r["prompt_id"])
            own = sims[:, j]
            rank = int((mean_sims > mean_sims[j]).sum()) + 1
            tier_idx = [i for i, p in enumerate(prompts) if p["tier"] == r["tier"]]
            tier_rank = int(sum(mean_sims[i] > mean_sims[j] for i in tier_idx)) + 1
            row = {
                "dir": r["dir"],
                "clip_cos": float(own.mean()),
                "clip_score": float(100 * 2.5 * np.clip(own, 0, None).mean()),
                "clip_rank_all": rank,
                "clip_rank_tier": tier_rank,
                "pixel_std_min": min(stds),
                "blank_render": min(stds) < m["blank_render_std_threshold"],
            }
            out.write(json.dumps(row) + "\n")
            out.flush()
