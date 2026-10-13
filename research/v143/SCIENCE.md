# V143 SCIENCE — 2026-10-13

**Active kernel:** Does producer-level Wave32 forwarding/multicast retain a throughput advantage when a nonforwarding baseline coalesces duplicate register reads?

**Frontier:** V142 multicast simulation overcharged the no-forward baseline for duplicate RF operands. V142 RTL CI passed in Actions run 38377160726. No integrated GPU PPA.

**Objective:** completion cycles, RF read count, physical writeback broadcasts at fixed banks/ports, collectors, issue width and latencies.

**Strongest control:** best grouped/interleaved nonforwarding policy WITH RF duplicate-read coalescing. Forwarding bus is extra hardware, so throughput results do not establish equal-area Pareto improvement.

**Mechanism hypothesis:** FMA(x,x,c) needs two physical reads, FMA(x,x,x) one, not three. Coalescing may erase forwarding benefits seen against uncoalesced RF.

**Decisive falsification:** a read count not equal to distinct source tags; FP32 final-state mismatch; independent timing checker disagreement; no forwarding win on unseen holdout.

**Publishable threshold:** new mechanism beyond established operand reuse/bypass, multiple unseen realistic kernels, mapped timing/area and energy-equalized comparisons. NOT MET.

**Architecture threshold:** >=5% cycles on two unseen workload classes with no increase in RF traffic plus RTL/PPA validation. NOT MET.

**Kill condition:** three runs without mechanism boundary or matched-resource gain.

### Frozen local model results (evidence class: synthetic cycle model, not RTL)
216 configurations, 12 policies/schedules/coalescing arms each (2592 runs); 96 discovery, 96 holdout, 24 wildcard (12.5% of 192 frozen configurations). 480/480 independent C++ integer-token timing/traffic comparisons agreed. Python numerical path checked final register states against glibc fmaf, one representative lane per wave, not Wave32 FMA RTL.

Holdout: coalesced-forwarding best-policy strict wins 36/96, >=5% wins 34/96, ties 60/96, losses 0 (best-of-policy oracle). By source multiplicity: 1x 20/32 strict, 2x 0/32, 3x 16/32. In 48/96 cases an apparent forwarding win over uncoalesced no-forward disappears when the baseline coalesces. Wildcard: 9/24 strict, 5/24 >=5%.

**KNOWN (model):** duplicate RF reads were unfairly charged in V142; coalescing corrects physical read count. **BELIEVED:** V-Tile RF collector should coalesce repeated source tags. **CONFLICTING:** no forwarding wins for 2x source multiplicity but wins for 1x and 3x in frozen workloads. **FALSIFIED:** per-logical-source RF reads as a fair baseline. **ANOMALOUS:** nonmonotonic 1x/2x/3x speedup boundary. **UNTESTED:** integrated RF+FP32, real workloads, mapped PPA, physical fanout energy.

**Prior art:** RF operand reuse and forwarding are established GPU microarchitecture techniques; no novelty claim. Source archive and full raw model results in local V143 reproducibility package. GitHub CI checks the independent abstract/RTL slice, not the full software cycle-model benchmark.

**Next decisive action:** integrate coalescer, V142 multicast capture, real FP32 FMA, and scoreboard into a complete V-Tile and run matched-resource kernel/PPA comparisons.
