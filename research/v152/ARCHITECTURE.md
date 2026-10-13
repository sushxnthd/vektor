# V152 ARCHITECTURE ledger

**Affected block:** Wave32 FP32 FMA finisher following the V148 multiplier and V151 collector integration.

**Decision:** retain V151 as correctness reference. Test balanced leading-one encoding as a drop-in combinational alternative; do not select it for silicon without technology-mapped area/delay. Both designs use the same functional I/O and 64-bit arithmetic window. A clocked FMA pipeline and tagged scoreboard/writeback are still missing.

**Build vs research:** full-range RTL correctness and generic synthesis are build gates. The balanced-priority experiment is research into a bottleneck, not a scientific law or claim of improved GPU throughput. Compare raw Yosys logs before advancing the design.

**Wildcard (cheap):** inspect the highest-bit-only input (bit 64) and zero as potential leading-one corner cases. The independent bit_length oracle covers these cases. A different bank mapping or scheduling mechanism is not being pursued in this run.

**Outstanding:** technology-mapped timing/area/power, scoreboard/writeback, actual kernel throughput, tensor path, memory/NoC, compiler/ISA, full-chip feasibility. RTX 5090 comparison not established.
