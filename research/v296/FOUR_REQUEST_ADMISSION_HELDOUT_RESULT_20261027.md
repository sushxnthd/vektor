# V296 exact four-request admission law: prospective synthetic result (2026-10-27)

**Evidence tier:** Exact analytical resource model plus independently sampled prospective synthetic holdouts. **Not** GPU performance, V296 speedup, or routed electrical closure.

## Provenance and protocol
- Preregistration commit `873c0b3e397ab6421dcadf680ad3773ed5c83e03` fixed 5 regimes, 3 unopened seeds, 30,000 four-request batches per cell, and absolute admission-rate tolerance 0.025.
- Implementation commit `6446f84d9ede806206f14b97f8187c325e20badb` preserved the exact recurrence and independent event-level simulator **before** heldout evaluation.
- Reproduce: `python3 research/v296/four_request_admission_law.py --self-test --evaluate --output research/v296/FOUR_REQUEST_ADMISSION_HELDOUT_20261027.json`. Local evaluation completed 2026-10-27; all 15 preregistered cells passed.
- Independent oracle checks the K=2 identity against exhaustive 16^4 operand combinations. Explicit event simulator uses a 16-entry remaining-port array; predictor uses only compressed port-occupancy counts, no simulation observations or fitted parameters.

## Positive predictive boundary law
Let each request draw two operand banks (a,b) with distribution `Pr(a,b)=p[a]*(rho*1[a=b]+(1-rho)*p[b])`. A fixed-priority admission consumes one read port per operand on each of 16 banks, two ports per bank. Define `S=(u_hot,n0,n1,n2)`, where `u_hot` is the hot bank's used ports and `n_j` counts cold banks with j used ports. For independent ready requests, propagate exact state probabilities by

`Pr(S_{t+1}=s') = sum_s Pr(S_t=s) sum_{a,b} Pr(a,b) 1[T(s,a,b)=s']`

where `T` consumes both reads if both fit, otherwise leaves the state unchanged. Then

`E[A_K] = sum_{t=0}^{K-1} sum_s Pr(S_t=s) sum_{a,b} Pr(a,b) 1[request admitted from s]`.

The recurrence is **exact under its assumptions** and contains no learned parameters. K=2 reduces to `E[A_2]=1+Pr(two requests compatible)`. It extends the existing compatibility sub-law to four competing requests without assuming pairwise probabilities add linearly.

## Frozen holdout results
| Frozen regime | Exact predicted admissions / 4 | Mean independent observed / 4 | Worst error among 3 seeds | Naive 1+3Ppair |
|---|---:|---:|---:|---:|
| Uniform, independent operands | 3.822723 | 3.825333 | 0.005410 | 3.955322 |
| Uniform, correlated operands | 3.534976 | 3.537244 | 0.005824 | 3.751526 |
| Moderate hotspot | 2.593159 | 2.592856 | 0.007759 | 3.034625 |
| Heavy hotspot | 1.402285 | 1.401856 | 0.000552 | 1.554096 |
| Extreme hotspot, correlated operands | 1.135374 | 1.135567 | 0.002293 | 1.199040 |

- **15/15 prospective cells pass**, worst absolute prediction error **0.007760 admissions per four-request batch**, below frozen tolerance 0.025.
- Across the 15 cells, mean absolute error is **0.002374** for the exact recurrence versus **0.200351** for naive pairwise extrapolation. This is a synthetic comparison, not an architecture performance result.
- Heavy bank pressure reduces expected admissions from 3.823 to 1.135 per four ready requests. A high pairwise compatibility probability does not justify scaling that probability linearly to four-way admission.
- Sample means are deterministic for the published seeds; they are **not** hardware measurements or an uncertainty bound for real workloads.

## Interpretation and hard stop
This strengthens V296's resource-pressure predictor, **not its novelty claim**: it is classical finite-state probability applied to the existing 16-bank/two-port model. It does not distinguish V296 from a functionally equivalent strongest serial arbiter at identical resources, latency and clock. A V296 benefit still requires a **physically feasible** clock/area/tile advantage that survives dependency latency, occupancy, bandwidth, and energy effects.

The decoded matched post-CTS extracted-RC run 40359299905 was still executing both contestants at the last check. Do not treat intermediate +0.206 ps pre-CTS guard margin as routed closure. If routed setup/hold/cap/slew/DRC fails the frozen gate, reject this decoder repair regardless of these synthetic results. V287 remains retired, V296 the sole provisional mechanism; real workload holdouts and Kernellum PR #119 remain untouched.
