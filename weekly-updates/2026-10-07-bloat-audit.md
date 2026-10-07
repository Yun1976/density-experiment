# Empirical Report: Measuring Engineering Bloat by Information Density (2026-10-07)

First retrospective utility back-verification of the rule ledger that feeds
this experiment's promotion chain (lessons -> skills -> stamps).

## Method

Every ledger rule is treated as an information block: accepting it carries
an implicit value estimate, and its later hit count proxies observed
utility u. The core test is age-controlled: among rules given a fair
exposure window (>= 14 days), what share never proved out again
(single hit)? Bloat follows the RRSI definition — complexity that keeps
accumulating without proportional utility. Honest limits: hits are a
lower bound on utility for insurance-type (rare-catastrophe guard) rules;
the design is retrospective, uncontrolled, mature-group n=34.

## Findings (all measured, script re-runnable)

1. **Bloat is accelerating and recent.** Of 94 dated rules, 52 (55%)
   were added in the last 7 days; the ledger tripled in 10 days
   (31 -> 94 since the 09-27 baseline snapshot).
2. **Two thirds of mature rules never proved out.** Among 34 rules with
   >= 14 days exposure, 23 (67.6%) remain single-hit, at a median age of
   25 days. Age-adjusted utility: 1.2 hits/30d (single-hit mature) vs
   2.3 hits/30d (multi-hit) — a ~2x gap.
3. **Heavy single-hit skew.** 77% single-hit, 18% double, 5% triple-plus.
4. **Consistent with the experiment's core finding.** The residual
   series (947 blocks, mean residual -0.192, 88.5% overestimated at
   acceptance) showed that acceptance-time value estimates run
   systematically high. This audit shows the downstream consequence:
   two thirds of mature retained rules stopped at u = 1. Systematic
   acceptance-side overestimate + an unbounded pre-promotion pool is
   the complete mechanism of engineering bloat.
5. **The promotion gate works; the bloat moved.** Only 5 rules ever
   crossed the >= 3 hit promotion threshold, keeping the constitution
   layer within its cap — but the pre-promotion pool itself is
   unbounded. Bloat did not disappear; it relocated to the intake pool.

## External corroboration

RRSI (arXiv:2609.24972) demonstrates complexity accumulation
experimentally: unregularized evolution raised the evolve-set score to
92.8 while OOD gains vanished (40.3) and tokens doubled. MetaRSI's fifth
law (gains require external entropy input) explains the timing: the
recent 52-rule burst was fed by real incidents, but most of that entropy
has since been absorbed — retention beyond absorption is pure
complexity. An internal modeling corroboration: on the same 280 samples,
expanding features 24 -> 104 with TF-IDF *reduced* out-of-sample r-squared
from 0.589 to 0.524.

## Anti-bloat mechanisms this data supports

Promotion counts spanning >= 2 distinct incident contexts; a 30-day
back-verification review that archives (not deletes) single-hit
non-insurance rules; an active-pool cap mirroring the constitution's
20-stamp cap; and upgrading the prediction-verification contract
protocol with component and cost fields so every new rule carries a
falsifiable expectation that is automatically reconciled at 30 days.

## Limitations

Insurance-type rules are undervalued by hit counts and need explicit
exemption tagging; n=34 limits statistical power (trend, not proof);
no control group; the 30-day review effect itself needs prospective
validation — which is the next step.
