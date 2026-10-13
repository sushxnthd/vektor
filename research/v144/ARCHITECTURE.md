# V144 ARCHITECTURE — 2026-10-13

**Decision:** reject completion-first return arbitration as the default. Preserve its negative holdout. Test a two-response, bank-conflict-checked Wave32 multicast router as a possible compromise between V143's one-response serialization and expensive three-response crossbar.

**RTL:** `research/v144/rtl/wave32_rf_dual_response.sv`: two 1024-bit response vectors, three operand slots, register-tag multicast, same-bank serialization. Requires upstream retry of unaccepted responses and stable collector IDs/tags; not a register file, FMA, scoreboard, or complete tile.

**Predicted regime:** two response vectors reduce modeled makespan when distinct operands queue and RF latency is short; the advantage disappears when long dependency latency dominates. The extra vector bus is additional hardware, not a free equal-resource win.

**Evidence:** cycle results are synthetic simulated; RTL source is an implementation candidate; generic Yosys counts are area proxies only after CI succeeds; frequency, mapped area, power, full-GPU throughput, matrix, graphics, ray, memory, software and RTX 5090-class gates all INCONCLUSIVE.

**Next:** verify RTL via Icarus and Yosys, inspect CI logs, then integrate collector identity, register-file requests, real IEEE FP32 FMA, writeback and scoreboard. Main remains stable.
