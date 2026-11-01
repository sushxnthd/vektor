# V317 tile-level consequence boundary: frozen conditional predictions pass (2026-11-01)

## Evidence provenance and what this is NOT
The [frozen protocol](FROZEN_TILE_CONSEQUENCE_BOUNDARY_20261101.md) was committed as `52225b49c1f2e9b1f6826efafe20ba390fed3966` **before** the calculator, independent finite-workload executor, and results. The implementation and independent tests were committed at `41f23ca` and `e156495`, and hosted verification workflow at `b020178`. Local Python 3 validation passed 5/5 unit tests, including **64 independently generated unseen synthetic parameter combinations** (128 source/pairwise finite-horizon checks). Hosted run [#41320367945](https://github.com/sushxnthd/vektor/actions/runs/41320367945) **PASSED** on the source-pinned workflow commit `b0201781102bc624e9308710e7514c8c4f8887c7`, independently reproducing the frozen predictions and 64 synthetic holdouts.

The source numbers are the *within-run* 24-fF BUF_X1 Nangate45 mapped-cell and ideal-wire STA observations: source 785.498 um2 / 1.26 ns; pairwise 260.414 um2 / 0.59 ns. They are not placed/routed, do not include extracted wire RC, and do not represent a complete tile. Other-tile area, clock path, wire penalty, demand, and traffic ceiling are hypothetical sensitivity inputs. The two arbiters have identical grant decisions and bank ports.

## Positive boundary law with explicit physical and traffic gates
For variant j in {source,pairwise}:

- `N_j = floor(A_budget/(A_other+A_arb,j))`
- `T_j = max(T_other, D_arb,j + delta_wire,j)`
- `C_j = N_j*r/T_j`
- `R_j = min(lambda, B, C_j)`
- `G = R_pairwise/R_source` when the denominator is positive.

Here `r` is effective work per tile cycle (identical for grant-equivalent arbiters), `lambda` offered workload work/ns, and `B` shared bandwidth/port work/ns. The model does not claim that area saved in one arbiter can actually instantiate another tile; that is a conditional threshold to be tested in a real integrated floorplan. It also cannot predict power, actual occupancy, or cross-tile traffic interference.

## Five frozen predictions and independent validation

| Frozen regime | Hypothetical source/pairwise tiles | Source/pairwise period (ns) | Model gain | Outcome |
|---|---:|---:|---:|---|
| Noncritical, fixed budget 1,000,000 um2 | 24/24 | 1.50/1.50 | 1.000000x | predicted no-win passes |
| Area threshold budget 1,010,000 um2 | 24/25 | 1.50/1.50 | 1.041667x | conditional win passes |
| Same budget, B=16 work/ns | 24/25 | 1.50/1.50 | 1.000000x | bandwidth kill passes |
| Hypothetical critical arbiter, T_other=0.80 ns | 24/24 | 1.26/0.80 | 1.575000x | conditional clock win passes |
| Same, extra pairwise wire penalty 0.70 ns | 24/24 | 1.26/1.29 | 0.976744x | differential wire kill passes |

All cases assume r=1 and lambda=100 work/ns. B=100 except the bandwidth-kill case. The independent integer-token executor (10,000 one-ns ticks per design) agrees with the closed-form throughput rate within 0.03 work/ns for each of 64 unseen parameter combinations, and independently enumerates discrete tile counts. These holdouts validate **software-model consistency only**, not unseen GPU workload performance.

## New exact boundaries
With A_other=40,000 um2, 25 pairwise tiles first fit at budget **1,006,510.350 um2**, while 25 source tiles first fit at **1,019,637.450 um2**. The discrete 25-vs-24 advantage is therefore confined to a finite area-budget window, assuming all other tile costs remain identical. The within-run arbiter reduction is 525.084 um2, or about 1.29% of the hypothetical source tile area; at a fixed 24-tile count, the area saving alone does not increase throughput.

For the isolated clock-critical comparison, a pairwise differential wire/placement penalty >= **0.67 ns** erases the 0.67-ns ideal-wire delay margin, before checking transition/capacitance and setup/hold. If a different path sets the clock (`T_other>=1.26 ns`), both variants have the same clock even with zero wire penalty. If shared bandwidth or offered work is below both compute capacities, gain is 1.000x regardless of tile-count or clock potential.

## Scientific decision and next decisive gate
**Falsify unconditional GPU-throughput benefit.** The lower mapped area and shorter isolated pre-route cell path are real within the previous experiment, but the model shows that tile throughput improves only if (a) the saved area crosses a *real* replication boundary and demand/bandwidth permit it, or (b) the arbiter is on the *actual* integrated clock-critical path after routed wire RC. Neither condition is presently evidenced. The strongest equal-resource fairness alternatives, rotating priority and oldest-first, remain controls; this analysis does not show a new scheduling gain over either.

The next experiment must place and route matched netlists with extracted RC, reconcile the earlier mapped-area discrepancy, and integrate arbiter timing into a real tile-level critical-path and power/area budget. If the clock is set elsewhere and the saved area cannot be productively reinvested, retain only the implementation optimization and kill any performance claim. No RTX 5090 equivalence is supported.

Reproduce: `python3 -m unittest research.v317.rtl.test_tile_consequence -v` and `python3 -m research.v317.rtl.tile_consequence --json`. Keep V317 draft PR #34 and Kernellum PR #119 unchanged apart from this Vektor research addition.
