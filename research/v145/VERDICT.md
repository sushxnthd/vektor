# V145 decisive falsification — 2026-10-13
**Verdict: CLOSE fixed even/odd bank-partitioned response routing as a V-Tile default.** This is an engineering rejection, not a scientific novelty claim.

**Implementation:** research/v145/rtl/wave32_rf_parity_fixed.sv vs V144 dual-flexible router. Both have 2x1024-bit response inputs, 3x1024-bit operand outputs, tag matching and duplicate-slot multicast. Fixed uses physical port0=even, port1=odd; flex accepts any distinct-bank pair. Both are combinational router slices, not complete RF/collector/tile.

**Exact selector proof by enumeration:** all 4096 triples of 16-bank response requests tested in independent C++; flexible supports at least as many grants for each triple; strictly more in 1008 and equal in 3088. This is a local one-cycle feasibility result, not an end-to-end scheduling dominance proof.

**RTL:** 1600 full-Wave32 legal parity-ordered differential vectors matched V144 outputs; invalid parity/tag negative tests passed in Icarus. Does not verify asynchronous backpressure or collector IDs.

**Synthesis (Yosys 0.33 generic):** flexible = 6238 cells, path length 8; parity-fixed = 8296 cells, path length 10. Fixed uses 32.99% more generic cells and 25% greater generic logic depth in this RTL realization. Generic depth is NOT a frequency measurement. Upstream bank-to-bus switch fabric is NOT included, so no complete interconnect PPA dominance claim.

**Synthetic FMA cycle model (one representative FP32 lane/wave):** 96 discovery fixed slower 96 (mean cycles ratio 1.30375); 96 unseen holdout fixed slower 76/tied 20 (mean 1.26332); 22 wildcard fixed slower 21/tied 1 (mean 1.15093). Final FP32 register state and RF reads identical. Full cycle-model source and raw CSV are preserved in the local V145 reproducibility package; the GitHub branch currently carries the aggregate JSON and independently executable RTL/selector checks. Do not misrepresent this as a fully repo-reproducible FMA cycle study.

**Gate:** fixed parity fails the architecture-relevance criterion (<=3% unseen mean slowdown + >=15% mapped-area improvement). No RTX 5090-class gate advanced.

**Decision:** retain V144 flexible dual return provisionally; prioritize attaching it to collector IDs, RF requests, FP32 FMA and scoreboard, then perform physically meaningful interconnect cost comparisons. Reopen parity only if upstream bank-to-bus fabric cost reverses the full-system area/energy Pareto result.

**Evidence:** https://github.com/sushxnthd/vektor/actions/runs/38395830852 (successful RTL + Yosys).
**SCIENCE:** known bank partitioning creates parity imbalance; V145 provides Vektor-specific negative evidence, not a new mechanism.
**ARCHITECTURE:** do not allocate RTL integration effort to fixed-parity network; next decisive experiment is flexible dual-response + real collector/scoreboard.
