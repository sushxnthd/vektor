# V309 single-cap branch-and-bound falsification protocol (2026-10-30)

**Frozen before the hosted corpus run.** This is a source-conditional computational-identifiability test, not GPU memory traffic, hardware architecture, or measured performance. The March 2020 NVBit tracer-source identity is unverified. All Rodinia families are exploratory and cannot serve as unseen holdouts.

## Motivation and intervention

The independently hosted antichain DP produced 1,586,186–1,595,385 sectors for 240,465 global-proxy rows, but one format-0 BFS instruction returned UNKNOWN at its 3,000-state cap. Do not change the original antichain solver, its 100,000-transition row cap, its 2,000,000-transition global cap, or the previous evidence.

Test a genuinely different exact solver: branch over hidden-lane placements, using a feasible completion as incumbent and admissible lower/upper cardinality bounds to prune. Track rank-sequence state (not antichains). Freeze **1,000,000 visited nodes per capped row**, and return UNKNOWN on cap or address overflow. A completed search returns sharp extrema under the same historical producer hypothesis.

## Predicted regimes

- **Potential win:** the antichain state count is large but the optimal sector cardinality is quickly certified by an incumbent and suffix-union bounds. The one known capped BFS row may become exact without increasing the original DP budget.
- **Predicted no win:** high-entropy token footprints with many nearly incomparable unions and weak suffix bounds. The alternative must return UNKNOWN at the fixed cap, not a guessed bound.
- **No physical speedup prediction:** even if the interval tightens, the pure fixed-address coalescer is already optimal in the earlier ideal-sector baseline. No hardware promotion follows.

## Frozen acceptance and kill criteria

1. Independently verify 15,000+ exhaustive small-mask cases, including nonpoint intervals, and 32-lane random tractable cases against direct original-mask enumeration. Explicitly reject overflow and capped cases.
2. Replay the exact SHA-256-pinned 21,011,152-byte archive (SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`) through the **unchanged** previous full-corpus audit. Require 210 traces, 240,465 global-proxy rows and the exact prior interval **1,586,186–1,595,385**.
3. Intercept only the prior UNKNOWN case; require the original capped-row token digest to match the frozen full-corpus audit's fingerprint. Require exactly one such case.
4. If exact, require new extrema contained in the original conservative interval and recompute the aggregate interval. If capped, preserve previous bounds and record the negative result. No threshold tuning after seeing the outcome.
5. Do not claim physical bank mapping, cache transactions, bandwidth, cycles, area, power, RTX 5090 equivalence or unseen-workload validation. Do not reopen V287/V296 or retired hardware candidates.

**Decision rule:** This experiment may qualify an exact reconstruction tool but cannot qualify a GPU architecture mechanism. The decisive architecture gate remains paired hardware counters or validated cycle simulation with prospective workloads and equal-resource RTL/physical comparisons.
