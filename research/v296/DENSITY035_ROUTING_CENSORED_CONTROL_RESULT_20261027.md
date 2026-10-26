# V296 symmetric density-0.35 route diagnostic: candidate improves, matched control censored (2026-10-27)

## Decision

**INCOMPLETE_CONTROL_CENSORED_NO_CAUSAL_CLAIM.** The corrected hosted experiment [40411106938](https://github.com/sushxnthd/vektor/actions/runs/40411106938) completed on 2026-10-26 UTC. Both contestants were given the same frozen 75-minute exploratory limit. The V296 candidate reached five *completed* detailed-route optimization iterations; the independently optimized fifth-stage serial control never entered detailed routing before its time limit. This is not a matched DRC win, a routing signoff, or a usable clock result. The original density-0.45 reference [40359299905](https://github.com/sushxnthd/vektor/actions/runs/40359299905) remains canonical for physical feasibility.

The new **SHA-verified** original artifact digests and exact DRC trajectories are preserved in [machine-readable evidence](DENSITY035_FROZEN_ROUTE_FORENSICS_20261027.json). Four ZIPs were independently downloaded, their byte-level SHA-256 digests matched the GitHub Actions artifact records, and their OpenROAD logs and generated physical manifests were inspected. The diagnostic trial differs from the canonical runner only by density 0.45 -> 0.35 and the separately generated Tcl density-guard expectation; clock 3.5 ns, 2x RC, source RTL, physical commands, fifth-stage serial repair and floorplan are unchanged.

## Frozen-checkpoint observations

| Completed DRT iteration | Candidate, density 0.45 | Candidate, density 0.35 | Reduction | Serial, density 0.45 | Serial, density 0.35 |
|---:|---:|---:|---:|---:|---|
| 0 | 22,343 | 15,575 | 30.29% | 21,145 | censored |
| 1 | 20,278 | 11,566 | 42.96% | 16,581 | censored |
| 2 | 17,245 | 9,720 | 43.64% | 14,993 | censored |
| **3** | **12,020** | **3,632** | **69.78%** | **5,281** | **censored** |
| 4 | 10,441 | 1,662 | 84.08% | 3,083 | censored |
| 5 | 9,305 | 1,019 | 89.05% | 2,071 | censored |

The preregistered candidate-only threshold at iteration 3 was at most **8,414 DRC**. The observed **3,632** passes this component by a wide margin. But the second, *required* paired-control condition cannot be evaluated: the density-0.35 serial log has no completed DRT iteration 0, let alone iteration 3. Its job spent the remaining time in the independently optimized fifth-stage timing-repair phase after finishing the fourth stage. The final visible stage was `cts45_fourth_routed`, with estimated setup slack **-0.310570 ns**; the fifth-stage repair started and did not finish before the timeout. Do not call the serial DRC count zero or extrapolate its missing trajectory.

### Partial-identification boundary (not a fitted prediction)

The preregistered relative-ratio requirement is

`(DRC_pair035 / DRC_serial035) / (12020 / 5281) <= 0.75`.

Given the **observed** candidate iteration-3 count of 3,632, the missing serial iteration-3 count would need to be **at least 2,128** for this second gate to pass. A serial count of 2,127 or less would falsify the density-specific relative advantage. This is a transparent threshold on *missing* data, not a claim that either outcome occurred. The candidate-only improvement cannot establish a comparative architectural effect.

## Physical trade-off observed before detailed route

| Candidate global-route estimate | Density 0.45 | Density 0.35 | Change |
|---|---:|---:|---:|
| Cell area (um²) | 16,857.4843 | 17,213.9245 | **+2.1144%** |
| Estimated setup slack (ns) | +0.089278 | +0.055559 | **-33.719 ps** |

Density relaxation substantially reduces *candidate* early DRC counts, but also increases candidate intermediate area and worsens estimated setup slack. The +55.559 ps value is pre-detailed-route and does **not** establish extracted-RC closure. The frozen +50 ps guard would leave just 5.559 ps at this non-signoff stage, before routed parasitics. No area packing, frequency, or GPU speedup should be inferred from these intermediate estimates.

## Independent forensic checks and limitations

1. Original artifacts: density-0.35 candidate ZIP `91b76619...`, density-0.35 serial ZIP `21796d52...`, density-0.45 candidate ZIP `34fc9000...`, density-0.45 serial ZIP `36c9ce00...`; complete hashes are in the JSON evidence.
2. The independently parsed candidate trajectories agree with the hosted fail-closed diagnostic result `INCOMPLETE_EARLY_ROUTE_NO_CLAIM`. All recorded iteration values are from completed `DRT-0199` summaries, never an unfinished iteration.
3. Both trial manifests record the same source RTL hash, frozen 3.5 ns clock, 2x RC, identical derived Tcl and runner hashes, and preserved serial-only fifth-stage repair. This rules out the earlier density-guard execution blocker, but not other hidden tool/placement differences.
4. The 75-minute diagnostic is *informatively censored* because the serial control's additional timing-repair work consumed the route budget. It cannot be repaired statistically by assigning zero violations or by comparing unequal optimization stages.
5. No detailed-route completion for density-0.35 candidate, no extracted-RC candidate timing, no matched feasible serial clock, no workload-level hardware speedup, and no power claim. Sealed workload holdouts were not opened.

## Next physical experiment and kill criteria

A new *separately preregistered* matched experiment must ensure both contestants reach the same completed DRT iteration-3 checkpoint without silently removing the fifth-stage serial optimization. A larger, symmetrically allocated wall-time budget or a separately measured stage-budget analysis can resolve censoring; do not retroactively reinterpret the 75-minute trial. If both checkpoints become available, apply the **unchanged** 8,414 candidate threshold and 0.75 relative-ratio threshold before any new interpretation. Even a diagnostic pass is not sufficient: full routed DRC=0, extracted setup >= +50 ps, hold >=0, cap/slew=0, matched area and bandwidth, and measured-clock throughput must all pass. If physically matched timing or bandwidth erases the gain, reject this decoded V296 repair rather than retuning thresholds.

V296 is the sole provisional mechanism. V287 stays retired. No additional mechanism or research branch is authorized by this diagnostic. Kernellum PR #119 and its prospective holdouts remain separate and untouched.
