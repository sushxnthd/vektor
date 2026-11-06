# V317 matched electrical-headroom challenge: routed falsification (2026-11-06 UTC)

## Provenance and fixed comparison
GitHub Actions [run 42135819724](https://github.com/sushxnthd/vektor/actions/runs/42135819724), source commit `702ee38077c12907d27e28e217783e95c676e35f`, completed successfully at the *workflow* level. [231-file raw artifact 13465559116](https://github.com/sushxnthd/vektor/actions/runs/42135819724/artifacts/13465559116), SHA256 of archive `8edd3fd2110b6fdee839ce5f49dce3dc21b8ad5e6de33f843cabc6dd85f690db`. Pinned ORFS container digest `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`. Same Nangate45 flow, 300 x 300 um die, 10..290 um core, density add-on 0.20. RTL equivalence reported `PASS V317 compact challenger cycles=4096 accepted=13191 overflow=0`.

**Independent extraction:** the two `logs/nangate45/vektor_v317_rf_proxy_top_{compact,pairwise}/base/6_report.json` files and corresponding `reports/.../6_finish.rpt` were read directly from the uploaded ZIP, rather than treating a green workflow status as signoff.

| Final routed metric | Compact greedy | Pairwise |
|---|---:|---:|
| Standard-cell instance area (um²) | 21,389.1 | 21,533.0 |
| Setup worst slack (ns) | +0.758337 | +0.800198 |
| Hold worst slack (ns) | +0.00245079 | **-0.00419309** |
| Setup violations | 0 | 0 |
| Hold violations | 0 | **12** |
| Max-cap violations (from 6_finish.rpt) | **10** | **13** |
| Max slew violations | 0 | 0 |
| Fmax proxy (MHz) | 446.098 | 454.586 |
| Reported total power proxy (W) | 0.0106334 | 0.0105572 |

Pairwise area is **143.9 um² larger**, i.e. **0.67277% more** than compact (143.9 / 21389.1). Pairwise fmax is 1.902% higher in this run, but that does not establish workload speedup, and its negative hold slack and 13 max-cap violations disqualify it. Compact is also electrically illegal due to 10 max-cap violations. The power figures are tool estimates without activity calibration; do not infer measured energy.

## Binding decision
**FAIL: relaxing die/core headroom did not establish an electrically legal, area-competitive pairwise RF proxy.** This is an additional physical falsification, not a reopened positive V317 mechanism. The 2% preregistered materiality requirement also fails, with the sign of the area difference reversed. Preserve the earlier compact-greedy no-go and do not claim tile density, GPU IPC, calibrated power, or RTX 5090 equivalence.

The workflow itself returned success because both routes completed and artifacts were preserved; success is not an electrical signoff verdict. Any subsequent experiment must first state a prospective repair mechanism and fixed electrical, area and workload gates; no positive claim may be made from timing or isolated controller statistics alone.

## Reproduction of the independent extraction
Download artifact 13465559116 from run 42135819724. In the ZIP, parse `rf_proxy_compact/logs/nangate45/vektor_v317_rf_proxy_top_compact/base/6_report.json` and the analogous `rf_proxy_pairwise` file. Extract keys `finish__design__instance__area`, `finish__timing__setup__ws`, `finish__timing__hold__ws`, `finish__timing__drv__hold_violation_count`, `finish__timing__fmax`, and `finish__power__total`. In each `reports/.../6_finish.rpt`, inspect `finish max_cap_violation_count` and `finish max_slew_violation_count`. These are raw reported values, not newly run signoff.
