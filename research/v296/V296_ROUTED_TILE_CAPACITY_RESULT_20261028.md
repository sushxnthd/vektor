# V296 routed-area capacity and global-port sensitivity result (2026-10-28)

**Scope:** Conditional synthetic tile-packing falsification. This is not a physical win. Protocol frozen in [V296_ROUTED_TILE_CAPACITY_PREREG_20261028.md](V296_ROUTED_TILE_CAPACITY_PREREG_20261028.md) before executing the sweep. Executable [v296_routed_tile_capacity_boundary.py](v296_routed_tile_capacity_boundary.py), structured [results JSON](V296_ROUTED_TILE_CAPACITY_RESULT_20261028.json). Local exhaustive 104,976-case independent serial-vs-pairwise admission test and two-port invariants passed. Synthetic run: three frozen seeds, 12,000 cycles each per regime; no real workload holdout opened. Hosted reproduction has **not** been run for this new script.

## Physical evidence caveat

The inputs are measured D4 deferred-write routed areas (candidate 19543.019647 um2, serial 21914.943 um2) from [run 40646515864](https://github.com/sushxnthd/vektor/actions/runs/40646515864). The serial comparator fails routed setup and hold. Thus **none of the following counterfactual two-slice results establishes a matched feasible tile benefit**. The separate integrated tile-slice physical run [40675850164](https://github.com/sushxnthd/vektor/actions/runs/40675850164) has now completed: both candidate and serial fail physical gates, independently audited; see [integrated falsification](V296_INTEGRATED_TILE_PHYSICAL_GATE_FALSIFICATION_20261028.md).

## Frozen predictions and outcomes

| Synthetic regime | Area budget (um2) | Shared B | Candidate / serial slices | Mean admitted-wave ratio | Frozen prediction |
|---|---:|---:|---:|---:|---|
| Capacity win, q=1, h=0 | 40000 | 8 | 2 / 1 | 1.99720 | >1.5: PASS |
| Shared-port no-win, q=1, h=0 | 40000 | 1 | 2 / 1 | **1.00000** | exact equality: PASS |
| Frozen-budget no-win, q=1, h=0 | 30000 | 8 | 1 / 1 | **1.00000** | exact equality: PASS |
| Capacity fragility, q=1, h=0 | 40000 | 8 | 2 / 1 | 1.99720 before area perturbation | +500 um2/slice eliminates second candidate slice: PASS |
| Mixed sensitivity, q=.60, h=.40 | 40000 | 5 | 2 / 1 | 1.87197 | no preregistered fit, descriptive only |

The 40,000 um2 nominal second-slice area boundary is **456.980353 um2 (2.33833%)** extra area per candidate slice. Above that perturbation, candidate also fits only one slice and the same-clock admission advantage disappears in the equal-occupancy model. The 40,000 um2 two-versus-one packing window is [39086.039294, 43829.886) um2 before overhead. The actual frozen 30,000 um2 budget has **one slice each**.

## Boundary law and failure conditions

For area budget A and additional per-slice physical overhead delta, K_a=floor(A/(area_a+delta_a)). For identical arbiter admissions, latency, occupancy and frequency, equal K and equal shared B imply exactly equal throughput under coupled identical request streams. If K_candidate > K_serial, a possible issue-capacity advantage still requires unsaturated global bandwidth, adequate ready work and physical closure. The full closed-loop stochastic simulator is a *synthetic* estimate, not a universal closed-form GPU law. Area overhead exceeding 456.980353 um2/slice kills this particular 40k two-slice packing hypothesis even before electrical and memory costs.

**Decision:** Do not advance this conditional 1.997x synthetic admission ratio as a V296 result. Both physical controls must first be feasible, and integrated tile physical evidence currently fails. The next decisive primary experiment is the bounded upstream-cone symmetric physical repair or retirement of V296. Keep V287 retired and Kernellum untouched.
