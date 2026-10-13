# V143 ARCHITECTURE — 2026-10-13

**Candidate design change:** coalesce identical RF operand tags before 16-bank arbitration; broadcast one returned Wave32 vector to all matching source slots. Preserve V142 producer multicast. Avoid additional RF ports merely to fetch the same register twice.

**RTL boundary:** new combinational request/response mapper, not a complete RF, collector, scoreboard or FMA. Requires stable collector source tags from read acceptance through response; no integrated cancellation verification. Testbench exercises 800 full-Wave32 data vectors. Generic Yosys area/logic-depth comparison is a proxy, NOT physical PPA.

**Model finding:** with RF duplicate-read coalescing in the strongest baseline, forwarding no longer wins in frozen 2x-duplicate FMA cases; other cases remain conditional. Hardware forwarding bus costs are not area/energy-equalized.

**5090 capability gates:** FP32 INCONCLUSIVE; tensor INCONCLUSIVE; graphics/raster INCONCLUSIVE; ray INCONCLUSIVE; memory INCONCLUSIVE; cache/NoC INCONCLUSIVE; software INCONCLUSIVE; physical PPA INCONCLUSIVE; reproducibility PARTIAL (model + isolated RTL only).

**CI state:** workflow vektor143.yml runs independent abstract checks, Icarus Verilog and Yosys, saves logs. Read actual Actions run before declaring RTL PASS. Main unchanged.
