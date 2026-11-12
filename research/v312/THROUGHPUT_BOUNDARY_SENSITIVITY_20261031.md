# V312 clock/occupancy/bandwidth boundary: necessary, not sufficient

Based on independently hosted frozen synthetic admission evidence from [run #41181757541](https://github.com/sushxnthd/vektor/actions/runs/41181757541). The RTL testbench passed 50,002 vectors and generic Yosys synthesis completed with **3,422 generic cells**. This count is candidate-only and is **not** a matched area comparison or physical pass. No Nangate45 mapped timing, routed RC, capacitance/slew, or real workload trace exists for V312 yet.

Define G as the predicted admission ratio, f as the fraction of baseline runtime that could be improved by admission, d as the full-tile candidate/base clock-period ratio, c as normalized control/occupancy overhead, and B as an independent bandwidth/port speedup ceiling. An optimistic necessary upper bound is:

`S <= min(1/[(1-f)+f/G], B) / [d(1+c)]`.

This assumes all f-limited work benefits at the synthetic G and all other work is unchanged. It is not a fitted performance model. The bound can be optimistic because new backup operands increase routing, crossbar, and scheduler pressure.

| Frozen regime | Synthetic G | f | Best S at d=1,c=0,B=infinity | Largest d allowing S>=1.10 |
|---|---:|---:|---:|---:|
| Hotspot | 1.9500 | 0.25 | 1.1387 | 1.0352 |
| Hotspot | 1.9500 | 0.50 | 1.3220 | 1.2018 |
| Transfer | 1.2686 | 0.25 | 1.0559 | 0.9599 |
| Transfer | 1.2686 | 0.50 | 1.1184 | 1.0167 |
| Transfer | 1.2686 | 0.75 | 1.1888 | 1.0807 |
| Disjoint no-win | 1.0000 | any | 1.0000 | 0.9091 |

**Decision boundary:** even with no area/power penalty, the perturbed transfer regime cannot reach 10% GPU speedup at f=0.25 without a faster clock. At f=0.50 it tolerates at most **1.67% clock-period increase** before losing the 10% target, with zero extra control overhead and unlimited bandwidth. With a 5% clock-period penalty and 2% extra control overhead, its optimistic upper bound falls to about **1.044x**. If the workload is already bandwidth-limited to B=1.0, no admission mechanism can produce positive throughput gain under this model.

**Physicality consequence:** candidate-only generic synthesis is not a survival gate. The next run must compare full two-choice RTL against a capable equal-resource selector with mapped area, placed timing, and electrical checks; test workload-level f and B from real traces. The present result is a narrow, source-pinned positive *admission* mechanism, not a credible tile-level GPU gain or novel architecture claim.
