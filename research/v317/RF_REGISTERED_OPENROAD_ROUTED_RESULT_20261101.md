# V317 matched registered OpenROAD routing: prospective physical result (2026-11-01)

## Source and evidence
[GitHub Actions run #41335740201](https://github.com/sushxnthd/vektor/actions/runs/41335740201), head `b87661dcb363dee59c5015221c4b61f73962fb72`, official pinned `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8` (ORFS 202c7fccb), Nangate45 typical. [Raw 390-file artifact #13095323121](https://github.com/sushxnthd/vektor/actions/runs/41335740201/artifacts/13095323121) contains 40-flop matched registered wrappers, Yosys logs, final OpenDB/GDS, routing logs, extracted RC evidence and full timing/electrical reports. The preregistered protocol and fixed-footprint amendment were committed before these final results.

**Workflow overall FAILED**, correctly preserving the `source_65` high-density floorplan failure. **Three of four physical implementations completed** the entire ORFS flow through detailed routing, extracted parasitics, reports and final GDS. RTL simulation passed 4,998 post-fill registered grant comparisons. Earlier failed attempts from missing ORFS output directories and conflicting floorplan modes remain visible in GitHub Actions; they are tooling failures, not scientific negative results.

## Independent reproduction status

The independent raw ZIP audit [#41336377514](https://github.com/sushxnthd/vektor/actions/runs/41336377514) **PASSED** on the committed checker. It reproduced the 55.6991% area reduction, 63.7348% wire-length reduction, 2.6897x rounded isolated minimum-period ratio, three legal routed configurations and one preserved source high-density failure. It does not establish multi-corner signoff or GPU throughput.

## Frozen equal-footprint results

The two 35-labeled variants have the **same** 60 x 60 um die, 52 x 52 um core, 2.0 ns clock target, input/output register boundary, input drive BUF_X2 and 10-fF output loads. The 65-labeled variants have the **same** 44 x 44 um die and 36 x 36 um core. Labels are nominal stress settings, **not matched actual utilization**.

| Metric | Original 35 | Pairwise 35 | Pairwise 65 | Original 65 |
|---|---:|---:|---:|---|
| Complete route + GDS | PASS | PASS | PASS | FAIL at global placement |
| Final standard-cell area (um², excludes filler) | 1,316 | **583** | 576 | unmeasured |
| Actual core utilization | 49% | 22% | 46% | infeasible in this flow |
| Extracted-RC minimum clock period (ns, rounded) | 1.56 | **0.58** | 0.57 | unmeasured |
| 2.0-ns setup slack (ns) | +0.44 | +1.42 | +1.43 | unmeasured |
| Hold slack (ns, rounded) | +0.00 | +0.01 | +0.01 | unmeasured |
| Final detailed-route DRC count | 0 | 0 | 0 | unmeasured |
| Max slew / cap / fanout violations | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | unmeasured |
| Setup / hold violation count | 0 / 0 | 0 / 0 | 0 / 0 | unmeasured |
| Routed wire length (um) | 9,789 | **3,550** | 3,096 | unmeasured |
| Default-activity estimated power (W) | 3.78e-4 | 2.78e-4 | 2.70e-4 | unmeasured |

At matched 35-footprint, pairwise achieves **55.6991% less final standard-cell area** and **63.7348% less routed wire length**. The rounded extracted-RC control-block minimum-period ratio is **1.56 / 0.58 = 2.6897x**; this is *not* a GPU frequency or IPC result. Default-activity OpenROAD power proxy is **26.455% lower**, but the assumed activity is not workload-measured and the report is not silicon power signoff.

The `source_65` failure is `FLW-0024` at global placement: density exceeds 1.0 with the frozen `PLACE_DENSITY_LB_ADDON=0.20`. The original synthesized area is **1,333 um²**, already greater than the 36 x 36 = **1,296 um²** core area before placement overhead. The pairwise core finishes in that same footprint. This is an equal-footprint *capacity boundary*, not a proof that the original cannot be redesigned to fit another footprint or remapped under different objectives.

## Electrical and evidence interpretation
The final `6_report.log` records `RCX-0045` parasitic extraction (original 1,366 nets / 5,582 RC segments, pairwise 445 nets / 1,563 RC segments at 35). The `6_finish.rpt` contains explicit zero max-slew, max-cap, max-fanout, setup and hold violation counts for each completed route, and the final detailed-route logs end at zero DRC. This is **single-corner, open-source, routed control-block electrical evidence**, not multi-corner industrial signoff. The original's rounded hold slack is only +0.00 ns; do not infer robust hold margin.

## Predictions, mechanism and tile consequence
1. Frozen 35-footprint implementation-area win: **CONFIRMED**.
2. Frozen equal-clock, equal-port architectural no-win: **CONFIRMED BY GRANT EQUIVALENCE**, not by GPU workload measurement. Both make identical grants at 2.0 ns, so intrinsic completed-service throughput is **1.000x**.
3. Frozen smaller-footprint stress: pairwise routes; original fails the fixed-density floorplan gate. **Negative result preserved**, not silently discarded.
4. Routed timing/area kill: not triggered at 35, but no integrated tile result has been measured.

The *conditional* tile frequency boundary remains
`T_tile = max(T_other, T_arbiter, T_memory, T_interconnect)`.
The routed arbiter timing reduction helps tile frequency only if the original arbiter was on the tile's critical path and the optimized one is not eclipsed by another path. At fixed clock/ports, throughput remains identical unless saved area funds an additional useful resource under a nonsaturated bandwidth ceiling. This experiment does **not** establish either tile-level condition.

## Remaining world-class gates
Independent source-level checker `research/v317/rtl/audit_registered_route_artifact.py` **PASSED** in [hosted raw-artifact audit #41336377514](https://github.com/sushxnthd/vektor/actions/runs/41336377514), with [machine-readable independent JSON artifact #13094399256](https://github.com/sushxnthd/vektor/actions/runs/41336377514/artifacts/13094399256). It independently parsed all four route statuses, extracted-RC markers, final standard-cell area, wirelength, clock periods, explicit zero max-cap/max-slew/max-fanout/setup/hold violation counts and the high-density source failure. Next: integrate the checker into CI, reconcile final area excluding filler versus total placed/filler cell area, inspect extracted SPEF and worst-path sensitivity across corners, and test an equal-resource tile including RF SRAM/ports, clock distribution and actual workload traffic. Prior-art novelty remains unestablished. No RTX-5090 equivalence claim.

**Decision:** retain pairwise bank-credit as a physically promising, grant-equivalent control-block implementation optimization. Do **not** promote it as a new GPU scheduling architecture or demonstrated GPU throughput breakthrough. Kernellum PR #119 unchanged.
