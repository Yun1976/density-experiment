# Signal Verification: Decision-Layer Ecosystem and the Harness Paper (2026-10-06)

Curated note accompanying this week's updates. Three social-media signals
were fact-checked against primary sources (GitHub API, arXiv, project
READMEs) before being absorbed.

## Verified

- **Jev (TypeSafe "System One") is real**: a non-generative decision layer
  exposing three typed primitives (boolean, choice, score) with calibrated
  confidence. The surrounding open-source ecosystem is substantial and
  recent: fast-jev-compaction (7.4k stars, Claude Code context pruning via
  per-tool-call keep/keep-truncated/drop decisions), hermes-jev-skills
  (1.0k stars, model routing / memory / compaction / skill selection),
  jev-browser-use (924 stars), SemIf-OpenJev (4.7k stars, open local
  alternative on a consumer GPU), foreman (675 stars, agent supervision).
  Caveat: "millisecond" latency claims are marketing; the vendor's own
  example cites ~0.11 s per call.
- **The "11 agents, 7 elements" paper is real**: arXiv:2609.00006,
  *Harness Engineering: Anatomy, Architecture, and Evolution of Coding
  Agents — A Source-Code Study of Eleven Systems*. Eleven production
  harnesses (Claude Code, Codex CLI, Gemini CLI, Mistral Vibe, OpenHands,
  Aider, Mini-SWE-Agent, Hermes, Pi, OpenCode, OpenClaw), seven canonical
  subsystems, 29 recurring design patterns, 18 design recommendations,
  ~4M lines analyzed.

## Why this matters for this experiment

1. **fast-jev-compaction validates the direction.** Its keepThreshold
   rule (keep verbatim / keep call + truncate result / drop both) is
   structurally identical to this experiment's keep / compress / discard
   trichotomy, executed by a fast decision model instead of a generative
   LLM. Its "never rewrite, only delete" stance matches our experience
   that summarization is lossy. What it lacks is exactly what this
   experiment contributes: residual back-verification (observed utility
   vs estimated density) and adaptive thresholds driven by regret and
   redundancy.
2. **The paper's two great absences are informative.** Across ~4M lines,
   no runtime imports a general-purpose agent framework and none uses
   vector-embedding code retrieval; the field runs deterministic
   retrieval. This experiment's knowledge access likewise favors
   deterministic full-text search.
3. **A triangle for the related-work section.** Harness anatomy
   (arXiv:2609.00006) + harness evolution (ScholarEvolve, see this week's
   deep read) + decision-layer executors (fast-jev-compaction) frame the
   density experiment's position: a governed, self-evolving harness whose
   pruning decisions are calibrated by residuals rather than fixed
   thresholds.
