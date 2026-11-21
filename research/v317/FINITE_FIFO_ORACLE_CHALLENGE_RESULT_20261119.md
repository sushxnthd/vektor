# Finite-FIFO oracle challenge: frozen prospective result (2026-11-19)

Protocol frozen **before** the evaluator at commit `2786a767a4506719d91482bc2ba706d124fb4d87`. Evaluator commit `886ae41df7aeaaff4a9f8b8144a23b8ca4270e8c`. The evaluator was executed in a local Python environment; reproduce with `python research/v317/rtl/finite_fifo_oracle_challenge_20261119.py`. Fifteen seed/case combinations; 2,000-cycle warmup, 20,000 measured cycles, FIFO capacity 16, four-request scheduling window, two reads/bank, independent identical arrival traces. Oracle selects a maximum-cardinality subset of the window; greedy scans in order. The oracle is **unfair, zero-cost, non-RTL** and can worsen oldest-request age. It is an optimistic theoretical comparator.

| Regime | Seeds | Oracle/greedy grants | Greedy drops -> oracle drops | Frozen >=1.02 gate |
|---|---|---|---|---|
| uniform 16-bank, 3 arrivals, 4 output | 11,29,47 | 1.000000, 1.000000, 1.000000 | 0 -> 0 for each | FAIL (predicted no-win) |
| uniform 4-bank, 3 arrivals, 4 output | 11,29,47 | 1.044265, 1.046928, 1.046535 | 9125->6873; 9114->6726; 9135->6768 | PASS (conditional oracle headroom) |
| 65%-hot 4-bank, 3 arrivals, 4 output | 11,29,47 | 1.004460, 1.001665, 1.000465 | 29956->29822; 29962->29912; 29916->29902 | **FAIL (conditional potential-win falsified)** |
| 65%-hot 4-bank, 3 arrivals, 2 output | 11,29,47 | 1.012871, 1.011093, 1.011055 | 30321->29939; 30342->30013; 30330->30002 | FAIL (bandwidth cap) |
| 65%-hot 4-bank, 1 arrival, 4 output | 11,29,47 | 1.000000, 1.000000, 1.000000 | 0->0 | FAIL (nonsaturated) |

The hot-bank **predicted potential-win regime failed** the materiality test in all three seeds despite previous independent-batch oracle ratios near 1.10x. The queue endogenously changes its head-of-line bank distribution under sustained contention. This is a strong counterexample to directly transferring a fixed independent-batch service ratio into a finite-buffer steady-state throughput bound. The queue is effectively full (mean occupancy ~16), and around half the incoming hot-bank requests are dropped. A conditional positive law therefore needs the **stationary scheduling-window distribution under each policy**, not only the exogenous bank probabilities. Oracle oldest-request age rose to 20–21 cycles versus 16 for greedy in the hot-bank case; no fairness claim is warranted.

**Caveats:** This is a small deterministic synthetic queue, not a physical scheduler, measured GPU IPC, or an independent external workload. The run used one Python implementation with inline port/capacity assertions, not a separate independent checker; its code and outputs still require hosted reproduction and adversarial audit. The frozen protocol's no-increased-drop condition is met, but this does not certify real-world performance. Equal-resource and electrical viability are NOT established. V317's compact-greedy area and electrical falsification remains binding (21,314.6 vs 21,324.7 um2, both illegal). Do not rehabilitate V317, relax the 2% threshold, or claim RTX-5090 equivalence.

**Next gate:** Independent FIFO accounting checker and held-out arrival distributions, then electrically legal matched RTL/route only if a realizable mechanism with a defensible benefit survives.
