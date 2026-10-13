# V147 SCIENCE ledger — simulated bank-mapping crossover

Status: SOFTWARE SIMULATION, NOT NOVEL. 2026-10-13.

Active question: Can equal-capacity XOR RF bank indexing reduce full Wave32 FMA kernel cycles relative to low-bit indexing, and when do RAW dependencies or RF latency erase the benefit?

Frontier: V145 falsified fixed even/odd response partitioning; V146 collector has software-model validation but lacks V146-specific RTL/synthesis verification. XOR banking is established prior art.

Objective: minimize cycles for 64/128-instruction Wave32 FP32 FMA workloads, 16 banks (four registers/bank), two response buses, one collector, three-cycle FMA and identical writeback backpressure.

Equal-resource baseline: low-bit bank=(reg&15) versus XOR bank=((reg^(reg>>4))&15), each with 16 equally populated banks and identical response ports. XOR decoding/wiring costs are NOT measured. One-bus configuration is not an equal-resource Pareto baseline.

Hypothesis: bank concentration is on the critical path only for independent operand requests; RAW dependencies and RF latency can mask/reverse gains.

Predictions frozen before holdout: XOR improves independent bankhot by >=10%; dependent bankhot by <5%; regressions on chain, independent, divergent <2%. Final FP32 state must match sequential reference.

Discovery: 72 configurations (3 seeds x 6 workloads x 2 port counts x 2 mappings). Holdout: 120 configurations (5 unseen seeds x 6 workloads x 2 port counts x 2 mappings), 128 instructions/configuration, 432604 active-lane FMA evaluations. All completed with zero FP32 or final-state mismatches. Holdout XOR/low speedup with 2 ports: independent bankhot 1.2392x (range 1.2312-1.2524), dependent bankhot 0.9996x (0.9963-1.0018), chain/independent/divergent 1.000x, mixed 1.0032x (0.9980-1.0101).

Wildcard: 36 configurations, seed 271828, RF latency 1/4/8 and stall probability 0.08/0.25. Dependent bankhot XOR/low 1.136-1.167x at latency 4 but ~1.000x at latency 1. Independent bankhot benefit falls to ~1.089x at latency 8. Exploratory, not confirmatory.

Falsification: any arithmetic/retirement mismatch, unequal bank populations, or holdout crossover failure. Publishable threshold: novelty, strong open baseline, physically matched resources and unseen realistic kernels; NOT MET. Architecture relevance threshold: >=10% cycle gain with <=2% mapped-area and <=2% timing regression on unseen kernels; only simulated cycles meet threshold in one synthetic class. Kill condition: physical cost erases gain or realistic kernels lack this regime.

Uncertainty: model assumes one RF response/bank/cycle, 2 global buses, one instruction collector, two-slot FMA execution queue, no cache, physical wires, fetch or measured power. Masked lanes do not shorten FMA latency. V138's oracle was independently checked against 34000 glibc fmaf cases; this run compares full state to a sequential reference sharing the oracle. No independent complete cycle model or RTL test this run.

Next decisive experiment: independently reimplement RF response timing, synthesize low-bit/XOR bank decode and complete collector; integrate FMA RTL with scoreboard. Do not claim scientific novelty or RTX 5090 capability.
