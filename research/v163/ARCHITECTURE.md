# V163 ARCHITECTURE — decision ledger

**Affected block:** Wave32 FP32 response register and future response FIFO/scoreboard.

**Correction:** The V162 B=4,900 response FIFO is not present in V155 or V153 RTL. Actual output is one 1,225-bit register; the upstream stage is one register, not 16. V155 input state is 3,401 logical bits, V153 intermediate state is 4,457 bits. Sixteen V155-sized upstream packets plus four dense response slots would require 59,316 logical storage bits, not V162's assumed 24,500. These are source-level widths, not mapped FF counts.

**Quantitative architectural boundary:** At the current 1,225-bit output storage budget and U=1, an ideal II=1 sparse buffer offers 2x modeled throughput for k=8 and no gain for k>=16. k=15 offers only 1.5x, with 33 register-equivalent bits of capacity left for control if two packets are retained. k=8 permits 214 register-equivalent bits of spare capacity to retain three packets. These are storage-only bounds, NOT silicon-area budgets.

**Decision:** Do not select sparse compaction or expand the response FIFO based on V162 alone. First build and synthesize a variable-entry 1,225-bit-budget response buffer with full-mask one-cycle bypass, then compare equal-area optimized dense buffer, real writeback traffic, timing, and power proxies. Maintain V151 baseline and V156 timing gate.

**V156 blocker:** OpenSTA cannot parse a concatenated assignment in V153 mapped netlist line 40278; RTL and simulator CI passed. This is infrastructure/plumbing, not scientific falsification. Proposed Yosys scalarization/preflight CI correction was attempted but connector safety rejected the write. No new OpenSTA result obtained.

**Next discriminator:** Exact real RTL widths checked against source, synthesize response-buffer mechanism and optimized dense control; rerun V156 parser-clean matched timing.