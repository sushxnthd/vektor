# V317 pre-route Nangate45 STA: load-induced reversal (2026-11-01)

## Source-pinned verification

Frozen protocol: [FROZEN_RF_OPENSTA_CELL_TIMING_GATE_20261101.md](FROZEN_RF_OPENSTA_CELL_TIMING_GATE_20261101.md) committed at `e7f1e6e` **before** the timing implementation and results. First hosted OpenSTA run #41304228217 failed because OpenSTA 2.0.17 accepts one TCL script argument, not positional parameters. Second run #41304317520 failed because this older OpenSTA lacks three newer TCL commands. Third run #41304406781 successfully produced 12 real timing paths but the checker correctly failed because it mistook a later *negative slack subtraction* for the forward data arrival. The initial 0.002/0.02/0.1 loads also had an incorrect capacitance unit: Nangate45 Liberty declares **fF**, not pF. These failures and the source history are retained, not silently discarded.

The corrected [source-pinned workflow #41304535696](https://github.com/sushxnthd/vektor/actions/runs/41304535696) **PASSED** on commit `0b9e58cd743509c740f957f4c2314403d69bac7a`. It installed Yosys and OpenSTA 2.0.17 on Ubuntu 22.04, verified the pinned Nangate45 Liberty Git blob `90e4afb274cfc6514c587c434c77903d554117d1`, mapped four RTL implementations with an identical recipe, analyzed 12 timed grant-output paths, and passed five independent parser regressions. [Raw mapped netlists, logs and audit artifact #13082951666](https://github.com/sushxnthd/vektor/actions/runs/41304535696/artifacts/13082951666).

## Measured worst grant-output data arrival (nanoseconds)

| External load | Source fixed | Pairwise fixed | Source rotating | Pairwise rotating |
|---:|---:|---:|---:|---:|
| 2 fF | 1.19 | **0.52** | 2.60 | **1.33** |
| 20 fF | 1.28 | **0.70** | 2.67 | **1.39** |
| 100 fF | **1.68** | 2.29 | 3.08 | **1.79** |

**Predeclared 2-fF and 20-fF delay predictions passed for both grant-equivalent pairwise implementations.** The prospective 100-fF stress test reveals a **fixed-priority ranking reversal**: pairwise fixed becomes **36.31% slower** than source fixed at the heavily loaded output, despite retaining its 67.50% mapped cell-area reduction. Pairwise rotating remains faster than source rotating at 100 fF. All numbers are pre-route, characterized-cell estimates with ideal wires, not routed STA.

The matched mapped-cell area comparison from run #41296883857 remains: source fixed 798.798 vs pairwise fixed 259.616 square micrometers; source rotating 997.234 vs pairwise rotating 445.018 square micrometers. The timing workflow uses the same library and mapping recipe but its mapped netlists should still be independently checked for exact cell/area parity before claiming bit-identical synthesis.

## Physical interpretation and new prospective boundary

A logic-minimized design can have a shorter intrinsic path yet a weaker critical output driver; output capacitance may reverse its delay ranking. At 20 fF the fixed-pairwise minus source-fixed delay is -0.58 ns; at 100 fF it is +0.61 ns. **Linear interpolation between those two measured differences predicts a crossover near 59.0 fF**. This is an explicitly *post-result* hypothesis, not a predeclared prediction. A separate prospective 40/60/80-fF holdout is required before trusting it. The 2-fF and 20-fF results support an implementation optimization only; they do not establish throughput or timing closure.

## Decision

**Do not promote a GPU architecture mechanism.** The grant-equivalent pairwise fixed implementation has zero intrinsic service-throughput gain at equal clock and ports. The load reversal defeats any unconditional timing-superiority claim. Strong oldest-first and rotating fairness baselines remain mandatory. No routed RC, placement, slew/electrical DRC, power, GPU IPC, tile-level speedup or RTX 5090 equivalence is established. Kernellum PR #119 is unchanged.
