# V317 exact selector physical no-go and rotating-priority strong control (2026-11-01)

**Decision:** reject the exact maximum-cardinality register-bank selector as an architecture improvement. Preserve it as a negative-control oracle. The rotating-priority RTL is a **simple control**, not a promoted novel mechanism. Existing V317 register forwarding remains rejected. Do not revive V287/V296.

## Source-pinned synthesis evidence

The previously queued [hosted matched RTL/Yosys run 41275143656](https://github.com/sushxnthd/vektor/actions/runs/41275143656) completed successfully at commit `4cca0062e327c95473558a614dd2b73e7912e76e`. Both baseline and exact RTL synthesized; the independent two-bank RTL test passed. From the preserved workflow's `matched_cost.json` and `ltp -noff` logs:

| Arbiter | Generic Yosys cells | Longest generic logic path | Maximum net sink fanout |
|---|---:|---:|---:|
| Fixed-priority source RTL | 1,321 | 49 levels | 49 |
| Exact maximum-cardinality challenger | **5,116** | **72 levels** | 33 |
| Exact / fixed | **3.872824x** | **1.469388x** | Not comparable as a delay |

No clock, placement, routing, wire parasitics, standard-cell area or GPU IPC was measured. Logic levels are **not** a frequency ratio. The 3.87x cost is the isolated combinational arbiter, not the whole GPU tile. Exact's 5,116 cells include no sequential flops; the stronger rotating control includes a phase counter.

## Workload falsification, already frozen before physical result

The frozen 30,000-cycle, four-slot streaming experiment showed no useful exact-selector completed-work gain: in the predicted-win regime exact/fixed = **0.999807x**, and in the unseen transfer **1.000018x**. A single-cycle grant-count witness is not a completed-work gain. This is a synthetic bank-service model, not GPU IPC.

At equal clock and with arbiter generic-cell cost used **only as an illustrative area proxy**, if the original arbiter accounts for a fraction `a` of the tile's area, an isolated replacement with cell ratio `r=5116/1321` implies the *assumed* tile area factor

`A_new/A_old = 1 + a*(r-1)`.

For `a=0.5%,1%,2%,5%`, this gives `1.01436, 1.02873, 1.05746, 1.14364`. With relative clock factor `c=f_new/f_old`, the required IPC improvement for throughput per area is **`IPC_new/IPC_old > [1+a*(r-1)]/c`**. Because exact did not improve completed service in the frozen regime, there is no evidence to clear even the equal-clock boundary for any positive area penalty. This is a sensitivity identity, **not** a chip area estimate or signoff.

## Strong simple control: frozen before new RTL synthesis

[Frozen protocol](FROZEN_ROTATING_PRIORITY_PHYSICAL_CONTROL_20261101.md) at `0825f26` precedes [rotating RTL](rtl/rf_bank_rotating_control.sv) and its synthesis. The new source-faithful design rotates a two-bit priority phase each cycle, permutes bank requests into the existing greedy arbiter, and inverse-permutes grants. No additional bank ports, issue slots, register forwarding or operand sharing.

The [independent RTL oracle](rtl/tb_rf_bank_rotating.sv) enumerates 16,384 two-bank configurations across all four phases plus 64 directed 16-bank cases and a phase-wrap check: **16,449 planned checks**. Results are **not claimed passed until hosted CI completes**. The [matched three-way synthesis and frozen holdout workflow](../../.github/workflows/v317-rf-rotating.yml) preserves outputs including failures.

## Frozen unseen transfer: local independent replication

The separate [independent standard-library audit](rf_rotating_independent_audit.py) reproduces the frozen arrival streams and all four policies without importing the candidate simulator. A locally executed equivalent implementation produced the following; the repository-hosted primary-vs-independent cross-check is **pending**.

| Unseen regime | Fixed completed | Rotating completed | Oldest-first completed | Age-aware exact completed | Rotating/fixed |
|---|---:|---:|---:|---:|---:|
| Four-bank p=.52, seed 317952 (predicted no material win) | 56,127 | 56,144 | 56,141 | 56,145 | **1.000303x** |
| Four-bank p=.60, seed 317960 (stressed) | 60,899 | 64,784 | 64,774 | 64,785 | **1.063794x** |
| Private-bank p=.55, seed 317955 (negative control) | 59,470 | 59,470 | 59,470 | 59,470 | **1.000000x** |

At p=.60, the final backlogs are **4,293 fixed / 16 rotating / 17 oldest-first / 6 age-aware exact**. p99 waiting times are **6,811 / 23 / 11 / 8 cycles**, respectively. At p=.52 the p99s are **62 / 8 / 5 / 5**. The apparently dramatic fixed-priority failure is largely a fairness/starvation artifact: a simple oldest-first greedy control almost matches rotation and exact age-aware service. There is **no identified novel maximum-cardinality mechanism**.

## Next falsification and gate

1. Require final-head hosted rotating RTL oracle and independent stream checker PASS before accepting this local transfer.
2. Extract rotating/fixed/exact matched generic cells, flop count, fanout and logic depth. Do not infer actual frequency from generic levels.
3. Even if rotating is cheap, treat it as a baseline. Any new candidate must beat rotating and oldest-first on frozen unseen workloads at matched ports, occupancy, tile area and clock, then survive standard-cell timing, placement/wire/load and power proxies.
4. Do not spend more runs polishing the rejected exact selector; prioritize identifying an implementable distinct resource advantage.

**No physically validated GPU throughput improvement, routed electrical closure, or RTX-5090 equivalence has been established.** Kernellum PR #119 remains unchanged.
