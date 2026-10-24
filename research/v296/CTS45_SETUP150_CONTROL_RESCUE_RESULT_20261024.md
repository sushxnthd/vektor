# V296 post-CTS setup150 control-rescue outcome (2026-10-24)

## Provenance and decision
Frozen experiment: `research/v296/CTS45_SETUP150_CONTROL_RESCUE_PREREG_20261024.md`.
Completed GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/40111559059
Source commit: `10ffb8ea4ed3b3a78d3e0d87fd2b8cd58ad86d1a`.
The independent aggregate job exited 3 with `CONTROL_RESCUE_FAIL_NO_PARETO_CLAIM`, as designed. Both contestant jobs completed and the independent checker self-tests passed. The workflow artifact SHA-256 values reported by GitHub are `8127b502e27ff44079a71b4fc6583d06c50bc062316da59a1ca94572469128ec` (pairwise), `ce5adfbd312ea6e6124e5c1b577802d9e4e7b8330b9419246094c633ab27074d` (serial), and `37adfbe68e4fa8152cda0db8a7479142759d1b22eee25e7ffced0a422f9d0f5d` (aggregate). The measurements below are transcribed from the hosted independent aggregate log; artifact byte-for-byte independent redownload is not claimed.

| Measured post-CTS, detailed-route, 2x OpenRCX | V296 pairwise | Serial one-hot |
|---|---:|---:|
| Area (um^2) | 6239.828210 | 7221.899967 |
| Setup slack (ps) | +430.410 | +19.125 |
| Hold slack (ps) | +284.848 | +249.349 |
| Max-slew / max-cap / route DRC | 0 / 0 / 0 | 0 / 0 / 0 |
| Meets 50 ps setup guardband | YES | **NO** |
| Controller area <= 7400 um^2 | YES | YES |
| Feasible under frozen gate | **YES** | **NO** |

Candidate area saving relative to serial: **13.5985%**; setup advantage **411.285 ps**. These are controller results, not equal-consumed-area comparisons, power measurements, tile-level frequency or GPU throughput.

## Falsification and intervention effect
The symmetric `repair_timing -setup -slack_margin 0.150` intervention improved serial setup slack from -74.400 ps in the preceding fanout16 experiment to +19.125 ps (**+93.525 ps**) while increasing its area from 7167.900 to 7221.900 um^2 (**+54.000 um^2**). Candidate values remained unchanged to reported precision. The serial implementation still misses the required 50 ps setup guardband by **30.875 ps**. The 150 ps control-rescue hypothesis is therefore falsified at the preregistered feasibility threshold. Do not label the experiment a Pareto victory.

At the current point, serial has only **178.100 um^2** area headroom to the 7400 um^2 ceiling. The pairwise implementation can grow by at most **259.882 um^2** at fixed serial area before its 10% relative area saving disappears; the serial area could fall by at most **288.757 um^2** at fixed pairwise area before the same boundary is crossed. Timing-lead advantage can shrink by **211.285 ps** before crossing the preregistered +200 ps threshold. These are algebraic budgets, not measured physical repair outcomes.

## Research interpretation
The previous 32-slew-violation problem was solved by a matched fanout16 intervention. The remaining obstacle to a defensible feasible-control comparison is serial setup closure, not electrical or routing closure. A higher post-CTS setup-margin policy is one *bounded* additional control-rescue attempt; if it fails, stop increasing margins blindly and inspect the control's critical path and equivalent-resource retiming options. A controller speed advantage at fixed 3.5 ns clock does **not** imply workload IPC gain. The necessary tile-level positive-gain boundary in `tile_throughput_boundary.py` still requires an actually clock-limiting controller, unused bandwidth, and measured tile-level frequency improvement. Workload holdouts remain sealed.

## Claim gate
**V296 remains the sole provisional mechanism; V287 retired.** No equal-consumed-area Pareto, power, signoff, GPU-tile, or RTX-5090 equivalence claim. Preserve this negative control result.
