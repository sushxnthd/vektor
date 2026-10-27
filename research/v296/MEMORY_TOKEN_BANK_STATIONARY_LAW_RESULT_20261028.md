# V296: finite shared-bandwidth admission law, prospective synthetic validation (2026-10-28)

**Evidence tier:** exact finite-state analytical model, independent small-resource enumeration, and prospective *synthetic* Monte Carlo. **Not GPU workload data, post-route timing, energy, or a V296-vs-serial speedup.**

## Preserved prospective order

1. [Frozen protocol](MEMORY_TOKEN_BANK_STATIONARY_LAW_PREREG_20261028.md) committed as \`7c577d27\` before evaluation.
2. [Executable exact-DP and independent direct-index reference](memory_token_bank_stationary.py) committed as \`70b81156\` before prospective synthetic seeds were evaluated. Small-resource exhaustive self-tests passed locally.
3. [Machine-readable 12-cell result](MEMORY_TOKEN_BANK_STATIONARY_LAW_RESULT_20261028.json) committed as \`bf44a1f7\`, with no fitted parameters, no seed/tolerance revisions, and sealed real-GPU holdouts untouched.

## Predictive boundary

For S priority slots, B banks, P ports/bank, independent valid probability p, within-wave same-bank operand-copy probability rho, refill r waves/cycle, bucket capacity K waves, let Q_t(k) be the **exact** probability of admitting k waves given t bandwidth tokens. Q is computed by a finite bank-load-histogram dynamic program that counts two read ports for a same-bank operand pair. The post-cycle token state x has transition

\[
P_{xy}=Q_{\min(K,x+r)}(\min(K,x+r)-y).
\]

The stationary distribution solves \(\pi P=\pi\), \(\sum_x\pi_x=1\). Predicted admission rate:

\[
\boxed{q(B,S,P,p,\rho,r,K)=\sum_x\pi_x\sum_k k\,Q_{\min(K,x+r)}(k).}
\]

By token conservation and validity, \(0\le q\le\min(Sp,r)\). This is an exact **model-law** under independent cycles and uniform bank sampling, not a measured architecture law. Because V296 and the strongest serial control admit exactly the same requests under identical resources, the model predicts **zero same-clock V296-vs-serial throughput gain**. Any future positive claim must additionally measure an independently feasible tile-clock or resource effect.

## Prospective test results

16 banks, four slots, two ports/bank, bucket capacity four, 100,000 cycles per seed (10,000 burn-in). Frozen unseen seeds 812731 and 812737; independent direct-index Monte Carlo, no fitted coefficients.

| Frozen regime | p | rho | Tokens/cycle | Exact predicted q | Maximum held-out absolute error |
|---|---:|---:|---:|---:|---:|
| Sparse, constrained | 0.25 | 0.0 | 1 | 0.907931 | 0.001565 |
| Uniform, constrained | 0.75 | 0.0 | 1 | 1.000000 | <0.000001 |
| Within-wave correlated, constrained | 0.75 | 0.5 | 1 | 1.000000 | <0.000001 |
| High within-wave correlation, constrained | 0.95 | 0.8 | 1 | 1.000000 | 0 |
| Uniform, less constrained | 0.75 | 0.0 | 3 | 2.787471 | 0.002060 |
| High within-wave correlation, less constrained | 0.95 | 0.8 | 3 | 2.984013 | 0.000298 |

**Frozen prospective gate: PASS, 12/12 cells**, max absolute error **0.002060 waves/cycle** against tolerance **0.035**. Independent direct-index exhaustive checks for B=2, S=2, P=2 at rho={0,0.3,1}, available tokens={0,1,2} agreed within 1e-12. Stationary residuals were <1e-10.

The original preregistration/code uses the shorthand \`hot_low_bw\` / \`hot_high_bw\`. **Those names do not denote a cross-wave hotspot**: rho is strictly *within-wave operand-copy probability* and the first operand bank is uniform in every case. Do not interpret these cells as a validation of hot-bank skew, temporal correlations, or real occupancy.

## Additional exploratory sensitivity, not prospective validation

At p=0.75, r=3, K=4, the exact model gives q=2.787471 for rho=0, q=2.678605 for rho=0.5, and q=2.715676 for rho=1. Thus within-wave operand reuse has a **nonmonotonic** admission effect in this finite-port model; naive monotonic reuse arguments are unsafe. These are analytical post-hoc sensitivity calculations, not held-out validation or a V296 advantage.

## Hard physical decision still outstanding

The [matched D4/D8 dynamic-RF extracted-RC experiment #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436) was **still in progress** at inspection: both frozen RTL-oracle jobs passed, all four matched physical jobs remained in progress, and no physical results artifact was available. Do not claim both contestants feasible. Preserve the original 3.5 ns, 2x RC, 25 ps hold, +50 ps setup, zero electrical/DRC violation, <=30,000 um² and equal-resource gates. A physical fail cannot be rescued by this synthetic law.

**Decision:** keep V296 as the sole provisional mechanism, V287 retired, one persistent branch and draft PR #13. This law sharpens the **bandwidth no-win boundary**, but does **not** meet the world-class completion gate. The next required evidence is both contestants' routed feasibility, followed by measured-clock, realistic RF/port/bandwidth/occupancy, power proxies and unseen external workloads. Kernellum PR #119 and its holdouts were not modified.
