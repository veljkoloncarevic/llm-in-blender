# Blender LLM complexity-tier benchmark

Single-pass bpy script generation → headless Blender execution → fixed-camera renders →
metrics → report. Everything runs in Docker; results land in `./results` on your PC.

## Requirements
- Docker Desktop (Windows: WSL2 backend). ~6 GB disk for the image.
- A Vercel AI Gateway API key **with a budget set on the key** (Dashboard → AI Gateway → API Keys).

## Run (Windows PowerShell, from this folder)
```powershell
.\run.ps1 -Smoke        # 1) FREE: builds the image, renders 3 hand-written reference scenes
.\run.ps1 -Limit 8      # 2) ~1 cent pilot: 8 real attempts, check results\main\report\
.\run.ps1               # 3) full run: 4 models x 30 prompts x 3 reps = 360 attempts
```
The script asks for the key (hidden input), shows prices and an estimated cost, and asks
`Start? [y/N]`. A progress bar shows attempts done, ok/fail counts and money spent.

- **Resume:** Ctrl+C at any time, run the same command again; finished attempts are skipped.
- **Budget:** `config.yaml -> budget.hard_limit_usd` (default $4.50). Before every call the worst
  case (max output tokens at the highest routed price) is reserved, so the limit cannot be crossed.
- **Rebuild report only:** `.\run.ps1 -ReportOnly -NoBuild`
- Linux/macOS: `./run.sh --smoke`, `./run.sh --limit 8`, `./run.sh`

## Output (`results\main\`)
| Path | Content |
|---|---|
| `report\paper_brief.md` | **Give this to Copilot** with the figures/galleries for Methodology/Results |
| `report\report.md` | Human-readable report with all tables and images |
| `report\figures\*.png` | Failure rate, task success, CLIPScore, failure taxonomy, cost |
| `report\galleries\gallery_tier{1,2,3}.png` | Prompt x model grid of renders / failure reasons |
| `report\attempts.csv`, `summary_*.csv` | Raw and aggregated numbers |
| `runs\<model>\<prompt>\rep<k>\` | `script.py`, `response.json`, `blender_log.txt`, `result.json`, `view_*.png` |

## What is measured
| Metric | Definition |
|---|---|
| Execution failure | No code block, Python exception, timeout or crash before the script finished |
| Empty scene | Script ran but produced no geometry |
| Poly-budget adherence | Evaluated face count (modifiers + geometry-node instances) within the prompt's range |
| Material checks | Required shader nodes **reachable from the active Material Output** of materials **assigned** to visible objects; Principled input values (4.x and 3.x socket names) |
| Task success | Executed + non-blank render + all prompt checks pass |
| CLIPScore | 100·2.5·max(cos, 0), ViT-B/32, averaged over 3 views |
| CLIP top-1 | The prompt's own caption is the best match among the 10 captions of its tier |

## Customising
- Models / prices / params: `config.yaml -> models`. If a model ID is wrong, the preflight lists the
  IDs that exist on the gateway for that provider and stops before spending anything.
- Prompts and checks: `prompts/benchmark.json`.
- Faster renders: `blender.render.engine: BLENDER_WORKBENCH` (no material appearance), or fewer `samples`.
