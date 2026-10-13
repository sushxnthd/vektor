# V144 SCIENCE — 2026-10-13

**Active kernel:** Does completion-first RF response arbitration outperform a work-conserving oldest-ready policy at equal resources? Which RF response bandwidth/latency regimes affect FP32 FMA completion?

**Frontier:** V143 found large synthetic one-bus serialization losses and a 115x generic-cell spread between its single and triple response implementations. No physical PPA.
**Objective:** minimum simulated cycles with identical final FP32 state, two global response slots, one return per bank, identical RF ports, collectors, issue width and waves.
**Strongest equal-resource baseline:** oldest-ready scan over all due responses, duplicate-read coalescing, two KPX instruction schedules.
**Mechanism:** completion-first priority could release collectors earlier; response bandwidth should matter at low latency, bank return duplication only at bank hot spots.
**Decisive falsification:** <5% improvement on holdout or significant regressions.
**Publishable success threshold:** new prior-art-distinct mechanism, realistic unseen workloads, equal-area/energy comparisons, independent cycle replication and physical proxy. NOT MET.
**Architecture threshold:** >=5% on two unseen kernel families at unchanged resources without material regression. NOT MET.
**Kill condition:** stop completion-first scheduling unless a qualitatively new >=5% regime appears.

**Synthetic cycle-model evidence (not hardware):** 240 discovery, 240 holdout, 48 wildcard cases; five FMA families, 4 waves, 2/4/8 collectors, RF latency 1/3, read ports 1/2, grouped/interleaved, seed 1445090. Arithmetic uses glibc fmaf on ONE representative lane/wave. Discovery 4 wins / 8 losses / 228 ties; holdout 6 / 5 / 229; wildcard 3 / 6 / 39. Zero >=5% wins in all three. Holdout speedup range 0.995885x–1.002899x. All policies matched sequential final FP32 registers.

**Selector replication:** 7,290 exhaustive bank/ready/bus/policy cases satisfied capacity, work conservation, no same-bank double-grant; independent C++ matched all Python grants. Not an independent cycle-model replication.

**Exploratory topology sweep (NOT equal hardware):** 180 model runs, 5 families x 3 latencies x 2 schedules x 4 response widths x 3 bank caps. Better of two schedules selected as oracle. One to two global buses: mean 1.6976x, 13/15 family-latency combinations >=5%, range 1–1.9931x. Two to three buses: mean 1.2081x, range 1–1.4948x. At two global buses, doubling bank return cap: mean 1.0036x, maximum 1.0204x, no >=5% improvements. Accumulator latency 1: 578/290/209 modeled cycles for 1/2/3 buses. At latency 6: 583/391/349. Triple-duplicate FMA latency 3/6: 1 and 2 buses tie.

**KNOWN (model):** global response bandwidth limits some workloads. **BELIEVED:** two-response hardware deserves synthesis. **CONFLICTING:** duplicate high-latency regimes do not benefit. **FALSIFIED:** completion-first has >=5% general advantage. **ANOMALOUS:** operand multiplicity changes crossover. **UNTESTED:** real kernels, full tile, mapped area/timing, energy, novelty.

**Residual:** predicted collector-release gains did not materialize; most configurations tied. Possible explanation: no collector pressure or too few completion-choice opportunities.

**Prior art:** register banks, operand reuse, arbitration and multicast are established. No scientific novelty claim.

**Next decisive action:** RTL test and generic Yosys cost for single/dual/triple Wave32 response networks, followed by area-equalized real FP32 tile comparison.
