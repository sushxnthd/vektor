# V317 strong-baseline materiality law, pre-route (2026-11-02)

**Evidence tier:** algebraic sensitivity using **historical** extracted-RC RF-proxy areas. The newly preregistered three-way source/pairwise/compact OpenROAD result is **PENDING**. This document is not a new physical observation, signoff, GPU IPC, SRAM result or performance claim.

## Strongest same-policy challenger

The historical serial-mask source RTL is not a competent isolated logic baseline: V309's separately verified compact fixed-priority greedy arbiter had 260 generic cells versus 1,321 for that source under matched generic synthesis, while emitting identical grants in 109,076 oracle cases. We imported that *same policy* as a third physical implementation. [Frozen protocol](FROZEN_COMPACT_GREEDY_RF_PROXY_CHALLENGE_20261102.md) precedes all new challenger RTL and physical outcomes. [Three-way hosted run](https://github.com/sushxnthd/vektor/actions/runs/41443576796) passed 4,096-cycle source/pairwise/compact grant, operand and RF-port equivalence; routing is not yet verified.

## Exact conditional boundary, no fitted parameters

Let `S` be the historical source routed area, `P` the historical pairwise area, and `C` the **unknown future** compact baseline area at the same physical constraints. Pairwise can save at least the prospectively frozen 2% of compact only if

`(C-P)/C >= 0.02  <=>  C >= P/0.98.`

Writing `C=S(1-d)` where positive `d` is compact's improvement over source, the necessary condition is `d <= 1-P/(0.98 S)`. This is a deterministic area-boundary law, **not a GPU throughput law**.

| Historical density | Source S (um2) | Pairwise P (um2) | Compact C required (um2) | Required compact area excess over source |
|---|---:|---:|---:|---:|
| 0.05 | 21,610.6 | 21,432.2 | 21,869.592 | +258.992 um2 (+1.1984%) |
| 0.15 | 21,533.5 | 21,404.2 | 21,841.020 | +307.520 um2 (+1.4281%) |
| 0.35 | 21,535.6 | 21,324.7 | 21,759.898 | +224.298 um2 (+1.0415%) |

Thus, **if the compact challenger is no larger than the historical source** and pairwise retains its historical area, the 2% materiality gate is mathematically impossible. Even a compact challenger **1% larger** than historical source would still fail the threshold at all three observed densities. A compact challenger **2% larger** would cross the raw threshold under the fixed-area assumption. These are prospective **conditional** predictions, not measured compact outcomes.

This analysis uses historical `P`; re-synthesizing the three variants may change all areas and invalidates literal transfer of those numbers. The independent new route must use its **own** compact/pairwise measurements and electrical legality; it cannot substitute this table for physical evidence.

## Architecture interpretation

All three variants implement the same greedy policy, 16 banks, two read ports per bank, four issue slots and identical register storage. At fixed clock and resources, their issue-service gain is **exactly 1.000x**. Area packing could hypothetically matter only if a legal additional tile can be implemented without reducing occupancy or saturating bandwidth. Neither a legal tile nor a GPU workload benefit is demonstrated. The prior V317 RF-proxy failures remain failed; do not relax 2%.

Reproduction: `python3 research/v317/rtl/compact_baseline_threshold_boundary.py` performs Decimal-arithmetic evaluation, positive/negative mutation controls, and sensitivity regimes from the immutable `RF_PROXY_DENSITY_OBSERVATIONS_20261102.json`. It does not read new physical artifacts; [raw-artifact checker](rtl/audit_rf_proxy_compact_challenger.py) is separate.
