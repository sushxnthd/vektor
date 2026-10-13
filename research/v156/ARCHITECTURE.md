# V156 ARCHITECTURE ledger

**Affected block:** Wave32 FP32 FMA finisher after operand collector/multiplier, before scoreboard/writeback.

**Build work:** Reuse verified V151 and V153 RTL; produce full mapped one-lane Verilog and OpenSTA critical-path reports using the same library and constraints. Rerun V155's oracle and mapped-area gate. This is a measurement gate, not a new arithmetic mechanism.

**Current decision:** retain V151 functional reference and V153 candidate until mapped STA, area and real workload checks are available. Never extrapolate one-lane timing to Wave32 routed timing.

**If candidate passes threshold:** prioritize full Wave32 tagged scoreboard/writeback and tile-level timing, then compute-bound, memory-bound, divergent workloads; test actual frequency/throughput boundary. If it fails: preserve negative result and inspect critical endpoints before revising cutset.

**Explicitly not demonstrated:** technology placement, parasitic extraction, power, clock-tree, tensor path, memory/NoC, compiler, system robustness, RTX 5090 equivalence.
