# V296: one-cycle RF read retiming violates read-before-write or the two-port budget (2026-10-28)

**Scientific result: a tempting upstream scheduler-to-RF pipeline cut is not a free physical repair.** This is an independently executable Python reference-model falsification, not RTL simulation, synthesis, or routed timing.

## Physical motivation and frozen gate

The SHA-pinned D8 V296 extracted scheduler-to-staged-operand path fails setup by 734.592 ps against the +50 ps guard. The D4 optimized serial path fails by 1366.510 ps. These are **different depths**, not a matched architecture comparison. Both have the same global write port and two dynamic read ports per bank. A proposed symmetric repair registers operand addresses at issue edge t and reads RF at t+1, intending to split the critical combinational path.

The original RTL reads **before** the write at edge t. A naive delayed read instead observes the RF **after** the write at t, which changes values for read/write collisions.

## Executed finite-state falsification

The committed script exhaustively enumerates 69,632 cases (two banks, two words each, 2-bit data, two simultaneous read requests, one optional global write):

| Model | Incorrect cases |
|---|---:|
| Naive delayed RF read | **21,504** |
| Global previous-write old-value undo | 0 |
| Selective old-operand collision snapshot | 0 |

A separate seeded 50,000-cycle synthetic experiment uses 16 banks, eight words per bank, eight-bit data, up to eight issued operands with **at most two reads per bank**, and one global write. It issues **199,889 operands**; 1,233 cycles have read/write collisions; naive retiming misreads on **1,229 cycles**. Both corrected reference models have zero mismatches. This is synthetic functional evidence, not real GPU traces or an RTL proof.

## The physical obstruction

The global undo scheme stores the prior write's old value and address. In bank 0, when the two operand ports read distinct words 0 and 1 while a write targets word 2, capturing the old value of word 2 requires a **third distinct bank read**. A flop RF may expose non-macro taps, but this is not an equal-resource two-port macro assumption. A 16-bit global undo register (valid + 7-bit address + 8-bit data) is not the full physical cost.

The selective collision snapshot instead captures old values only for issued operands that collide with the write, using their existing operand read ports. It is functionally correct in this model, but its **same-cycle RF-data-to-snapshot-register path still exists on collisions**. Even rare collisions remain subject to static timing analysis; the current setup failure is not thereby repaired.

## Predictive occupancy boundary, not a speedup

For an in-flight capacity N, issue ceiling I, shared bandwidth ceiling B, and token residence L cycles, a necessary throughput bound is T <= min(I, B, N/L). With I=4, N=2 and B=2, an idealized latency increase L=1 to L=2 reduces this upper bound from 2 to 1 wave/cycle. With N=4, B=1, both bounds equal 1. This sensitivity is an analytical capacity ceiling, not observed throughput.

## Decision

**Kill address-only delayed RF reads** for functional non-equivalence. **Reject the unrestricted global old-value undo as equal-resource** absent a demonstrated two-port implementation. Selective snapshot remains a possible semantic repair but not a demonstrated timing improvement. Before any expensive routed run, require a synthesizable **symmetric** two-port implementation, cycle-accurate arbitrary-collision oracle, matched mapped area and pre-CTS timing, and then both contestants' post-route extracted RC with the unchanged 3.5 ns clock, 2x RC, +50 ps setup, >=0 hold, zero DRC/cap/slew, and 30,000 um2 area budget.

V296 remains the sole provisional mechanism; V287 retired. Workload holdouts remain sealed. Kernellum PR #119 untouched. No GPU throughput, power, or RTX-5090 equivalence claim.

Reproduce: `python3 research/v296/v296_retiming_hazard.py --output /tmp/v296_retiming_hazard.json`.
