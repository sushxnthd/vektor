# Exact uniform-bank headroom: independent deterministic enumeration (2026-11-19)

**Evidence tier:** exhaustive synthetic four-request bank-service arithmetic. This is not RTL, extracted-RC signoff, SRAM-macro integration, power, or measured GPU IPC.

## Method and reproducibility
Independent local Python enumeration (separate from the committed script) evaluated every ordered sequence of eight bank indices for B in {2,3,4}, grouping indices into four two-operand requests. Each bank has two read ports; all four requests are valid. Strict-order compact greedy admits each request only when both reads fit. An unfair oracle enumerates all 16 subsets and maximizes granted requests. The new independently implementable checker is `python research/v317/rtl/exact_uniform_bank_ceiling_20261119.py`. Its hosted execution has **not** been verified. No new physical route was run.

| Banks B | Exhaustive cases | Greedy grants sum | Oracle grants sum | Oracle-only extra grants | Exact oracle/greedy |
|---|---:|---:|---:|---:|---|
| 2 | 256 | 442 | 494 | 52 | 19/17 = 1.1176470588 |
| 3 | 6,561 | 14,391 | 15,435 | 1,044 | 1715/1599 = 1.0725453408 |
| 4 | 65,536 | 171,076 | 178,972 | 7,896 | 44743/42769 = 1.0461549253 |

For these exact distributions, the prospective *necessary* 2% materiality boundary under proportional service is `clock_ratio * occupancy_ratio >= 1.02 / (oracle/greedy)`: B=2 requires >=867/950 (~0.91263), B=3 requires >=81549/85750 (~0.950999), and B=4 requires >=2181219/2237150 (~0.9750). An independent bandwidth ceiling must also be >=1.02. Passing these necessary bounds **does not establish** a realizable hardware win.

## Scientific interpretation
These are **upper bounds**, not positive V317 mechanism measurements. The 4-bank exhaustive value 1.0461549 is close to but not identical with the prior seeded 4-bank Monte Carlo 1.046683, as expected from sampling variability; neither warrants physicality claims. This exact finite-bank stress test strengthens the small-bank candidate's *conditional* headroom while leaving the previously frozen uniform-16 no-win and hot65 conditional-win regimes untouched. The strong compact-greedy routed area counterexample (21,314.6 versus 21,324.7 um2) and both electrically illegal routes still falsify V317's positive tile claim. No V287 revival, no second active mechanism.

**Next discriminating gate:** legal matched compact-greedy/pairwise route with max-cap and hold repaired, then freeze clock/occupancy/bandwidth from those routes before applying any oracle service headroom. A real scheduling implementation must beat compact greedy at matched resource and physical legality; an unfair oracle cannot substitute for that implementation.
