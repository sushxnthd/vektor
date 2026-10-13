# V152 ARCHITECTURE ledger

**Affected block:** Wave32 FP32 FMA finisher following the V148 multiplier and V151 collector integration.

**Decision (verified V152): REJECT balanced leading-one replacement.** It preserved correctness but increased generic cells from 14,459 to 19,981 (+38.19%) and generic longest path from 383 to 439 (+14.62%) with identical tool flow and I/O. Retain V151 as functional baseline. This is a decisive generic-synthesis falsification, not physical timing evidence. Next highest-information action: inspect actual Yosys critical path and test one register boundary / fixed-shift subpath before any further encoder redesign. A clocked FMA pipeline and tagged scoreboard/writeback are still missing.

**Build vs research:** full-range RTL correctness and generic synthesis are build gates. The balanced-priority experiment is research into a bottleneck, not a scientific law or claim of improved GPU throughput. Compare raw Yosys logs before advancing the design.

**Wildcard (cheap):** inspect the highest-bit-only input (bit 64) and zero as potential leading-one corner cases. The independent bit_length oracle covers these cases. A different bank mapping or scheduling mechanism is not being pursued in this run.

**Outstanding:** technology-mapped timing/area/power, scoreboard/writeback, actual kernel throughput, tensor path, memory/NoC, compiler/ISA, full-chip feasibility. RTX 5090 comparison not established.
