# Conditional hot-bank service headroom audit — 2026-11-20

Scope: exhaustive four-request, four-bank, two-operands/request, two-read-ports/bank synthetic *instantaneous* scheduler model. No new active mechanism. This is a diagnostic decomposition of the existing V317 oldest-protected zero-cost oracle, not GPU performance.

Executable: `python3 research/v317/rtl/conditional_hot_operand_headroom_20261120.py`. Locally independently enumerated 65,536 ordered assignments and checked grant conservation and oldest protection before GitHub persistence. GitHub-hosted execution of the committed file has not been verified.

| Number of operands addressed to bank 0 | Assignments | Greedy grants | Protected-oracle extra grants | Oracle / greedy |
|---:|---:|---:|---:|---:|
| 0 | 6561 | 14391 | 276 | 1.019179 |
| 1 | 17496 | 44328 | 696 | 1.015701 |
| 2 | 20412 | 59508 | 492 | 1.008268 |
| 3 | 13608 | 36246 | 816 | **1.022513** |
| 4 | 5670 | 13392 | 216 | 1.016129 |
| 5 | 1512 | 2790 | 0 | 1.000000 |
| 6 | 252 | 396 | 0 | 1.000000 |
| 7 | 24 | 24 | 0 | 1.000000 |
| 8 | 1 | 1 | 0 | 1.000000 |
| Total | 65536 | 171076 | 2496 | 1.014590 |

**New conditional boundary observation.** Only the exactly-three-hot-operand stratum exceeds the existing 1.02 instantaneous oracle materiality gate, at 1.022513. All strata with five or more hot operands have exactly zero oracle headroom. This is an exact *conditional mean over uniformly enumerated remaining operand placements*, not a universal per-batch bound. Stratification was exploratory and post hoc, not a prospectively validated predictor. No claim of robust gain follows: the overall 1.014590 remains below 1.02 and all oracle costs are zero by construction.

A prospective diagnostic can freeze the hot-operand count as a pre-service feature, evaluate a *realizable* stateful age-protected scheduler against compact greedy on unseen finite-buffer traces, and test whether conditional headroom survives queue-state shifts, drops, occupancy, fairness, and wiring overhead. Reject on nonpositive matched electrically legal throughput/power/area gain. Preserve the existing V317 compact-greedy area dominance (21,314.6 vs 21,324.7 um2) and electrically illegal routing. No RTL simulation, new synthesis, legal route, SRAM integration, power calibration or GPU IPC was performed. V287 remains historical; no RTX 5090 equivalence is implied.
