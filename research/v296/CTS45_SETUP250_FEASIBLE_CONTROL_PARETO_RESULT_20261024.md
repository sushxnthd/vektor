# V296 setup250: first feasible-control post-CTS Pareto support (2026-10-24)

## Provenance and evidence tier

Frozen preregistration: `research/v296/CTS45_SETUP250_FINAL_CONTROL_RESCUE_PREREG_20261024.md`. Source branch `research/v296-pairwise-bank-conflict`, source commit `c0a5b17e9cd573d72e0b85226244fb61d61f46b5`. Completed workflow: https://github.com/sushxnthd/vektor/actions/runs/40113773976 . Independent aggregate job `120934558740` completed successfully and returned `FEASIBLE_PARETO_SUPPORTED`. Both contestant jobs `120930709292` and `120930709457` succeeded. All four independent audit self-tests passed. Values below are transcribed from the independent aggregate job log; independent artifact-byte redownload is **not** claimed.

GitHub Actions archive digests reported during download: pairwise SHA256 `76415bacd881ea5534a1ca0afe1beb69c9243ea65d91b9cdf08650175df9ee59`; serial SHA256 `bddd2e73b893b5506dcf52378b33eb943112649973d7137bfa112fb0c0a07c6a`. Original evidence archives: https://github.com/sushxnthd/vektor/actions/runs/40113773976/artifacts/12568335950 and https://github.com/sushxnthd/vektor/actions/runs/40113773976/artifacts/12568600086 ; independent aggregate archive https://github.com/sushxnthd/vektor/actions/runs/40113773976/artifacts/12567828794 .

**Evidence tier:** matched Nangate45 post-CTS propagated-clock detailed route, extracted 2x OpenRCX RC, 45% placement-density target, 3.5 ns clock, 16 maximum fanout, 250 ps max transition, 7400 um^2 controller ceiling. This is **not** silicon signoff, not a full GPU tile, not measured power, and not strict equal-consumed-area.

## Frozen physical comparison

| Measurement | V296 pairwise | Serial one-hot |
|---|---:|---:|
| Final controller cell area (um^2) | 6239.828210 | 7284.941983 |
| Extracted setup slack (ps) | +430.410 | +104.791 |
| Extracted hold slack (ps) | +284.848 | +249.547 |
| Max-slew violations | 0 | 0 |
| Max-cap violations | 0 | 0 |
| SPEF-extracted output-net load count | 15 | 15 |
| Routing DRC violations | 0 | 0 |
| Meets area <=7400 and setup >=+50ps | YES | YES |
| Independently audited feasibility | **PASS** | **PASS** |

V296 saves **1045.113773 um^2 (14.3462%)** of controller cell area and has **325.619 ps** greater extracted setup slack. Both contestants meet the preregistered gate; this is the **first supported feasible-control Pareto comparison** for this mechanism, and the independent checker explicitly reports `strict_equal_consumed_area=false`.

The control's setup slack improved from +19.125 ps in the setup150 run to +104.791 ps (**+85.666 ps**), with controller area increasing from 7221.899967 to 7284.941983 um^2 (**+63.042016 um^2**). V296 area and timing were unchanged to displayed precision. This improvement is an actual stronger-control rescue, not an unfair weakening of the baseline.

## Resource and timing robustness budgets (algebra, not measurements)

At the frozen 10% relative-area threshold and current control area, V296 can absorb at most **316.619575 um^2** of additional candidate-only area before dropping below 10% savings. At current V296 area, the control can shrink to **6933.142455 um^2** before the candidate's saving drops below 10%. At the +200 ps timing-lead threshold, the observed 325.619 ps lead has **125.619 ps** of remaining relative slack budget. Control has **115.058017 um^2** area headroom to the original ceiling; V296 has **1160.171790 um^2**.

These budgets are not equivalent to equal-area frequency superiority, switching power, or resource reinvestment.

## Claim discipline and next decisive science

1. **Stop blind setup-margin escalation:** the frozen setup250 experiment has succeeded and the strongest serial control is now feasible. Further margin tuning on the observed results risks selection bias.
2. **Independent physical replication:** repeat the feasible-control comparison with independently chosen placement seeds and physically matched I/O loading and wire assumptions. Report the entire distribution and failures, not only winning seeds. An actual full-tile CTS/STA analysis is necessary before converting controller slack into clock gain.
3. **Strict equal-resource challenge:** compare both controllers inside an identical tile with equal bank count, ports, occupancy, clock, output loading and offered work. The candidate's saved area is a *separate area metric* until resource reinvestment is physically implemented and validated. Do not equate a common area ceiling with strict equal-consumed-area.
4. **Positive boundary law:** at unchanged frequency, equivalent arbitration admits the same operations per cycle. The existing `tile_throughput_boundary.py` predicts a positive tile throughput change only if V296 actually reduces the limiting tile period and the baseline is not bandwidth saturated. Freeze one win and one no-win workload regime before opening unseen holdouts; quantify q and bytes/op from counters.
5. **Power/novelty:** measure matched switching activity, dynamic/leakage proxies and compare with published bank arbitration designs; report negative regimes and prior-art overlaps.

**Decision:** V296 remains the only active provisional mechanism. V287 stays retired. Holdouts sealed. `FEASIBLE_PARETO_SUPPORTED` is a bounded controller-level finding, not a world-class GPU result or RTX-5090 equivalence. Kernellum PR #119 is separate and untouched.
