# Independent finite-FIFO accounting audit — 2026-11-19 UTC

## Scope and provenance

The previously frozen protocol is `FROZEN_FINITE_FIFO_ORACLE_CHALLENGE_20261119.md`; no seeds, thresholds, queue parameters or traffic definitions were changed. The original evaluator is `rtl/finite_fifo_oracle_challenge_20261119.py`. The independent audit is `rtl/independent_fifo_audit_20261119.py` (commit `5d4546d2fbfb3529114bf83e4790f00911926916`). A local run executed the checker on a faithful local copy of the original evaluator as fetched from the canonical GitHub branch; GitHub-hosted execution of the newly committed checker is not yet verified.

The checker independently enumerates all legal four-slot subsets for oracle optimality with a separate `Counter`-based port feasibility test, replays identical deterministic arrival streams, and verifies per-cycle FIFO bounds, cumulative arrival/admission/drop/grant conservation **including warmup**, and exact agreement with all original reported accounting fields.

## Local audit observations

All 15 frozen regime/seed combinations passed. The oracle-to-greedy grant ratios and oracle-minus-greedy dropped-arrival counts were:

| Regime | Seed 11 | Seed 29 | Seed 47 |
|---|---:|---:|---:|
| uniform16, rate3, cap4 | 1.000000 / 0 | 1.000000 / 0 | 1.000000 / 0 |
| uniform4, rate3, cap4 | 1.044265 / -2252 | 1.046928 / -2388 | 1.046535 / -2367 |
| hot65, rate3, cap4 | 1.004460 / -134 | 1.001665 / -50 | 1.000465 / -14 |
| hot65, rate3, cap2 | 1.012871 / -382 | 1.011093 / -329 | 1.011055 / -328 |
| hot65, rate1, cap4 | 1.000000 / 0 | 1.000000 / 0 | 1.000000 / 0 |

The 65%-hot regime is rejected by the frozen 1.02 relevance criterion even with an impossible zero-cost maximum-cardinality oracle. Uniform four-bank retains synthetic oracle headroom but **no implementable mechanism is demonstrated**. The checker is a second accounting implementation, not an independent hardware design or GPU benchmark.

## Interpretation and next gate

The earlier instantaneous batch-distribution law is not a valid general predictor of finite-queue throughput: contention changes the endogenous queue-state distribution. The full-cycle accounting check closes a potential conservation loophole in the first simulator, but does not resolve fairness, clock, area, wire, SRAM, or electrical physicality. The compact-greedy baseline's 21,314.6 um2 versus pairwise 21,324.7 um2 area result and electrical violations remain binding. Do not revive V317's positive tile claim. Next scientifically meaningful gate is a preregistered, equal-resource, physically implementable scheduler and matched electrically legal routing; stop if the no-win bound applies.

Reproduce: `python3 research/v317/rtl/independent_fifo_audit_20261119.py`. No third-party dependencies. No RTX-5090-equivalence claim.
