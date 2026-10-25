# V296: bank-hotspot falsification of the uniform occupancy law (2026-10-25)

**Evidence tier:** exact rational analysis for a declared independent-slot traffic family, independently checked against concrete per-bank enumeration and deterministic synthetic sampling. **Not a measured GPU workload, measured tile clock, physical power, or architecture speedup.**

## Decision

The previous uniform-bank law must **not** be extrapolated to skewed register-bank traffic using only bank count, validity, and same-bank correlation. It can overpredict admitted work by more than 100% relative to the skewed workload in the most concentrated synthetic case below. A generalized, class-weighted exact law survives for the explicitly independent-request model. V296 remains the sole provisional mechanism, and V287 remains retired. The prospective real-workload holdouts remain sealed.

## Predictive positive boundary and independent implementation

Partition banks into classes c, each containing n_c banks with individual selection probability w_c, where sum_c n_c w_c = 1. Each slot is valid with probability p. Its first bank A follows w; its second bank B equals A with probability rho and otherwise follows an independent draw from w. Each accepted request consumes two read ports; requests are processed greedily in slot order.

Let h_(c,l) count class-c banks currently using l of P read ports. Define

- U(h) = sum_(c,l<P) h_(c,l) w_c, the total probability of choosing a bank with at least one port free.
- D(h) = sum_(c,l<P-1) h_(c,l) w_c, the probability of choosing a bank with two ports free.
- L(h) = sum_c h_(c,P-1) w_c^2, the probability mass correction for selecting the **same** bank when only one port remains.

Then the exact next-valid-request compatibility is

```
C(h) = rho * D(h) + (1-rho) * (U(h)^2 - L(h))
Pr(admit next slot | h) = p * C(h)
q = sum_(t=0 to S-1) p * E[C(h_t)]
```

A rational dynamic program tracks histograms by class and read-port occupancy. A separate oracle enumerates **concrete bank-index traces**, not histograms, on four small configurations; all match exactly. Independent sampling checks three larger synthetic skewed cases (50,000 cycles each). A per-state closed-form compatibility identity and exact probability-mass conservation are also checked.

The law is not new GPU architecture mathematics. Its scientific use is to supply a falsifiable workload boundary and expose an important failure of an overly simplified model. It cannot distinguish V296 from serial one-hot at equal resources and clock because both have the same greedy acceptance semantics.

## Frozen synthetic skew sweep

Nominal: 16 banks, four ordered issue slots, two read ports per bank, p=0.8, rho=0.2. One designated hot bank has probability h; each of the other 15 banks has probability (1-h)/15. These are synthetic, **not** measured bank-request distributions.

| Hot-bank probability h | Exact q, admissions/cycle | Error if uniform q=2.992340 is reused, relative to true q |
|---:|---:|---:|
| 0.0625 (uniform) | 2.992340 | 0.00% |
| 0.125 | 2.973380 | +0.64% |
| 0.25 | 2.820104 | +6.11% |
| 0.50 | 2.194698 | +36.34% |
| 0.75 | 1.473656 | +103.06% |

This is a **falsification of uniform extrapolation**, not of the generalized weighted law.

### Stronger controlled counterexample: equal actual operand-bank overlap

The actual same-bank probability is `rho+(1-rho)*sum_i w_i^2`, which changes under skew even when rho is held fixed. To isolate this confound, set the **actual** same-bank probability to exactly 0.5 in each configuration by adjusting rho.

| Hot-bank probability | rho needed to hold actual overlap at 0.5 | Exact admitted waves/cycle |
|---:|---:|---:|
| 0.0625 | 7/15 | 2.911052 |
| 0.25 | 4/9 | 2.758033 |
| 0.50 | 7/22 | 2.195945 |

Thus even **equal bank count, read ports, offered occupancy, and actual operand-bank overlap** are insufficient to predict q without information about bank-selection skew. The hot-bank case loses 24.57% of admissions relative to the uniform case at matched actual overlap. A scalar compatibility/overlap summary is not a sufficient statistic for this workload family.

### Independent validation

Concrete-bank exhaustive oracle matches the exact class-histogram DP on four small cases. Synthetic independent samples:

| Hot probability | Exact q | 50,000-cycle independent sample | Absolute error |
|---:|---:|---:|---:|
| 0.25 | 2.820104 | 2.823900 | 0.003796 |
| 0.50 | 2.194698 | 2.195200 | 0.000502 |
| 0.75 | 1.473656 | 1.470420 | 0.003236 |

All discrepancies are below the conservative 99.9% Hoeffding bound 0.034874 for observations in [0,4]. This is a **synthetic-model consistency check**, not an empirical GPU holdout test.

## Tile consequence and falsification gates

The conditional bandwidth threshold `Wcrit = b*q / Tserial` changes with bank skew. For illustrative b=4 B/wave and controller-path proxy Tserial=3.427697 ns, it decreases from **3.491954 GB/s** at uniform traffic to **1.719704 GB/s** at h=0.75. Both are **model predictions**; neither is measured sustained GPU bandwidth. At equal integrated tile clock and overhead, V296's issue-throughput advantage remains **exactly zero**, regardless of this skew.

The controller physical result still has the separate, narrow evidence tier of matched post-CTS area/timing against a feasible serial one-hot control. No GPU-tile Fmax or performance improvement follows from it without integration.

**Next required falsifier:** Before examining prospective held-out bank traces, freeze a bank-frequency estimator, effective per-request correlation estimator, and prediction interval; then use independent trace playback to compare this weighted law, the original uniform law, and a strong empirical baseline under nonuniform, time-correlated, scheduler-dependent requests. Measure the same RTL trace against serial one-hot, and reject any performance claim if the equal-resource integrated tile clock or bandwidth does not improve. Equal-consumed-area reinvestment, power and physical replication remain open.

Reproduce with `python3 research/v296/class_weighted_bank_skew_law.py --self-test` and `python3 research/v296/class_weighted_bank_skew_law.py`. No prior holdout was opened or modified.
