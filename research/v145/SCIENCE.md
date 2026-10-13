# V145 SCIENCE ledger — 2026-10-13
## Active kernel: fixed bank-parity response wiring vs flexible dual response
**Frontier:** V144 demonstrated dual-response RTL and generic synthesis (6,238 generic cells, logic depth 8) and large simulated gains over a single bus. No physical area, energy, clock, or full FP32 tile.
**Objective:** Minimize modeled FMA makespan at two 1024-bit response buses, one return per bank per cycle, unchanged RF read ports, collectors, issue width and FP32 state. Separately measure router generic synthesis cells and depth.
**Baseline:** V144 flexible dual response, work-conserving oldest-ready selector.
**Mechanism:** A fixed even/odd bank-to-bus partition may simplify response routing but strands one bus when both ready requests have the same parity. For a saturated queue with parity fraction p and negligible per-bank conflicts, idealized fixed throughput <= min(1,2p)+min(1,2(1-p)) responses/cycle against flexible 2; extreme skew approaches 2x serialization. This is a model bound, not a measured GPU law.
**Prediction:** parity-hot cases should lose more than balanced cases, and latency-dominated duplicates should lose least. Protocol fixed before running experiment.
**Decisive falsification:** >5% makespan loss on two unseen compute families unless mapped cell/timing savings establish a convincing area-throughput Pareto trade.
**Publishable success threshold:** new mechanism beyond standard bank partitioning, equal-area comparison, unseen realistic kernels, independently reproduced cycle model, mapped PPA, RTL tile integration. NOT MET.
**Architecture relevance threshold:** <=3% mean throughput loss across unseen workloads with >=15% mapped area proxy reduction and no major family regressions. NOT MET on cycle performance.
**Kill condition:** If RTL synthesizes without a compelling area/timing reduction, close fixed-parity branch and preserve flexible dual-bus router.
## Results — simulated, not hardware
96 discovery cases: fixed slower 96, tied 0, mean fixed/flexible cycles 1.30375x; even-hot mean 1.68865x.
96 unseen holdouts: fixed slower 76, tied 20, mean 1.26332x; odd-hot mean 1.70449x; dup3 mean 1.02466x.
22 wildcard probes (10.28%): slower 21, tied 1, mean 1.15093x. Final FP32 state and RF reads matched between policies.
Independent C++ exhaustive selector feasibility: 4096 3-request bank tuples, 1008 with strictly more flexible grants; 3088 ties. This is selector-level independent verification, NOT independent FMA cycle-model reproduction.
**KNOWN:** parity routing restricts response pairings. **FALSIFIED:** fixed parity is a low-penalty universal drop-in replacement for flexible dual response in this synthetic model. **BELIEVED:** flexible dual bus is worth routing cost under skew. **CONFLICTING:** dependency/latency dominated workloads can tie. **UNTESTED:** physical PPA, full Wave32 execution, power, realistic kernels, compiler reallocation, bank mapping changes.
**Novelty:** bank partitioning, multicast, and operand collectors have extensive prior art; no novelty claim. Exact Vektor-specific tradeoff only.
**Cheapest next discrimination:** RTL differential test and Yosys synthesis on both interfaces; then area-budgeted flexible-vs-partitioned router with bank remapping.
