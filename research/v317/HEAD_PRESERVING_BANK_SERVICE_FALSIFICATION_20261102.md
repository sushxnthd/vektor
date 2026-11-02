# V317: age-head-preserving bank-service oracle falsifies the hot-bank positive regime (2026-11-02)

## Evidence and prospective ordering
The protocol [FROZEN_HEAD_PRESERVING_BANK_SERVICE_20261102.md](FROZEN_HEAD_PRESERVING_BANK_SERVICE_20261102.md) was committed at `7544eecd` **before** the evaluator, checker or outcomes. The primary evaluator is [head_preserving_oracle.py](rtl/head_preserving_oracle.py); the independent recursive checker is [audit_head_preserving_oracle.py](rtl/audit_head_preserving_oracle.py); raw [JSON results](HEAD_PRESERVING_BANK_SERVICE_RESULT_20261102.json) are preserved. Local execution passed independent exhaustive B=2 (256 operand tuples), B=4 (65,536 tuples), and separately seeded 2,000-case holdouts per stochastic regime. Hosted reproduction is configured in [v317-head-preserving-oracle.yml](../../.github/workflows/v317-head-preserving-oracle.yml); do not claim hosted success before the run completes.

## Main result: the unconstrained hot-bank win depends on bypassing the oldest request

| Four-slot, 2-read-port/bank regime | Compact greedy grants | Head-preserving oracle grants | Unrestricted oracle grants | Head/greedy | Unrestricted/greedy |
|---|---:|---:|---:|---:|---:|
| Uniform 16 banks, K=4 | 114,787 | 114,829 | 114,915 | 1.000366x | 1.001115x |
| Uniform 4 banks, K=4 | 78,167 | 79,310 | 81,709 | 1.014623x | 1.045313x |
| 65% hot bank, 16 banks, K=4 | 57,413 | 57,706 | 63,206 | **1.005103x** | **1.100900x** |
| 65% hot bank, 16 banks, K=2 | 50,262 | 50,262 | 54,887 | **1.000000x** | 1.092018x |
| 70% same-bank operands, 16 banks, K=4 | 106,093 | 106,142 | 106,311 | 1.000462x | 1.002055x |

Each sampled row comprises 30,000 independent, backlogged *instantaneous* batches (three frozen seeds × 10,000). These are not queueing workloads or GPU IPC measurements.

**Prospective decision:** uniform16 no-win prediction **passes** (<1.02x); hot65 candidate win prediction **FAILS** (1.005103x <1.02x); hot65 K=2 no-win prediction **passes** (1.000000x). No post-hoc threshold change. Under the hot-bank workload, preserving the oldest request removes `(63,206-57,706)/(63,206-57,413) = 94.94%` of the unconstrained oracle's incremental grant headroom. A hot-bank oracle can look like a 10.09% service win while an age-head-preserving version has only 0.51% optimistic headroom.

The constructed adversarial head blocker `[(0,1),(0,0),(1,1),(2,2)]` gives greedy=2, head-preserving=2, unrestricted=3; its celebrated 1.5x theoretical win requires dropping the oldest request. The disjoint control gives 4/4/4.

## Exhaustive distribution check
For **all** 4^8=65,536 four-request tuples over four banks (each of eight operand banks independently ranging 0..3), compact greedy grants 171,076, head-preserving grants 173,572, unrestricted grants 178,972: **1.014590x vs 1.046155x**. The independent recursive checker reproduced all three totals exactly. For two banks, 256 exhaustive tuples give 442/442/494: **zero** head-preserving advantage despite an 11.76% unrestricted oracle advantage. These are exact combinational results under the stated model.

## Compact positive boundary, and its limits
For any sampled distribution with greedy grants G and head-preserving optimal grants H, and output cap K applied after bank admission,

```
R_head(K) = E[min(K,H)] / E[min(K,G)]
          = 1 + E[min(K,H)-min(K,G)] / E[min(K,G)].
```

This is an exact **accounting identity**, not a fitted predictive mechanism. In the frozen four-slot experiments the head-preserving gain is at most one grant per batch; for the sampled regimes the positive event probability and denominator are recorded in the JSON. A physically useful predictive law would need to estimate the event probability from bank correlations, occupancy, output pressure and age constraints **before** observing outcomes, then survive unseen queueing workloads and physical timing.

## Physical and novelty decisions
- **Do not promote an unrestricted oracle to an architecture mechanism.** It can bypass the oldest request; even head preservation alone is **not** starvation freedom, since younger slots may repeatedly bypass the second-oldest.
- **Do not revive V317**: its earlier same-policy compact greedy physical baseline is smaller (21,314.6 vs 21,324.7 um²) and both integrated RF-proxy routes are electrically illegal. No change to the frozen 2% area gate.
- **Do not claim** any GPU throughput, SRAM-macro integration, power advantage, real workload gain, or RTX 5090 equivalence.
- The strongest next kill test, before committing RTL for a new service mechanism, is a **finite-buffer, strict-age or bounded-wait scheduler** with realistic bank skew, output saturation and bank-service latency, compared against a competent same-resource baseline. The 65%-hot-bank prospective win hypothesis is rejected; no new active mechanism has been promoted.

## Reproduction

```sh
python3 research/v317/rtl/head_preserving_oracle.py > head_results.json
python3 research/v317/rtl/audit_head_preserving_oracle.py head_results.json
```

The independent checker uses a separate recursive search rather than importing the evaluator. This remains an algorithmic audit, not an independent silicon/EDA signoff.
