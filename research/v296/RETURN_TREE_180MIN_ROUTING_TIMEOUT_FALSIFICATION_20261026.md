# V296 balanced-return integrated slice: routed timeout and congestion falsification (2026-10-26)

**Evidence tier:** Retrospective SHA-locked forensics of the original, unchanged matched physical experiment. Not a preregistered new physical trial, not completed routing, and not a GPU speedup. Original frozen protocol remains `RETURN_TREE_INTEGRATED_REPAIR_PREREG_20261026.md`.

## Experiment status and reproducibility

[GitHub Actions run 40244774412](https://github.com/sushxnthd/vektor/actions/runs/40244774412) finished **cancelled**, not successful. Both physical jobs reached the specified **180-minute** timeout while OpenROAD detailed routing was still optimizing. The independent aggregate correctly failed closed with `INCOMPLETE_NO_TILE_PHYSICAL_CLAIM`. Hosted four-way RTL and four-way mapped synthesis **passed separately**; neither establishes post-route closure.

Original archived evidence:
- Pairwise artifact **12624420514**, `pairwise.high.log` SHA-256 `9f68536beace12b49ccbc33b29a1b0d5b3b1f6c6ea3d598366ee50784700bf9b`.
- Serial artifact **12624490016**, `serial_onehot.high.log` SHA-256 `b4d3b78618d81debd6ff733d9799ec95ad691937162c9ca320aebe4b51a32678`.
- Independent aggregate artifact **12623966404**; source runner and physical logs are preserved, not rewritten.

Use `python3 research/v296/return_tree_timeout_forensics.py --self-test`. Download both original artifact ZIPs from the run and execute `python3 research/v296/return_tree_timeout_forensics.py --pairwise PAIRWISE.zip --serial SERIAL.zip`. The checker rejects mutated SHA, inconsistent DRT iteration counts, incorrect floorplan, missing post-CTS checkpoint, and any unexpectedly completed run. [Frozen results](RETURN_TREE_TIMEOUT_FORENSICS_RESULTS_20261026.json) provide compact, independently reviewable values.

## Physically meaningful intermediate findings

| Matched checkpoint | V296 pairwise | Optimized serial |
|---|---:|---:|
| Post-CTS **global-route** cell area | 16,509.556 µm² | 19,443.270 µm² |
| Post-CTS global-route **reported** worst slack | −0.270312 ns | −0.842638 ns |
| Deficit to +0.050 ns setup guard at this checkpoint | 0.320312 ns | 0.892638 ns |
| Estimated slew / cap violations at this checkpoint | 0 / 0 | 0 / 0 |
| DRT violations after iteration **0** | 21,257 | 27,937 |
| DRT violations after **matched iteration 8** | **9,672** | **4,480** |
| Last *completed* DRT iteration | 8 | 14 |
| Last observed DRT violations | 9,672 | 390 |
| Completed detailed-route SPEF / final extracted STA | **No** | **No** |

At the shared post-CTS global-route checkpoint, V296 shows **15.0886% lower cell area** and **572.326 ps better reported slack**, but **both** miss the +50 ps setup guard. The reported slack is an intermediate OpenROAD estimate; it is **not** final routed extracted STA, and the estimated zero slew/cap counts are **not** final electrical closure.

The DRT trajectory reveals a potentially important counterpressure: at the **same completed optimization iteration 8**, the candidate has **9,672** outstanding DRC violations versus **4,480** for serial. These are intermediate router counts, not signoff. Comparing counts at a common iteration is not a comparison at equal CPU time or matched convergence, and cannot establish that V296 intrinsically routes worse. The candidate had *fewer* initial violations (21,257 vs 27,937), so simple one-point congestion claims are especially misleading. The serial route progressed to iteration 14 with 390 violations before its own 180-minute timeout; neither route converged to zero.

## Scientific decision

**The balanced-return implementation has NOT crossed the integrated physicality gate.** The mapped-area and pre-route slack advantages remain observations, but any claim of integrated frequency improvement, physically realizable packing, energy reduction, or tile throughput gain is rejected until matched complete routes close setup/hold/slew/cap and equal consumed resources are enforced. Both physical jobs timed out, so this is an **incomplete test**, not a definitive architectural kill.

The next trial must be **newly preregistered**, with a bounded stage/checkpoint plan and identical candidate/control constraints. First investigate the non-closing post-CTS setup cones and DRT convergence using existing artifacts; do not simply increase timeouts and rerun the same uncontrolled three-hour route. A checkpointed or smaller cone experiment may guide optimization but cannot substitute for final matched full-slice routing. Retain the original failed artifacts unchanged.

V296 remains the sole provisional architecture mechanism. V287 is retired. Four-way same-clock admission equivalence implies **exactly 0% same-clock admission throughput difference**. No GPU speedup, measured power benefit, RTX-5090 equivalence, or successful physical signoff is claimed. Kernellum PR #119 and all prospective holdouts remain untouched.
