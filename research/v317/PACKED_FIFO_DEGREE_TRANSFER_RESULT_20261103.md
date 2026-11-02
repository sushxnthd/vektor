# V317 packed-FIFO validity confound and unseen four-bank transfer (2026-11-03)

**Evidence tier:** synthetic combinational scheduling cardinality; NOT finite-buffer throughput, mapped PPA, routed timing/electrical signoff, GPU IPC or an RTX 5090 result. [Protocol](FROZEN_PACKED_FIFO_DEGREE_TRANSFER_20261103.md) committed at `8a0972c` **before** the four-bank holdout. The prior three-bank enumeration is a retrospective reanalysis, not a fresh holdout. The independent checker passed locally, with hosted reproduction pending.

## The exact structural no-win law

Four slots, two operand reads per request, two ports per bank, mandatory oldest request when valid, and output capacity K. For **head-valid K<=2**, any work-conserving sequential selector first serves the head and, if there is any compatible second request, finds one. Consequently

`G_greedy = G_degree = G_exact` for K<=2 and a valid head.

This is a cardinality result, **not** an equality of selected request identities or future queue behavior. It does not apply to head-invalid masks or to selectors that decline feasible requests. Independently, with B banks and P=2 read ports per bank, two charged reads per admitted request imply `G<=min(K,B)`; thus B=3 cap-3 and cap-4 snapshots coincide.

For cap>=3 in this four-slot model, the measured service identity is

`R_degree/greedy = 1 + (p_plus - p_minus) / E[G_greedy]`,

where `p_plus` and `p_minus` are probabilities that degree grants exactly one more or one fewer than greedy. This is a decomposition of observed grant counts, **not yet a mechanistic pre-outcome predictor** of these probabilities. The K<=2 boundary is predictive and exact.

## Retrospective exhaustive B=3 mask audit

The previous aggregate used **all 16 valid masks**, including invalid oldest slots and holes impossible in a packed FIFO. Each of 6,561 eight-operand bank assignments was evaluated under all 16 masks, two ports per bank.

| K | Valid-mask population | Greedy grants | Degree grants | Relative gain |
|---|---|---:|---:|---:|
| 2 | All 16 masks | 153,477 | 153,585 | +0.07037% |
| 2 | Head valid (8 masks) | 88,758 | 88,758 | **0%** |
| 2 | Packed FIFO prefixes (4 masks) | 42,426 | 42,426 | **0%** |
| 3 | All 16 masks | 158,409 | 158,529 | +0.07575% |
| 3 | Head valid (8 masks) | 92,880 | 92,892 | +0.01292% |
| 3 | Packed FIFO prefixes (4 masks) | 44,928 | 44,940 | +0.02671% |
| 3 | All four requests valid | 14,391 | 14,403 | +0.08339% |

At K=3, **108 of the 120 net extra grants (90%) arise from head-invalid masks**. In the head-valid subset, degree wins 108 cases and loses 96. This is an eligibility-distribution confound in the original 0.0758% average, not a universal proof that degree is worse. K=4 is identical to K=3 for B=3 by the bank-port capacity ceiling.

## Prospective unseen B=4 uniform operand holdout

Frozen seeds 191, 409, 733, 40,000 independent four-request vectors per seed, all four requests valid, bank IDs uniform on 0..3, two reads/request, two ports/bank. No seed/threshold changes after opening. The K=3 and K=4 prediction was degree/greedy **<1.005x**, and K=2 exactly 1.0x.

| K | Greedy | Degree | Exact-head oracle | Degree/greedy | Frozen test |
|---|---:|---:|---:|---:|---|
| 2 | 237,352 | 237,352 | 237,352 | **1.000000x** | PASS |
| 3 | 308,942 | 310,194 | 313,474 | **1.004053x** | PASS (<1.005) |
| 4 | 313,524 | 314,776 | 318,056 | **1.003993x** | PASS (<1.005) |

At K=3, degree wins 2,256 batches but loses 1,004. The net 1,252 grants out of 120,000 snapshots explain its 0.4053% advantage. The nonphysical exact oracle has another 3,280 grants over degree. No sustained FIFO performance is inferred.

Per-seed K=3 (greedy/degree/exact): 191 = 102,938/103,361/104,445; 409 = 103,014/103,424/104,531; 733 = 102,990/103,409/104,498. Per-seed K=4: 191 = 104,437/104,860/105,944; 409 = 104,540/104,950/106,057; 733 = 104,547/104,966/106,055.

## Independent audit and decision

The separate [checker](rtl/audit_packed_fifo_degree_transfer.py), which does **not** import the [evaluator](rtl/packed_fifo_degree_transfer.py), independently verified all B=2/3 head-valid K=2 cases, all B=3 K=3/4 capacity equalities, and the entire 120,000-snapshot B=4 seeded holdout, including per-seed wins and losses. **Local independent audit PASS.** Reproduction:

```sh
python3 research/v317/rtl/packed_fifo_degree_transfer.py > /tmp/v317-packed.json
python3 research/v317/rtl/audit_packed_fifo_degree_transfer.py /tmp/v317-packed.json
```

**Decision:** The degree-head controller remains a negative hardware candidate: 734 vs 260 generic Yosys cells (2.823x), while its prospective B=4 snapshot gain is <0.5% and K=2 with valid head has a **provably zero** grant-count advantage. This is stronger than the earlier unqualified all-mask comparison. Do not promote V317 or the exact oracle. Prior matched RF-proxy area and electrical failures remain binding. A future candidate needs independently derived workload bank traces, finite-source queueing, and legal routed PPA against compact greedy; no physical gate is passed by this result.
