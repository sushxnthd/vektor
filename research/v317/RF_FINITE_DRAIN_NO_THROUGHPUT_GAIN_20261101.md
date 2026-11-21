# V317: single-cycle RF scheduling gain disappears under finite-batch drain (2026-11-01)

**Decision: reject the prior 1.0468x / 1.0108x grant-count ratios as throughput evidence.** The original V317 forwarding candidate remains rejected. The exact bank-selection RTL is only a resource-matched challenger pending hosted RTL simulation and generic synthesis; it is not a promoted architecture mechanism.

## Frozen predictions

The protocol was committed as `FROZEN_RF_FINITE_DRAIN_CHALLENGE_20261101.md` at `6decf5c`, before the new drain checker or aggregate results.

* Predicted single-cycle win: three requests (0,0),(0,1),(0,1), valid=0b0111. Priority grants one; exact grants two. **Both take two cycles to drain the complete batch**, matching the preregistered no-throughput-gain prediction.
* Predicted no-win: (0,0),(1,1), valid=0b0011. Both issue two requests and finish in one cycle, also matching prediction.

## Finite-batch service results

The new checker removes completed instructions each cycle, preserving the original four request-slot priorities. It independently solves the optimal multi-cycle partition by dynamic programming, charging both reads of each instruction against the same two ports per bank. All results below are synthetic finite-batch *service cycles*, not GPU IPC.

| Frozen/transfer set | Cases | Fixed-priority total cycles | Myopic exact-cardinality total cycles | Optimal multi-cycle total cycles | Exact better/tie/worse |
|---|---:|---:|---:|---:|---|
| Exhaustive two-bank, all masks/pairs | 4,096 | **6,508** | **6,508** | **6,508** | 0 / 4,096 / 0 |
| Unseen fixed-seed four-bank transfer | 10,000 | **12,421** | **12,425** | **12,410** | 7 / 9,982 / 11 |

**Falsification:** the exact single-cycle selector does not improve finite-batch drain at all in the exhaustive two-bank space. In the four-bank transfer it is marginally *worse* in aggregate than fixed priority (12,425 vs 12,421 cycles), and both schedulers sometimes lose to a multi-cycle optimal scheduler. A larger per-decision grant count is not sufficient to infer higher completed-work throughput.

The independent finite-batch audit was run locally with a separate implementation of the fixed-priority, exact-cardinality and multi-cycle oracles, reproducing the tabulated counts. The committed regression test fixes these totals. Hosted CI must be checked separately; do not claim it passed before inspection.

## Physical gate in progress

A distinct experimental RTL comparator `rtl/rf_bank_exact_challenger.sv` and exhaustive 4,096-case two-bank Icarus testbench are committed. The RTL testbench also checks the two frozen witnesses, port exclusivity, deterministic tie-break and baseline consistency. A dedicated no-cost Actions workflow performs identical Yosys generic synthesis commands for the original priority arbiter and the exact challenger and archives cell/fanout/depth logs.

**At this report's writing, the new hosted run is queued.** No cell-area, logic-depth, timing, fanout, or electrical outcome is asserted here. The RTL selection network may be prohibitively expensive. If matched area/timing erases any remaining throughput advantage, the scheduler must be killed. Do not confuse generic Yosys statistics with routed timing or electrical signoff.

## Scope and next gate

This deliberately simple model has no arrivals, dependencies, register-file request pipeline, collector pressure, warp age, memory latency, occupancy, power or wire delay. The current no-gain finding already invalidates the headline synthetic first-cycle claim; the physical comparator can only further constrain it. A credible architecture claim would need an actual workload-level improvement against the strongest same-resource and age-aware baseline, positive boundary law, and clean routed timing. None is established.

Kernellum PR #119 was not modified. The Vektor draft PR #34, branch and negative evidence are preserved. No RTX 5090 equivalence claim.
