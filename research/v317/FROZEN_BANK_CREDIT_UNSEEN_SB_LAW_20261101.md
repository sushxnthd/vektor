# V317 preregistered unseen S/B transfer for generic pairwise-cell law (2026-11-01)

Frozen **after** the nine-point discovery sweep but **before** running any new holdout synthesis. This is an implementation-cost law, not an architecture throughput law. The original [nine-point protocol](FROZEN_BANK_CREDIT_SB_SCALING_20261101.md) and results remain immutable historical evidence.

## Derived law (fit only on S={2,4,8}, B={4,16,64})
With W=log2(B), predict Yosys generic pairwise cells

C(S,W) = (14*S*S - 17*S + 2) + (4*S*S - 2*S - 2)*(W-2).

This expression interpolates all nine training points exactly. That is not validation.

## Unseen holdouts, frozen predicted counts
| Slots S | Banks B | W | Predicted pairwise cells | Tolerance |
|---:|---:|---:|---:|---|
| 2 | 8 | 3 | 34 | exact |
| 4 | 32 | 5 | 320 | exact |
| 8 | 8 | 3 | 1,000 | exact |
| 3 | 8 | 3 | 105 | <=10% relative |
| 5 | 32 | 5 | 531 | <=10% relative |
| 6 | 32 | 5 | 794 | <=10% relative |
| 7 | 8 | 3 | 749 | <=10% relative |

The first three test unseen bank widths at previously seen slot counts. The remaining four test unseen slot counts and bank widths simultaneously. The 10% tolerance is declared prospectively, not fitted to holdout outcomes. Any miss must be reported and the law narrowed or rejected, not refitted on these same holdouts and called prospective.

## Strong controls and no-go
For each holdout, use the identical synthesizable bank-mask RTL, independent 2-reads-per-bank RTL oracle, same Yosys version/commands, source pin, full logs, and preserved netlists. Report pairwise and mask cells, logic depth, fanout, flops. Reject any claim of throughput advantage because grants are identical at matched clock. Generic Yosys cost is not standard-cell area, wire RC, power, physical signoff or GPU IPC. A fitted cell-count law alone does not meet Vektor's world-class mechanism completion gate.
