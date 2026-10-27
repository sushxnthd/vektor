# V296: SHA-pinned four-artifact hold25 matched physical delta and falsification (2026-10-27)

**Evidence tier:** routed OpenROAD / extracted OpenRCX, not signoff. **Architectural status:** V296 pairwise bank admission is the sole provisional mechanism; V287 retired. The fixed-word register-file remains a **two-word-per-bank proxy** and is not a production-deep RF implementation. This is a physical-repair result, not an independent new architecture mechanism.

## Immutable provenance and independent replay

Original no-margin full-route run [#40469489684](https://github.com/sushxnthd/vektor/actions/runs/40469489684), prospective symmetric +25 ps hold-target run [#40494515995](https://github.com/sushxnthd/vektor/actions/runs/40494515995). Both contestants completed detailed route, RC extraction and zero DRC. The hold25 independent aggregate **failed by design** (exit 3): candidate feasible but strongest serial control infeasible. It was not a GitHub plumbing error.

Original ZIP artifact IDs and SHA-256 digests:

| Variant | Baseline ID / SHA-256 | Hold25 ID / SHA-256 |
|---|---|---|
| V296 pairwise | 12721519936 / 7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b | 12732409198 / 6265bc15d8be03d62ec8b8f4c3f435b0e30c355f42ed75c5e7316fed40efc625 |
| Fifth-stage optimized serial | 12724948549 / 56781fca03ab151661e2c3c393639caa5e71862358fbbe50e0be1dfc278d6050 | 12732424916 / 1847b10524877f02791b335a0aed4afc99ba1c21a8143d070122489b8017e9c8 |

All four ZIPs were downloaded and verified against their original digests. Independently parsed original tool logs, DRC markers, 2x RC markers, serial fifth-stage marker, hold25 execution marker, and original audit JSON. The original and repaired synthesized netlists are **byte-identical within each contestant**, with candidate SHA ba201934346a482eb808e33fb5368ec53eefa9e7c0474b1bd59fa5bc185bc8e5 and serial SHA cd4804c9661c6b2daa50691ac10def0f098f625a1a76db09c457e0d71cace0b6. RTL source SHA is unchanged (1d798344ede7aee67d84f6dab5fd266dbd65c3c164f65694206c3d6b921eb8f2). The 3.5 ns clock, 0.45 density, 2x RC, and original thresholds were not relaxed.

## Matched extracted-RC observations

| Metric | Pairwise original | Pairwise hold25 | Serial original | Serial hold25 |
|---|---:|---:|---:|---:|
| Setup slack, ps | +74.236 | **+93.778** | −751.540 | **−731.487** |
| Hold slack, ps | −12.622 | **+14.704** | −9.430 | **+3.399** |
| Final area, µm² | 13,379.002 | **13,382.194** | 15,779.651 | **15,783.643** |
| Max-cap violations | 0 | **0** | 1 | **2** |
| Max-slew violations | 0 | 0 | 0 | 0 |
| DRC violations | 0 | 0 | 0 | 0 |
| Routed wire, µm | 149,199 | 149,346 | 176,658 | 176,742 |
| Vias | 56,915 | 57,064 | 67,500 | 67,656 |

The symmetric repair yields **pairwise +27.326 ps hold recovery, +19.542 ps setup improvement, and +3.192113 µm² area**, with 147 µm more wire and 149 additional vias. The serial control also improves both slacks (+12.829 ps hold, +20.053 ps setup) but gains a second capacitance violation. At the frozen +50 ps setup guard, nonnegative hold, zero cap/slew/DRC and <=30,000 µm² area, **only V296 passes**. Serial is still **781.487 ps short** of the +50 ps setup guard, before addressing two cap violations.

The candidate's final +43.778 ps setup guard margin and +14.704 ps hold margin are measured at this specific flow, RC corner, and two-word RF. These margins are not a signoff yield distribution.

## Scientific falsification and the boundary that survives

The prospectively frozen local delay-transfer model assumed nonnegative setup cost per effective hold-delay insertion, with nonnegative adverse setup drift. Under those assumptions, hold recovery cannot *improve* setup slack. The candidate exhibits **positive hold and setup improvements simultaneously**, so the model's **nonnegative setup-cost assumption is falsified as a description of this routed observation**. Do not post-hoc fit a negative kappa or claim a universal positive physical law. Physical restructuring, critical-path switching, and routing changes may explain the sign, but this one pair does not identify their separate causal contributions.

The physical feasibility boundary remains explicit: setup >= +50 ps, hold >= 0, cap = slew = DRC = 0, area <= 30,000 µm², for **both** contestants. A candidate-only pass is insufficient to claim matched feasible Pareto superiority. The original aggregate checker correctly returned CONTROL_TILE_SLICE_INFEASIBLE_NO_PARETO_CLAIM.

The conditional packing calculation for 18 candidate slices versus 16 serial slices at the observed areas allows only (16*15783.642837 - 18*13382.194020)/18 = 647.711 µm² additional candidate-only overhead per slice. It is not a tile-level result: the serial reference fails timing and capacitance, and RF depth, interconnect, SRAM, clock-tree, and bandwidth scaling are excluded.

At the same 3.5 ns clock, the matched admission checker reports **zero throughput gain**. No measured tile Fmax, application speedup, power advantage, or RTX-5090 equivalence follows.

## Independent reproduction and hard next gate

Run the Python 3 standard-library checker in research/v296/hold25_matched_delta_audit.py with --self-test. Download the four original artifact ZIPs in the table above, then run it with --audit BASE_PAIR BASE_SERIAL HOLD25_PAIR HOLD25_SERIAL.

The checker refuses changed ZIPs, nonmatching RTL/physical Tcl provenance, incomplete route, changed RC, nonzero DRC, missing hold25 markers, mismatched serial fifth-stage control, tool-log/audit disagreement, or changed synthesized netlists. Machine-readable anchors are in HOLD25_MATCHED_DELTA_20261027.json.

**Next scientific action:** do not retune the 25 ps hold target after seeing these results. Establish a *physically feasible strongest serial alternative* under equal resources and the same acceptance thresholds; then perform a deeper-bank RF transfer test, wire/load sensitivity, matched feasible clock and workload traffic analysis, and unseen-regime predictive boundary evaluation. If deep-bank transfer or bandwidth removes the benefit, reject the fixed-word route without rescuing it with the two-word proxy. Prospective workload holdouts remain **sealed**. Kernellum PR #119 is unchanged.
