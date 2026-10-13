# V148 SCIENCE ledger (2026-10-13)
Status: CAPABILITY-BUILDING, not a novel mechanism. Evidence classes: RTL candidate, pending HDL simulation and generic synthesis.

**Kernel:** Does RF bank remapping yield >=10% more completed Wave32 FP32 work per cycle with <=2% area/timing proxy regression once real arithmetic and backpressure are present?
**Frontier:** V147 XOR mapping improved synthetic independent bank-hot workload by 1.239x in software simulation, but not dependent kernels. V145 rejected fixed-parity routing. XOR banking is prior art.
**Objective:** completed lane-products/cycle, bank conflicts, generic mapped cell count, critical-path proxy.
**Equal-resource baseline:** flexible dual-response, 16-bank low-bit mapping, identical collector and multiplication slice; compare against XOR indexing with same bank count and ports.
**Mechanism/prediction:** XOR only helps when independent bank-hot responses conflict; RAW waits and output stalls mask gain. Prediction >=10% independent, <5% dependent at RF latency 1.
**Falsification:** tagged RTL mismatch, unseen workload fails crossover, or matched synthesis/timing cost exceeds throughput gain.
**Publishable threshold:** new mechanism, independent replication, realistic unseen workloads, equal physical resources, measured architectural effect. NOT MET.
**Architecture threshold:** >=10% unseen throughput gain, <=2% mapped area and timing regression, <=2% worst broad workload regression. NOT MET.
**Kill condition:** after three runs no realistic >=5% gain at matched resources; preserve negative results.
**This run:** integrate V146 collector with a one-deep elastic Wave32 exact 24x24 significand multiplier and verify/synthesize. No claim of correctly rounded IEEE FMA, energy, or RTX 5090 class.
**Wildcard:** vary downstream stalls and bank-hot concentration after the baseline gate.
**Next:** align/add/round, exception behavior, tagged writeback and scoreboard, then equal-resource bank-index comparison.
