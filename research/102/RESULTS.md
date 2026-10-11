# Vektor-102: joint divergence, RF-bank and memory-service discrimination
2026-10-11. **SIMULATED serialized service slots only**: no GPU cycle-level timing, RTL, synthesis, silicon, energy, novelty or 5090-class gate advancement.

## Claim -> implementation -> experiment -> measurement
Claim: regrouping masked SIMT lanes can lose its issue-group savings when 32-lane groups overload banked register-file service, incur migration overhead, or alter memory transactions.
Implementation: joint_cost.py compares equal-resource IPDOM, DWF-like regrouping, coarse static-length-8 heuristic, and a perfect-information oracle. Per-group service = sum over instructions of max(1, ceil(max RF-bank reads / RF ports), ceil(unique 128-byte lines / memory ports) for memory ops). Compaction pays setup + ceil(moved lanes / migration bandwidth). This is NOT a GPU cycle model; overlap, caches and physical implementation are absent.

Preregistered discovery (256): unconditional compaction **110 wins / 146 losses / 0 ties**. Median baseline/compaction service ratio 0.9859. Coarse heuristic regressed in 82/256. Its mean speedup of 1.300 is unweighted and should not be interpreted as a real workload throughput gain.
Minimally guided probes (32/256 = 12.5%): 10 wins / 19 losses / 3 ties.
Independent random holdout (96, seed 9102): 39 wins / 53 losses / 4 ties; 36 heuristic regressions. Median speedup 0.9872. These are unseen *model configurations*, not external benchmarks.
Independent C++ replication: **256/256 exact integer cost-vector matches** across IPDOM, DWF, heuristic and oracle. Six Python unit tests pass. Logical lane work and RF reads are conserved across policies.

## Predictions, residuals and mechanism
P1 coherent setup positive -> 0 compaction wins among 64 (PASS). P2 both wins/losses (PASS). P3 increasing RF ports never raises absolute service slots (zero violations across 128 controlled pairs, both policies). P4 oracle never loses, heuristic can regress (PASS, 82). P5 controlled sign reversals (PASS, 18 region-length and 2 memory-density pairs).
Balanced branch, 8 warps, length 16, no memory, 16 banks, migration bandwidth 8, setup 4: 2 RF reads/bank service capacity gives IPDOM 256 vs compacted 276 (0.928 ratio); 4 ports gives IPDOM 256 vs compacted 148 (1.730 ratio). A compacted group demands 4 reads/bank while a masked 16-lane group demands 2. The discontinuity is due to the *modeled* RF bank service boundary, not extra hardware given to compaction.
The preregistered follow-up predicts loss for <=3 RF ports and win for >=4, for unseen 12/24 instruction lengths, 8/16 warps and 4/8-warp windows. **56/56 direction predictions passed**, zero sign residual. A bookkeeping error in the prereg text says 16 combinations per category; the actual Cartesian product is 8 contexts x 7 ports = 56. Preserve this error in the record.
Posthoc anomaly: 4-path, 16-instruction, 2-port case changes from 1.803 baseline/compaction ratio (linear bank hash) to 0.948 (lane bank mapping). This **falsifies generalization across bank mappings**. The balanced-case threshold across several mappings is not independent proof because the path pattern is regular.

## World model (Discovery Protocol V2)
- KNOWN: software conservation and independent replication; 56/56 within-model sign predictions; oracle lower bound.
- BELIEVED: RF pressure, register migration and memory locality must be co-modeled before implementing cohort compaction.
- CONFLICTING: large gains on some long multi-path regions versus majority losses across both discovery and holdout; means obscure the reversals.
- FALSIFIED: unconditional compaction always pays; mask-only static length-8 heuristic is safe; one RF bank mapping supports general performance conclusions.
- ANOMALOUS: bank mapping flips the result; 18 region-length and 2 memory-density sign reversals.
- UNTESTED: real KPX/Vortex traces, RF layout, compiler register renumbering, operand cache disruption, occupancy, memory latency overlap, area, frequency, power and energy.

Adversarial roles: Explorer proposes RF-aware gating; Skeptic flags serialized-service assumption and synthetic hash; Experimentalist requests cycle-model integration; Analyst refuses to interpret service ratios as GPU speedup; Anomaly Hunter prioritizes mapping reversals; Prior-Art Auditor closes generic DWF/RF banking novelty; Replicator confirms 256 exact C++ comparisons but not independent cycle simulation; Theorist identifies the profitability inequality: saved IPDOM service > extra compacted service + setup/migration cost.

**Single next decisive action:** integrate realistic bank conflicts, migration and cache disruption into existing V-Tile cycle simulator, then compare equal-budget IPDOM/DWF/RF-aware heuristics on Vortex-compatible register/address traces. Continue Vektor-101 return-fabric formal verification in parallel.
