# V296 deferred-write matched D4/D8 extracted-RC routed transfer: prospective protocol (2026-10-28)

## Question and provenance
The corrected [pre-CTS four-way run #40640100044](https://github.com/sushxnthd/vektor/actions/runs/40640100044) completed successfully at commit `ae7a90ad28a3ed795156b98b50e9cf21eadfaf59`, with independent aggregates at both depths. This is estimated-RC global-route evidence, **not** routed signoff. This preregistration is committed **before** the new extracted-RC outcomes.

| Depth | Candidate pre-CTS area (um2) | Strong serial pre-CTS area (um2) | Candidate setup (ns) | Serial setup (ns) |
| --- | ---: | ---: | ---: | ---: |
| D4 | 18794.230172 | 20763.694764 | +0.381283 | +0.150760 |
| D8 | 25645.858770 | 26891.802563 | +0.214891 | +0.110820 |

## Immutable mechanism and physical contract
- Sole architecture mechanism: **V296 pairwise bank-conflict admission**. V287 retired. This trial changes implementation retiming only, not admission, RF banking, scheduler semantics, or algorithm.
- Compare same-depth `PAIRWISE=1` against **strongest serial one-hot controller** `PAIRWISE=0` with the existing serial-only fifth-stage physical repair. Both use identical deferred-write RTL, 16 banks, two dynamic RF read ports/bank, one global write port, four issue slots, 3.5 ns clock, 2x RC, 0.45 density, 260 um die / 240 um core, same Nangate45 technology, OpenROAD/Yosys versions and Tcl. No extra ports, no asymmetric timing fixes, no clock relaxation.
- Derive the existing `deep_bank_postcts.build(bits)` physical runner; substitute only `v296_tile_slice_deep_bank` with already validated `v296_tile_slice_deferred_write` **symmetrically**. Preserve `cts45_hold25_tile.tcl` byte-identically, including CTS, propagated clocks, hold repair margin 25 ps, detailed route, extracted parasitics, electrical checks and DRC. No edited route Tcl.
- Four independent bounded contestants: D4 candidate/serial, D8 candidate/serial. Record original exit codes, tool versions, SHA-pinned source and generated inputs, logs, DEF/SPEF, route DRC, extracted setup/hold, cap/slew and area. Timeouts and incomplete evidence are failures/censored, never silently excluded.
- An independent fail-closed aggregate must verify matching depth, source/Tcl hashes, complete route markers, both contestant results and original physical checker. A green workflow **alone** is not a physical pass; aggregates must explicitly report physical verdict.
- Accept a depth only if both contestants complete routed extracted-RC analysis with >=+50 ps setup, >=0 hold, zero cap/slew and DRC violations, <=30000 um2 area. Additionally require >=1% candidate area reduction and >=50 ps candidate setup lead to support the preregistered slice Pareto hypothesis. Any failure rejects the depth.
- The occupancy/retiming throughput law remains mandatory; the new extra operand cycle is not a GPU performance win. Workload holdouts remain sealed. Do not claim SRAM macro signoff, power, full-tile advantage or RTX-5090 equivalence.

## Predictions frozen before outcomes
- **Predicted-win regime:** D4 with lower RF density, where pre-CTS candidate saves 1969.464591 um2 and leads setup by 230.523 ps. Prediction: both close extracted-RC timing/electrical and candidate retains >=1% area and >=50 ps setup lead. Falsify on any failed condition.
- **Predicted-no-win regime:** D8 with higher RF density and smaller 1245.943793 um2 area and 104.071 ps setup lead. Prediction: at least one of the routed feasibility/Pareto gates fails. Falsify if the entire matched D8 pair passes all gates. These are hypotheses, not empirical outcomes.
- **Necessary fixed-geometry perturbation envelopes (not guaranteed route outcomes):** pre-CTS candidate setup may degrade at most 331.283 ps (D4) or 164.891 ps (D8) to retain +50 ps; serial at most 100.760 ps (D4) or 60.820 ps (D8). The pre-CTS area margin may be erased by differential added area >=1969.465 um2 (D4) or >=1245.944 um2 (D8). Path migration, clock-tree changes and congestion invalidate naive additive extrapolation.

## Decision
If both depths fail, retire deferred-write as a physically demonstrated V296 repair and preserve the negative results. If one depth passes, keep V296 **provisional** pending occupancy-adjusted measured-clock workload prediction, power proxies, wire/load sensitivity, unseen transfer, prior art, independent checker and tile integration. Keep one branch and draft PR #13; never merge or force-push.
