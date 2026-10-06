# Deep Read: ScholarEvolve — Learning from Research (2026-10-06)

Curated note accompanying this week's automated status update. Source
paper studied via full-text translation; all numbers below were
cross-checked against the tables in the translated full text.

## What the paper does

ScholarEvolve evolves the agent harness (not the model weights) by mining
research literature: failure audits produce capability gaps; literature is
organized into semantically orthogonal mechanism topics; each selected
paper becomes a single-module mutation with a blueprint; cheap health
probes filter broken candidates; crossovers are ranked by additive
predicted gain but decided by **joint evaluation of the full shell**; a new
champion is kept only when the paired-bootstrap lower confidence bound is
positive. New papers arriving across publication windows drive lifelong
evolution.

## Four results that matter for this experiment

1. **Harness design closes capability gaps.** Qwen3.5-27B on AppWorld
   Challenge TGC 49.6% -> 63.6%; Normal 69.0% -> 81.4%; the gap to a much
   larger frontier model shrinks by ~74% with weights fixed.
2. **Monomer scores do not predict combination performance (Table 3).**
   Swapping a 75.4% single-module candidate for a 73.7% one *raised* the
   combination from 80.7% to 84.8%. Combinations must be measured jointly.
3. **Candidate pools are brutal (Table 7).** Same pool, same budget:
   gains from +13.5 to -67.8 points (one memory mechanism scored 0 wins /
   50 losses and was gated out; the same mechanism was later selected for
   a different backbone+benchmark). Health probes and validation gates are
   load-bearing, not bureaucracy.
4. **Research-driven beats experience-driven over time (Table 5).**
   Across three publication windows: 69.00 -> 73.41 -> 79.76 -> 81.55 TGC,
   while a feedback-only baseline wandered 69.00 -> 69.64.

## Portable insights for the density experiment

- **External literature intake is an organ, not a luxury.** An internal
  feedback loop alone plateaus; that is the core motivation for this
  weekly update channel.
- **Topic-orthogonal selection operationalizes second-order density.**
  Our information-density framing distinguishes first-order density (how
  much one document carries) from second-order direction coverage (whether
  a corpus covers many mechanisms or rephrases one). The paper's topic
  orthogonality + round-robin selection is a concrete precedent for
  measuring and enforcing direction coverage.
- **Gates before glory.** Cheap probes (importability, interface
  compatibility, sane outputs) before expensive evaluation; deployment
  decisions by paired-bootstrap lower bounds rather than mean deltas.
- **Mechanisms do not transfer blindly across hosts.** A rule validated on
  one backbone/agent can be harmful on another; portability needs its own
  validation, which is exactly why our residual back-verification exists.
