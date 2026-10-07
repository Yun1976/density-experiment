# Deep Read: RRSI — Regularized Recursive Self-Improvement (2026-10-07)

Curated note for this week's literature intake. Paper: arXiv:2609.24972
(Google Research). Open source: github.com/google-research/rrsi. Claims
were cross-checked against the repository README and its method-to-code
mapping table.

## The finding that matters most

Harness evolution overfits, in three named modes: benchmark-specific
fitting, noise chasing, and complexity accumulation — extra reflections,
checks, memories, and retries that buy small in-distribution gains while
nobody knows whether real capability improved. In their ablation,
unregularized evolution raised the evolve-set score higher (92.8 vs
90.5) while OOD gains vanished (40.3 vs 43.6) and per-trial tokens
ballooned (3.80M vs 2.42M). Evolve-set score is not capability; OOD
retention is.

## Why this is not a threat but a validation

This experiment was designed (May 2026) on the premise that knowledge
systems inflate: every addition is an information block scored for
surprise, relevance, and causal novelty, then back-verified for actual
later utility, with the residual correcting the estimator. The three
failure modes RRSI meets from the benchmark side are the three
entropies this experiment was built to measure from the knowledge-base
side: relevance decay (stale overfit knowledge), regret/redundancy rates
(noise chasing), and inflated-output detection with a keep/compress/
discard rule (complexity accumulation). Complexity accumulation is
entropy; measuring whether each added bit of complexity actually carries
retrievable information is the point of the density experiment.

RRSI's regularization (annealed single-variable edits, an edit ledger
that keeps falsified hypotheses dead, a leakage critic, a noise floor, a
cost rule, pruning) is convergent evidence from a third group: like
ScholarEvolve and fast-jev-compaction, it measures acceptance-time
scores without tracking whether retained knowledge is actually used
later. That later-utility measurement remains this experiment's
differentiator.

## Follow-ups proposed (pending review)

Upgrade the prediction-verification contract protocol with component and
compliance-cost fields (turning it into an edit ledger); require
promotion counts to span at least two distinct incident contexts; treat
the sealed set as the evolve track and the next real incidents as the
OOD track; add a leakage check and a cost column to change lists.
