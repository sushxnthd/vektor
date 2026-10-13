# V152 SCIENCE ledger — balanced leading-one test

**One active kernel:** Can balanced leading-one selection reduce the critical combinational depth of V151's exact FP32 bounded finisher without increasing generic synthesis area enough to erase the benefit, while preserving every bit and flag?

- **Frontier/best-known:** V151 64-bit bounded signed-tail RNE RTL passes 24,220 vectors and reports 383 generic path levels; no mapped PPA. Parallel priority encoders/leading-zero detectors are established prior art. No novelty assumed.
- **Exact objective:** bit-exact match on frozen V151 oracle corpus and baseline, followed by same-tool generic cell count and longest topological path. Follow with technology-mapped area-delay and equal-throughput tests.
- **Strongest equal-resource baseline:** unmodified V151 finisher, identical I/O, 64-bit window, lane count, synthesis tool, and vector corpus. External CVFPU/HardFloat comparisons remain required before any competitive claim.
- **Mechanism hypothesis:** three serial leading-bit overwrite loops (48,24,65 candidates) induce priority selection. A seven-stage binary search should shorten the leading-one portion, possibly exposing a different critical path. The new topology may cost extra mux area.
- **Quantitative prediction:** identical outputs for all tested inputs; generic longest path <383 levels if priority encoding dominates. Predict no workload IPC gain until the datapath is registered; throughput improvement is NOT claimed.
- **Decisive falsification:** any differential mismatch, or no reduction in generic depth at matched RTL interfaces; synthesis growth large enough to prevent mapped area-delay improvement.
- **Publishable threshold:** >=5% mapped area-normalized throughput improvement over a strong public equal-resource FMA, independently checked on unseen workloads, plus demonstrated novel mechanism beyond known priority encoders. Current hypothesis is not novel.
- **Architecture relevance threshold:** a >=10% reduction in mapped critical delay at <=5% area overhead, or demonstrably useful pipeline-stage partitioning for the Wave32 FP32 tile.
- **Kill condition:** after three substantive tests without a new physical gate, informative boundary, or architectural improvement, terminate leading-one optimization and prioritize register insertion / scoreboard integration.

**Evidence class:** V151 historical RTL/synthesis PASS; V152 pending GitHub CI. Python independent 565,536 leading-one comparisons passed locally, but do not substitute for HDL. Preserve failing gates and logs.
