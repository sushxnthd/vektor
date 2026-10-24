# V296: fixed-topology RC/load sensitivity falsification (2026-10-23)

## Evidence identity and precommitment
- Protocol frozen before measurement: `research/v296/FIXED_TOPOLOGY_RC_LOAD_PREREG_20261023.md`.
- GitHub Actions run [39944024015](https://github.com/sushxnthd/vektor/actions/runs/39944024015); artifact [12497702110](https://github.com/sushxnthd/vektor/actions/runs/39944024015/artifacts/12497702110).
- Artifact SHA-256: `338b95627e12154b451afe383ca47853a46eacfcdfacc2897f99c33ceb90625e`. The independent audit reported `FIXED_TOPOLOGY_SENSITIVITY_FAIL`; the CI failure is a scientific gate failure, not a crash.
- Three same-toolchain Nangate45 implementations, common 3.5 ns clock, same floorplan, nominal-RC placement/repair/global route per implementation. Frozen per-variant DEF SHA-256 is checked across all nine RC/load settings. The RC estimator is OpenROAD global routing, **not** detailed-route SPEF or signoff. All workload holdouts remain sealed.

## Fixed-topology results
All rows below use 0.005 pF output load. Slack is setup slack in ns at 3.5 ns; the suffix is the number of max-capacitance violations. Every case has zero max-slew violations.

| Wire RC multiplier | Original | Optimized one-hot | V296 pairwise | V296 slack lead vs best control |
|---:|---:|---:|---:|---:|
| 0.5 | +0.105485 / 0 | +0.338295 / 0 | +0.824474 / 0 | +0.486179 |
| 1.0 | +0.044824 / 0 | +0.259952 / 0 | +0.764527 / 0 | +0.504575 |
| 2.0 | **-0.092500 / 5** | +0.094309 / **3** | +0.616108 / **3** | +0.521799 |

At fixed nominal topology, V296's postrepair standard-cell area is 5,299.784 um² versus 6,165.348 um² for the smallest optimized control: **865.564 um² (14.039%) less controller area**. Area does not change during the sweep. No variant passes the full electrical gate at 2× RC; original also fails setup.

At RC=0.5, 1, 2, increasing output load from 0.0025 to 0.010 pF changed V296 slack by only -0.000023, -0.000023, and -0.000027 ns respectively (under 0.03 ps). This narrow perturbation does not establish output-driver or tile-level load robustness. The dominant setup path is nearly insensitive to this load setting.

## Independent inference and negative results
1. **FAIL**: The fixed-topology gate requires all 27 cases across all three designs to be electrically clean and meet the clock. At RC=2, V296 and the optimized control each have three max-capacitance violations; original has five and negative setup slack. This is an *electrical falsification*, not a software exception.
2. V296 is smaller and has better modeled setup slack than both controls in every tested case, and **has no candidate-only electrical failure**. These facts are insufficient for physical closure.
3. At the shared 3.5 ns clock, issue decisions are equivalent. **The analytical same-clock throughput-gain prediction is 0% under equal issue/cycle and unchanged downstream constraints; no workload-level throughput was measured.** The timing lead is a margin, not a measured frequency advantage. The controller-area reduction is not a GPU-area saving.
4. The earlier adaptively repaired low-RC experiment also failed (V296 one cap violation; original setup failure). Fixed-topology and adaptive-repair results must not be pooled to claim a single RC law.
5. There is no extracted interconnect, power evidence, integrated tile result, unseen workload transfer, or independent signoff. V296 remains provisional, not validated.

## Prospective local timing-law discriminator (unmeasured when this report was committed)
Freeze a **piecewise-linear interpolation**, not a universal physical law, between RC=1 and RC=2 at 0.005 pF:
`s_v(r) = s_v(1) + (r-1)[s_v(2)-s_v(1)]`, for `1 <= r <= 2`.
Predictions for new RC points (ns):

| RC | Original | Optimized | V296 | V296 lead vs optimized |
|---:|---:|---:|---:|---:|
| 1.25 | +0.010493 | +0.218541 | +0.727422 | +0.508881 |
| 1.50 | -0.023838 | +0.177131 | +0.690318 | +0.513187 |
| 1.75 | -0.058169 | +0.135720 | +0.653213 | +0.517493 |

**Frozen test:** hold each nominal implementation topology and output load at 0.005 pF, measure these intermediate RC values without repair/rerouting, and compare observed setup slack to these predictions. Tolerance: absolute error <= 0.040 ns per variant per point; the predicted V296 slack lead must remain positive. Capacitance-violation onset is not predicted and must be reported without post-hoc exceptions. These are new *electrical sensitivity* points, **not** permission to open workload holdouts. A failure bounds this local approximation; a pass does not establish architecture novelty or GPU throughput.

**Next kill gate:** symmetrical electrical repair and detailed-route/extracted-wire check against the strongest equal-resource control. Retire V296 if matched repair erases its area/timing benefit. The frozen full electrical gate remains failed.
