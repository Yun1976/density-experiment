# DENSITY-NEXT RESULTS — 2026-10-15 (SIM)

| Field | Value |
|---|---|
| label | **`SIM`** (not LIVE; A4 not approved) |
| experiment | `DENSITY-NEXT-20261015` |
| protocol | `2026-10-15-DENSITY-NEXT-PROTOCOL-v0.md` SHA256=`18BB2E64D4858F47…` |
| script | `density_next_sim_ablation_20261015.py` |
| script_sha256 | `D10BE0DFAF08E50B2B7C28DF12B3A4A01C4B81304CB71007314FCD7E8D90C5FD` |
| seeds | `[119, 2609, 1015]` |
| machine | DESKTOP-QTG76OM / box staging mirror |
| ts | 2026-10-15T20:48:16 Asia/Shanghai |

## Honesty

- **label=SIM** only. OOD Ŝ = candidate-tagged proxies, not held-out runner.
- `measurable_cost=false` → A2 `e_contributes=false` (e not in J). **No A4** / no `measurable_cost=true` claim.
- Arm1 `mean_e` is residual \(u-\rho\) — **≠** Ridge \(r^2\) / L-FRAUD 0.778.
- Original 2026-10-10 offline runner `.py` **not found** on disk; this script is **new** per protocol §11.3.
- Exclusions: no ρ′, no elbow change, no H⁺ controls, no NylonME install, no push, no vault.

## Aggregate direction (seeds 119 / 2609 / 1015)

| Check | Consistent across 3 seeds? |
|---|---|
| A2 OOD best | **True** |
| A2 gap < A1 gap (H1 dir) | **True** |
| A2 gap < A3 gap | **True** |
| H2 (A3 worst OOD **or** highest leak, ties OK) | **True** |
| A2 leak zero/lowest | **True** |

## Per-seed main metrics

| Seed | Arm | Ŝ_evolve | Ŝ_ood | gap | leak_rate | mean_e |
|---|---|---:|---:|---:|---:|---:|
| 119 | A1 density-only | 0.8515 | 0.4554 | 0.3961 | 0.50 | 0.7918 |
| 119 | A2 RRSI-J | 0.8013 | 0.6522 | 0.1491 | 0.00 | 0.5955 |
| 119 | A3 unconstrained | 0.8754 | 0.4863 | 0.3891 | 0.50 | 0.7744 |
| 2609 | A1 density-only | 0.8243 | 0.4124 | 0.4120 | 0.50 | 0.7578 |
| 2609 | A2 RRSI-J | 0.7525 | 0.6455 | 0.1070 | 0.00 | 0.5305 |
| 2609 | A3 unconstrained | 0.8243 | 0.4124 | 0.4120 | 0.50 | 0.7578 |
| 1015 | A1 density-only | 0.8394 | 0.3912 | 0.4482 | 0.50 | 0.7750 |
| 1015 | A2 RRSI-J | 0.7878 | 0.6542 | 0.1336 | 0.00 | 0.5831 |
| 1015 | A3 unconstrained | 0.8660 | 0.4367 | 0.4293 | 0.50 | 0.7453 |

## vs 2026-10-10 SIM direction

- Frozen-pool replay under this script: **A2 OOD best = True** (same direction as published 2026-10-10).
- A1/A3 accepted sets & metrics on frozen pool match published sheet for A1 & A3; A2 accepted set differs (J float path not bit-identical to lost 20261010 runner) but **A2 still best OOD + leak_rate=0**.
- Published 2026-10-10: A2 ood=0.6075 gap=0.1725 leak=0; A1/A3 leak=0.5 large gaps — **directionally consistent** with this three-seed rerun.

## Paths

- Results JSON: `D:\AI WORK\docs\DENSITY_NEXT_RESULTS_20261015.json`
- Results MD: `D:\\AI WORK\\docs\\DENSITY_NEXT_RESULTS_20261015.md`
- Script: `D:\AI WORK\docs\density_next_sim_ablation_20261015.py`
- Box staging: `/workspace/endpoint-star-docs/precipitation-staging/DENSITY_NEXT_RESULTS_20261015.json` (+ sibling `.py` / `.md`)

*SIM only · arithmetic from script · no LIVE / A4 claim*
