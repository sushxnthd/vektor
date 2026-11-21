# Exact hot-bank service ceiling sensitivity (2026-11-19)

## Evidence tier and scope
Exploratory **exact enumeration**, executed locally before this report was committed. This sweep was **not preregistered** and is not a prospective holdout. It does not introduce a new architecture mechanism. It preserves the existing V317/V296 lineage and the V317 negative physical result.

Model: four ordered requests, two independently sampled operand bank IDs per request, four banks, two read ports per bank. A strict-order greedy policy is compared against an **unfair, zero-cost maximum-cardinality subset oracle**. All 4^8=65,536 ordered bank assignments are enumerated for each probability distribution with integer probability weights; ratios are reduced with exact rational arithmetic. The single hot bank has probability h; the other three banks share 1-h uniformly. All values below are rounded for display only.

| h | Oracle/greedy service ceiling | P(oracle improves) | E[greedy grants] |
|---|---:|---:|---:|
| 0.25 (uniform) | 1.046154925 | 0.120483398 | 2.610412598 |
| 0.50 | 1.072037336 | 0.161779835 | 2.245777606 |
| 0.65 | 1.106716567 | 0.194233509 | 1.820087678 |
| 0.75 | 1.119826101 | 0.181852783 | 1.517639160 |
| 0.875 | 1.080401350 | 0.094497785 | 1.175325849 |

**New bounded finding:** oracle relative service headroom is **non-monotone in hot-bank probability** on these five exact sampled points: it rises through h=0.75 then falls at h=0.875. The probability of an oracle improvement peaks earlier, at h=0.65 among these five points. Thus neither raw skew nor improvement probability alone is a sufficient monotone proxy for relative service gain. The exact identity is R = 1 + P(oracle>greedy) / E[greedy grants] in this four-request model, since the oracle can improve grants by at most one.

**Critical limitation:** This is a ceiling for an idealized, unfair oracle, not evidence that any finite-cost scheduler beats compact greedy. This enumeration does not establish an optimal skew value, prospective transfer, physical feasibility, fairness, throughput, GPU IPC, SRAM-macro integration, area or power. The historical compact-greedy whole-RF-proxy area dominance and electrical violations remain binding. Do not interpret h=0.75 as a post hoc winning workload or change the previously frozen h=0.65 candidate regime.

Reproduction: `python3 research/v317/rtl/exact_weighted_hot_bank_ceiling_20261119.py`. No dependencies beyond Python standard library. Source commit: `9f7db19e8174ec73c635b729991f9c957afb860c`.

**Next decisive gate:** preregister held-out skew points and finite-buffer bandwidth/occupancy regimes *before* observing their results, then require a legal matched compact-greedy physical implementation before any positive tile claim. The exact oracle alone cannot clear the gate.
