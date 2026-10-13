# V150 SCIENCE ledger (2026-10-13)

**Active kernel:** Can a shared bounded general FMA finisher, combined with register-bank-aware scheduling, deliver a reproducible throughput/energy/area/timing Pareto improvement over the strongest equal-resource public GPU/FMA baseline?

- **Frontier:** V149 CLOSE-only RNE passed 3,072 supported vectors, but 0% of same-sign vector FMA and 12.72% of synthetic GEMM fragments were eligible. Public full-FMA implementations already exist (see V149 PRIOR_ART.md).
- **Exact measurable objective:** full binary32 RNE numerical correctness, plus accepted FMA/cycle, energy proxy, generic mapped area, path delay and broad workload coverage under matched RF ports and area.
- **Strongest equal-resource baseline:** an open full-FMA implementation (Vortex/Tachyum/ARCH HDL, after independent reproduction) with same lane count, ports, buffering and mapped cell library. Not yet established.
- **Mechanism hypothesis:** a bounded far/near finisher with selectively shared normalization may avoid a 555-bit exact-wide datapath; if cancellation-specialized hardware is worth keeping, its net area-normalized throughput benefit should correlate with cancellation frequency.
- **Quantitative prediction:** CLOSE-only eligibility is 0% for all-positive vector FMA; a general finisher covers 100% of finite inputs. Optional CLOSE bypass must exceed 5% throughput/energy benefit in a cancellation-heavy unseen workload, while causing <2% loss on broad workloads.
- **Decisive falsification:** bit mismatch/flag mismatch, a hardware cost increase not offset by >=5% benefit, or a holdout workload reversal outside the predicted cancellation-frequency regime.
- **Publishable threshold:** novel mechanism beyond established FMA architectures, frozen equal-budget benchmarks, independent checker, mapped PPA, unseen kernels, quantified mechanism law. NOT MET.
- **Architecture-relevance threshold:** complete FMA RTL path, >=10,000 independent bit-exact checks, same-resource benchmark and <=2% broad-workload regression before adding bypass to V-Tile.
- **Kill condition:** after three substantive runs without better numerical coverage, a mapped PPA boundary, or equal-budget performance evidence, retire the separate CLOSE bypass hypothesis.

**V150 experiment:** 555-bit exact-dyadic RTL correctness *reference*, not a GPU datapath candidate. Evidence class: locally generated exact software oracle checked against libc on finite inputs; HDL CI PENDING. A large reference does not establish novelty, throughput, energy or timing.

**Negative result preserved:** V149 cancellation-only architecture does not cover broad workloads. The next mechanism must optimize a *complete* general FMA, not another isolated CLOSE circuit.
