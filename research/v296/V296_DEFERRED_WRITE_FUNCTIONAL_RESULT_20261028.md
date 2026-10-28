# V296: deferred-write retiming restores two-port read-before-write semantics (2026-10-28)

**Evidence:** prospective functional RTL result and independent Python state-invariant audit. **Not** synthesis, timing closure, routed electrical feasibility, energy, real GPU traces, or architecture performance advantage.

## Preregistration and exact mechanism
Frozen before hosted execution at commit `d2894208` in [DEFERRED_WRITE_RF_RETIMING_PREREG_20261028.md](DEFERRED_WRITE_RF_RETIMING_PREREG_20261028.md). Previous address-only delayed reads failed read/write collisions; an unrestricted old-value log could demand a third read port. The new *symmetric implementation repair* delays the one global write by exactly one edge, as well as the operand read, while leaving both V296 pairwise and V295 optimized-serial arbitration unchanged.

Let S_t be the immediate-write reference RF state before edge t and W_t its write. At edge t the retimed design captures operand addresses and buffers W_t. At edge t+1, its RF still contains S_t, so the read of the t request samples the correct pre-W_t data; on the same edge W_t commits via nonblocking assignment. Inductively, after edge t+1 the retimed RF is S_(t+1), ready for the next read. There is **one** global write port and **two** dynamic reads per bank, not a hidden third port. Operand execution is visible one additional edge later. The proof applies to the declared quiescent-reset interface, **not arbitrary mid-flight reset or external same-cycle RF observers**.

## Independently executed results
[Hosted Icarus run #40626709496](https://github.com/sushxnthd/vektor/actions/runs/40626709496), original independent immediate-write oracle, both pairwise and serial:
| Words/bank | Randomized cycles | Admitted waves | Directed+random read/write collisions | RTL verdict |
|---:|---:|---:|---:|---|
| 4 | 2,048 | 6,608 | 236 | PASS |
| 8 | 2,048 | 6,608 | 207 | PASS |
| 16 | 2,048 | 6,608 | 191 | PASS |

Each test also checks exact issue identity, maximum two reads per bank, non-X execution data, and dynamically addressed RF contents. These are *functional simulation* checks, not formal RTL equivalence over all possible inputs.

The separate [Python invariant checker](v296_deferred_write_checker.py) exhaustively enumerated **1,600 two-edge small-memory cases**, with **zero deferred-write errors** versus **960 errors** in a deliberately naive same-edge-write negative control. Across six independent seeded depth/traffic regimes (120,000 synthetic cycles, 481,936 operands, 11,100 collisions), the deferred-write invariant held with **zero errors**, versus **11,058** naive errors. The [machine-readable output](V296_DEFERRED_WRITE_SEMANTIC_RESULT_20261028.json) is committed. These are not unseen GPU workload tests.

## What this resolves and what it does not
- Resolves the specific **semantic collision obstruction** to one-cycle address retiming *under the declared RF interface*. Does not need a collision snapshot or a third read port.
- Does **not** establish that the scheduler-to-RF critical path is physically shortened enough; registered-bank-to-RF-data path may remain too long. Added address registers and write buffering consume area and energy.
- Adds one edge to operand-use latency; prior exact occupancy law predicts a >1.9x frequency threshold in the N=2, B=2, q=.9 low-occupancy regime, versus >1.0009x in a bandwidth-saturated regime. This does not itself show V296 superiority over serial.
- **No claim** of arbitrary reset equivalence, external memory-order equivalence, SRAM-macro compatibility, full GPU tile integration, routed feasibility, or RTX-5090-class performance.

## Next hard gates
The [same-run matched Nangate45 synthesis jobs](https://github.com/sushxnthd/vektor/actions/runs/40626709496) for D4 and D8 were pending at report creation. Require both candidate and serial mapped area/logic-depth results and same-depth pre-CTS critical paths. Reject if area exceeds 30,000 um2 or if symmetric retiming cannot remove sufficient critical-path delay. Only then consider equal-depth extracted-RC routing at 3.5 ns, 2x RC, setup >=+50 ps, hold >=0, zero cap/slew/DRC. Compare measured frequency gains against the *already frozen* occupancy thresholds and strongest serial control before any workload claim.

**Research status:** V296 remains the only provisional mechanism; V287 retired; Kernellum PR #119 and prospective holdouts untouched. Existing negative results and sealed workload regimes preserved.
