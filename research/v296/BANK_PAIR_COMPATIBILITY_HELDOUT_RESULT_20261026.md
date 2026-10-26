# V296 bank-port compatibility: exact law and prospective holdout result (2026-10-26)

**Evidence tier:** Exact analytical two-request compatibility, independently enumerated and checked on synthetic heldout RNG streams. **Not** a V296 GPU speedup, not a complete 4-slot scheduler throughput law, and not a routed physical result.

## Provenance and freeze

The [protocol](BANK_PAIR_COMPATIBILITY_PREREG_20261026.md) was committed at `ff6b088ab901a88e7751b5abdf0435916af0bae1` before evaluating prospective seeds 424243, 515151, 616161. Pilot seeds 271828, 314159, 161803 were examined before the protocol and excluded. The exact law, five (hotspot, operand-copy) regimes, 50,000 samples per seed/regime, independent exhaustive 16^4 reference, and per-cell acceptance tolerance were frozen. The [reproducible code](bank_pair_compatibility_law.py) was committed at `72fc6ed2f72a9cd2569ae7183e0b3dc19cb4fd1d` before these holdouts were evaluated.

The law uses a fixed 16-bank, two-port/bank resource model. For independent two-read requests with bank distribution p and intra-request copy probability rho, define q_ab=p_a(rho*[a=b]+(1-rho)*p_b), d_a=q_aa. Then

`P_compatible = sum_a d_a*(1-p_a)*(rho+(1-rho)*(1-p_a)) + sum_(a!=b) q_ab*(1-d_a-d_b)`.

The derivation partitions the first request into same-bank (second must avoid that bank entirely) and distinct-bank (second may not consume two additional reads on either of those banks). No parameters are fitted. The independently implemented brute-force reference explicitly counts bank demands across all 65,536 quadruples; agreement was <1e-10 for all frozen regimes and edge cases.

## Prospective synthetic holdout (15/15 cells within frozen tolerance)

| Regime (hotspot h, copy rho) | Exact P_compatible | Empirical seeds 424243 / 515151 / 616161 | Largest absolute error | Frozen tolerance |
|---|---:|---|---:|---:|
| Uniform independent (0, 0) | 0.985107 | 0.98476 / 0.98556 / 0.98508 | 0.000453 | 0.005000 |
| Uniform correlated (0, 0.7) | 0.917175 | 0.91490 / 0.91784 / 0.91696 | 0.002275 | 0.006163 |
| Moderate hotspot (0.45, 0.2) | 0.678208 | 0.67970 / 0.67622 / 0.67624 | 0.001988 | 0.010446 |
| Heavy hotspot (0.80, 0.2) | 0.184699 | 0.18610 / 0.18474 / 0.18672 | 0.002021 | 0.008677 |
| Extreme hotspot (0.95, 0.7) | 0.066347 | 0.06666 / 0.06452 / 0.06796 | 0.001827 | 0.005565 |

The exact two-request compatibility probability falls from **98.51%** for uniform independent operands to **6.63%** for the extreme-hotspot/correlated regime. For precisely two ready requests and a greedy first-then-second grant, the expected issue count is `1+P_compatible`, conditional on the model. The corresponding values are 1.9851 and 1.0663 instructions per two-request opportunity, **not** the throughput of the V296 or serial 4-slot architectures.

**Reproduction:**

```bash
python3 research/v296/bank_pair_compatibility_law.py --self-test
python3 research/v296/bank_pair_compatibility_law.py --evaluate --output research/v296/BANK_PAIR_COMPATIBILITY_HELDOUT_20261026.json
```

Local execution of the frozen equations and prospective RNG streams passed. Hosted execution of the newly committed script has not yet been independently verified. The script writes all 15 raw rows and fail-closed per-cell decisions as JSON. This report preserves the observed results, not a physical artifact.

## Mechanistic implication and strict limit

The diagnostic quantifies one *necessary* input to an architecture-level positive law: the probability that two independently ready warp requests can coexist under bank-port pressure. It explains why extra nominal issue slots can fail to increase throughput when bank demand is skewed. It is a classical combinatorial resource calculation, **not** a novel GPU arbitration mechanism. A complete V296-vs-strongest-serial law still needs scheduler occupancy, latency, actual request ordering, mask/operand compatibility where applicable, physical feasible clocks, and shared bandwidth.

The existing matched decoded post-CTS experiment [40359299905](https://github.com/sushxnthd/vektor/actions/runs/40359299905) remains the immediate kill gate. If V296 fails +50 ps routed setup, nonnegative hold, zero cap/slew/DRC, or full routing, reject the decoded repair despite this correct sub-law. The serial fifth-stage control, replicated equal-resource tile, unseen GPU-workload predictions, and power proxies remain outstanding. V296 remains sole provisional mechanism; V287 retired. Kernellum PR #119 and its sealed holdouts are unchanged.
