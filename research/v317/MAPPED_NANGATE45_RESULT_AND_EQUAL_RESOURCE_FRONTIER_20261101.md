# V317: source-pinned Nangate45 mapping result and equal-resource frontier (2026-11-01)

## Evidence and frozen predictions

The pre-outcome protocol at `research/v317/FROZEN_NANGATE45_MAPPED_AREA_AND_LOAD_GATE_20261101.md` was committed before [run #41296883857](https://github.com/sushxnthd/vektor/actions/runs/41296883857). That run **passed**, source SHA `0d62a15fd0c1046374f287a6c683333297e6139d`, artifact [#13079606499](https://github.com/sushxnthd/vektor/actions/runs/41296883857/artifacts/13079606499). All four RTL variants were mapped with the same pinned Nangate45 typical Liberty and Yosys/ABC flow. The independent mapped-netlist checker passed. This report is a post-outcome analysis, **not** a second prospective prediction.

| 4 request slots, 16 banks | Nangate45 mapped area (um^2) | Cells | Sequential cells | Max net sinks | Dimensionless depth proxy (alpha=0) |
|---|---:|---:|---:|---:|---:|
| Source fixed priority | 798.798 | 747 | 0 | 67 | 19 |
| Pairwise fixed priority | **259.616** | **201** | 0 | **12** | **9** |
| Source rotating priority | 997.234 | 877 | 2 | 49 | 22 |
| Pairwise rotating priority | **445.018** | **344** | 2 | **36** | **12** |

Both frozen mapped-area predictions **survived**: fixed area falls **67.4992%**, rotating area falls **55.3748%** relative to its respective source implementation. The pairwise versions make identical grants to their corresponding source versions. Consequently their intrinsic completed-service gain at matched clocks and ports is **exactly zero**. This is a substantial *implementation optimization*, not evidence of a new GPU scheduling policy or GPU throughput acceleration.

## Strong-control equal-resource challenge

Against the **equally optimized pairwise fixed** implementation, pairwise rotating costs **1.714139x** mapped area. Prior frozen synthetic four-bank, p=.60 streaming arrivals produced 60,899 completed requests under fixed priority and 64,784 under rotating (ratio **1.063794x**). Oldest-first achieved 64,774, essentially tying rotation. These are 30,000-cycle queue-service models, **not** GPU IPC; the fixed-priority control suffers from starvation.

Let `g=64784/60899`, `c=f_rot/f_fixed` be the *unknown actual clock ratio*, `a` be the *unknown* fixed-arbiter share of baseline tile area, and `r=445.018/259.616`. Conditional service per tile area is

`E(a,c)=g*c/[1+a*(r-1)]`.

This is a boundary equation under a single-issue-service-rate scaling assumption, **not** a measured tile consequence. At `a=0`, rotation loses its modeled raw completed-service advantage if its achieved clock is **5.99685%** slower. At equal clock, the hypothetical fixed-arbiter area share must be below **8.9330%** for the stressed-regime service/area ratio to exceed 1. At `a=10%`, the area penalty already outweighs the 6.3794% service benefit even with identical clock. No actual tile area fraction is established.

If comparing only the arbiter's own mapped area, the synthetic service-per-mapped-area ratio is **0.620600x** for rotating versus fixed. This is not full-tile throughput per area and cannot be used as a silicon PPA claim.

## Wire/load sensitivity, without pretending it is timing

The pinned independent checker reports a dimensionless fanout-weighted path stress. Rotating/fixed depth ratios at alpha `0, 0.05, 0.2, 0.5` are **1.3333, 1.6051, 2.2167, 2.9394**. If one *hypothetically* scaled clock inversely with these proxies, rotating/fixed synthetic service would be **0.79785, 0.66275, 0.47991, 0.36191**. This exercise is a **sensitivity warning**, not OpenSTA delay, placed net length, extracted RC, setup/hold closure or a frequency prediction. In a real GPU, another tile path may determine the clock.

## Independent reproduction

The committed `research/v317/rtl/hosted_mapped_audit_snapshot_20261101.json` transcribes selected fields from the hosted independent audit, with exact run/artifact/source identifiers. To recompute the post-outcome boundaries:

`python research/v317/rtl/audit_rf_mapped_frontier.py research/v317/rtl/hosted_mapped_audit_snapshot_20261101.json --check`

The snapshot is **not a substitute** for the original full mapped netlists and Liberty; those remain in the hosted artifact. The script fails on nonpositive areas, unexpected flop counts, missing stressed-regime identity or drift in the pinned source and expected key boundaries.

## Decision and remaining hard gates

**Retain pairwise bank-credit as an optimized equal-grant implementation baseline.** Do not promote rotating priority as a novel mechanism: its stressed synthetic benefit is a fairness effect that oldest-first nearly matches, and the optimized rotating implementation is more expensive and deeper under all tested dimensionless load assumptions. Do not infer that rotating is electrically slower until standard-cell STA with characterized arcs and loads is performed.

**Next:** (1) matched OpenSTA constraints and pin loads; (2) placement and routed RC/electrical checks; (3) map oldest-first or a fair minimal alternative at equal resources; (4) trace-based GPU issue and bank pressure; (5) prospective workload boundary prediction. Preserve V296 as the historical primary physical direction and V287 as historical; do not revive either from this result without an explicit active-mechanism transition. No RTX-5090 equivalence, silicon power or GPU IPC is claimed.
