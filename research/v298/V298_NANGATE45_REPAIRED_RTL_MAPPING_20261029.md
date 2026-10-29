# V298 repaired RTL and Nangate45 mapped-cell falsification (2026-10-29)

**Evidence tier:** independently checked controller RTL plus four-policy Nangate45 standard-cell mapping. **No placed/routed timing, extracted RC, electrical closure, switching power, complete MSHR-array cost or GPU IPC.**

## Exact event-order bug

Original RTL incorrectly allowed background refill of the final MSHR in the same cycle as a critical return with a known dependent miss. The independent reference found **15 discrepancies among 2,560 policy/state/input combinations** in the old equation. A directed trace has `free_count=1, guard_q=0, critical_return=1, dependent_known=1, bg_pending=1, crit_ready=0`: old RTL grants background, while the discrete-event simulator already reserves the returned credit. The corrected RTL blocks it using a combinational effective guard. Cancellation takes precedence.

The updated clocked 4-policy RTL test passed 2,560 output checks and 2,560 next-state checks. A separately structured Python checker passed all 2,560 combinations, detected the 15 old-RTL mismatches, and preserved a 256-cycle starvation counterexample without dependency cancellation or critical issue.

[Hosted repaired RTL and holdout reproduction #40793545889](https://github.com/sushxnthd/vektor/actions/runs/40793545889) passed. [Matched Nangate45 mapping #40793696412](https://github.com/sushxnthd/vektor/actions/runs/40793696412) passed after repairing the initial `check -assert` failure caused by missing Liberty blackbox port declarations. The failed attempt [#40793626170](https://github.com/sushxnthd/vektor/actions/runs/40793626170) remains preserved.

## Matched mapped area

All policies share the same controller ports, registered guard output, Yosys synthesis flow, fixed Nangate45 typical Liberty revision `eda8e552974d47a12616294dddf4012d892548d3`, and standard-cell mapping script. These are isolated admission-controller macros, not full MSHR queues.

| Policy | Mapped standard-cell area (um^2) | Relative to work-conserving |
|---|---:|---:|
| 0: work-conserving critical-first | 12.236 | baseline |
| 1: fixed one-credit reserve | 12.236 | +0.00% |
| 2: corrected dependent-credit guard | 13.034 | **+6.52%** |
| 3: deadline-aware oracle (future-latency input) | 13.832 | +13.04% |

Policy 3 is **not implementable without a separate prediction mechanism**. Its area omits the predictor and cannot be treated as a fair hardware baseline. The equal mapped area of policies 0 and 1 is a mapper result, not proof of identical logic or timing.

The repaired guard adds **0.798 um^2 mapped area** versus the work-conserving controller. This is a **6.52% controller-macro penalty**, not a 6.52% GPU area penalty. It also adds a same-cycle critical-return-to-background-grant path, so the area number alone cannot establish clock feasibility.

## Scientific interpretation and next kill gate

The frozen synthetic H1/H2 results remain reproducible but cannot establish physical performance. The corrected RTL now matches the intended event order at the isolated admission interface. The candidate is not viable unless a scoreboard can prove bounded cancellation of false dependent predictions or a watchdog is implemented, and unless matched extracted-RC physical implementation, variable-latency/false-positive sensitivity, and a strong implementable equal-state control retain a joint latency/throughput benefit.

Next: one bounded prospective variable-latency/cancellation-delay experiment and matched routed PPA under common clock, loads, area and physical constraints. Kill V298 if a feasible equal-cost control dominates or if its critical-return path violates timing. Preserve the negative evidence. No novelty, power, RTX-5090 equivalence or world-class architecture claim is justified.
