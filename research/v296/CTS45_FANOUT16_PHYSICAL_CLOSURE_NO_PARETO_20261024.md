# V296 symmetric fanout-16 CTS experiment: physical closure with a failed-control Pareto gate (2026-10-24)

## Provenance and evidence tier

Frozen protocol: [CTS45_SLEW40_NULL_INTERVENTION_AND_FANOUT16_PREREG_20261024.md](CTS45_SLEW40_NULL_INTERVENTION_AND_FANOUT16_PREREG_20261024.md). Completed [Actions run 40108270016](https://github.com/sushxnthd/vektor/actions/runs/40108270016), input commit `78e5850fab6d289f77cc0d0156b13b9f319030f2`. Both contestant jobs completed successfully; the independent aggregate exited 3 deliberately because the serial-onehot control was timing-infeasible. All raw archives are retained: pairwise artifact 12565679085 (SHA256 `177c0655d4c6a2e0eb6730fa739f995347966928baae12d653f72b0619b498c3`), serial artifact 12566780115 (SHA256 `e6254f6e4d8d00cc1cc63904616bce4dacbad4481b4e6370b18f1f8a93fe21ed`), independent audit 12566227519 (SHA256 `5cad1c240017be0e105f15948531ede650ecfe498814d08c50fe6a12ff29a0ff`). SHA digests are reported by GitHub Actions, not separately rehashed here.

Evidence tier: Nangate45, 45%-density placement target, 3.5 ns clock, 2x RC, propagated-clock CTS, detailed route, OpenRCX SPEF extraction and independent electrical/physical checker. **Not foundry signoff, strict equal-consumed-area, power, or integrated GPU throughput evidence.**

## Independent measured comparison

| Metric | V296 pairwise | Serial one-hot |
| --- | ---: | ---: |
| Pre-CTS controller area (um^2) | 5987.926155 | 6942.599828 |
| Post-CTS controller area (um^2) | 5991.915852 | 6946.589970 |
| Final extracted controller area (um^2) | **6239.828210** | 7167.901828 |
| Extracted propagated-clock setup slack (ns) | **+0.430410** | **-0.074402** |
| Extracted hold slack (ns) | +0.284848 | +0.275125 |
| Max-slew / max-cap violations | **0 / 0** | 0 / 0 |
| Routing DRC violations | 0 | 0 |
| Output net `issue_wave0[0]` extracted loads | **15** | 15 |
| Output net `issue_wave0[0]` extracted capacitance (pF) | 0.0255194 | 0.0243236 |
| CTS buffers inserted | 3 | 3 |
| Frozen candidate physical gate | **PASS** | n/a |
| Frozen control physical gate | n/a | **FAIL: setup** |

V296's final area advantage is **928.073618 um^2 = 12.947633% of serial control area**, and its extracted setup slack lead is **504.812 ps**. Both satisfy the *numerical* 10%-area / 200-ps-lead thresholds, but **do not satisfy the preregistered feasible-control Pareto gate**. The independent aggregate decision is `FANOUT16_CONTROL_INFEASIBLE_NO_PARETO_CLAIM`, not a pass.

## Causal physical finding

Compared with the prior symmetric 40%-slew-margin experiment, fanout-16 changes V296's `issue_wave0[0]` output net from 79 internal sinks to 15, eliminates all 32 max-slew violations, and reduces the extracted net capacitance from 0.126904 to 0.0255194 pF (79.89% reduction). This comes at an observed final controller area increase from 5989.256202 to 6239.828210 um^2 (**+250.572008 um^2**) and setup slack change from +0.299279 to +0.430410 ns (**+131.131 ps**). The control also changes: its area rises from 6953.771781 to 7167.901828 um^2 (**+214.130047 um^2**) and its setup improves from -0.188049 to -0.074402 ns (**+113.647 ps**). These are matched-run observations, not isolated causal attribution to a specific buffer cell.

**Decision:** the frozen fanout topology and V296 physical feasibility predictions survive. The control-feasibility/Pareto requirement does not. Retain V296 as the sole provisional architecture mechanism; V287 remains retired. Do not reclassify the aggregate's expected nonzero exit as a CI failure.

## Quantified next decision boundary (not a post hoc pass criterion)

At the *measured* control area 7167.901828 um^2, V296 may grow by only **211.283435 um^2** before losing the frozen 10% relative area advantage. The serial control has **232.098172 um^2** area headroom below the 7400 um^2 ceiling. To satisfy the frozen +50 ps setup margin, the control requires at least **124.402 ps** additional extracted setup slack while retaining zero electrical/DRC violations and nonnegative hold. If control area shrinks while candidate stays fixed, a control area below **6933.142455 um^2** also destroys the 10% area-saving criterion; a stronger control must not be discarded because it improved.

The measured candidate/control setup difference can shrink by **304.812 ps** before the 200 ps relative-lead criterion fails. These bounds are necessary arithmetic, **not** a guarantee that a feasible control exists or that a physical intervention can reach it. The next preregistered matched experiment must give the control a real chance to close timing under identical clock/load/floorplan/RC constraints and must evaluate both physical feasibility and relative advantage without reopening sealed workloads.

## Architecture limitation

V296 and serial one-hot have equivalent issue-admission semantics. At fixed tile frequency, same resources, and same traffic, this controller substitution has **zero intrinsic IPC advantage**. Its measured controller-level timing/area can translate into throughput only if it changes the tile's critical clock or resource budget without creating a bandwidth, occupancy, port, or power bottleneck. The 504.812 ps extracted controller slack lead is **not** a measured tile fmax increase. No RTX-5090 equivalence is supported. Workload holdouts remain sealed.

## Reproduction

Inspect run 40108270016 artifacts and execute `python3 research/v296/audit_cts45_fanout16.py --self-test`, then `python3 research/v296/audit_cts45_fanout16.py --aggregate build/v296/cts45_fanout16` after extracting the pairwise and serial artifacts into that directory. Exit 3 with `FANOUT16_CONTROL_INFEASIBLE_NO_PARETO_CLAIM` is the expected **scientific** outcome.
