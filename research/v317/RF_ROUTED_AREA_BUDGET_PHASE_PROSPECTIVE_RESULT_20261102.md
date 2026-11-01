# V317 routed-area budget-phase law: prospective accounting result (2026-11-02)

## Source and evidence tier
Frozen before evaluation: [protocol](FROZEN_RF_ROUTED_LOAD_AND_AREA_PHASE_20261102.md) at commit `c288650`. The new [exact law and independent enumeration](rtl/rf_routed_budget_phase.py) and [five tests](rtl/test_rf_routed_budget_phase.py) were committed later at `f2e5e5c` and `fa11c21`. The pinned measured inputs are the earlier **single-corner 52x52-um matched routed 40-flop control-block** results, original/pairwise **1316/583 um2** and rounded extracted-RC periods **1.56/0.58 ns**. All other tile area, bandwidth, offered load and critical-path values in this report are **hypothetical**. This is an exact resource-accounting identity, not a GPU performance measurement or a novel scheduling mechanism.

## Exact predictive boundary
Let `A_s=A_o+1316`, `A_p=A_o+583`, `Delta=733`, and `n` source tiles fit in a budget `B`. Tile counts are `N_s=floor(B/A_s)`, `N_p=floor(B/A_p)`. For budgets uniformly sampled over the one-source-tile phase interval `B in [n A_s,(n+1) A_s)`, the fraction allowing **at least one extra pairwise tile** is

`P_extra = clamp((n+1)*Delta/A_s,0,1)`.

The proof is elementary: `N_p>=n+1` exactly when `B >= (n+1) A_p`; the intersection of this threshold with the interval has length `clamp((n+1)(A_s-A_p),0,A_s)`. The formula is valid for the event **at least one** extra tile, even if multiple extra tiles become possible. It does **not** predict GPU manufacturing budget distributions, occupancy, SRAM area, clock tree cost or RF traffic.

The conditional service ceiling is
`R_x=min(lambda, BW, N_x*r/max(T_other,T_x))`.
Since both RTL implementations issue identical grants, `r` is **identical** at equal RF ports. No performance benefit is possible at a common noncritical clock when the saved area buys no useful extra resource, or when `lambda` or `BW` already saturates service.

## Frozen results and unseen arithmetic transfer
Local Python 3 independent enumeration passed **five tests**, covering every integer budget in each interval (the hosted test is part of the new physical workflow, not yet confirmed).

| Frozen regime | Enumerated budgets | Extra-tile budgets | Throughput-win budgets | Outcome |
|---|---:|---:|---:|---|
| W1: 24 source tiles, other area 40,000, noncritical arbiter | 41,316 | 18,325 | 18,325 | PASS, conditional gain 25/24 only in extra-tile phases |
| N1: same, BW capped at 8 work/ns | 41,316 | 18,325 | **0** | PASS, **1.000x** under bandwidth saturation |
| Transfer H1: 17 tiles, other area 100,000 | 101,316 | 13,194 | 13,194 | exact formula PASS |
| Transfer H2: 32 tiles, other area 80,000 | 81,316 | 24,189 | 24,189 | exact formula PASS |
| Transfer H3: 48 tiles, other area 200,000 | 201,316 | 35,917 | 35,917 | exact formula PASS |
| Conditional clock-critical: 24 tiles, other period 1.0 ns | 41,316 | 18,325 | 41,316 | modeled clock win; **not** tile timing evidence |

At exactly `B=24*(40000+1316)=991584 um2`, both designs fit **24** tiles and W1 throughput is **1.000x**, even though the control-block area decreases by 733 um2 per tile. A 25th pairwise tile requires `B>=25*(40000+583)=1014575 um2`: **22,991 um2 of extra budget slack** above the exact source-24 threshold. Under the deliberately uniform phase assumption, the chance of this discrete tile-count step is **18,325/41,316 = 44.3533%**, and the average hypothetical throughput ratio is only **1.01848x** when bandwidth/offered work are unlimited and the arbiter is noncritical. These are *conditional budget-phase arithmetic*, not estimated GPU speedups.

## Physical experiment launched, not evaluated
[Matched routed output-load transfer workflow #41342972002](https://github.com/sushxnthd/vektor/actions/runs/41342972002) was **queued** at inspection. It runs the same original and pairwise 40-FF wrappers at **10 and 40 fF**, the same 52x52-um core, identical 2.0-ns clock and Nangate45 typical, preserving every failure. The 10-fF cases are replication controls; 40 fF is a prospective electrical stress holdout. **No 40-fF routed timing, electrical, area or power result is claimed yet.** It is not multi-corner signoff.

## Decision
This experiment tightens the architectural **NO-GO**: grant equivalence plus routed control-block savings cannot justify unconditional GPU IPC. It defines a measurable future gate: integrate actual tile area, SRAM/RF port constraints, clock paths and workload bandwidth before claiming resource-reinvestment performance. The prior routed area/period advantage remains an isolated implementation result; do not extrapolate it to RTX-5090 equivalence. Kernellum PR #119 was not modified.
