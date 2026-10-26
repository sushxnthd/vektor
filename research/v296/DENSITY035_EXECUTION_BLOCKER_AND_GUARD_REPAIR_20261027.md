# V296 density-0.35 diagnostic: execution blocker, falsification of the attempted run, and controlled repair (2026-10-27)

## Result of original hosted attempt (run 40406533602)

**Verdict: INCOMPLETE, NO DENSITY CAUSAL TEST, NO PHYSICAL OR GPU CLAIM.** Both paired contestants completed synthesis but **neither entered placement or detailed routing**. The original frozen thresholds at detailed-route iteration 3 (candidate DRC <= 8,414 AND candidate/control ratio <= 0.75 of the original 12,020/5,281) were therefore **not evaluated**. Do not substitute zero violations, a failure of the hypothesis, or a successful physical result.

The independent audit job failed because no completed iteration-3 logs existed. The actual physical-tool failure was earlier: both `pairwise.high.log` and `serial_onehot.high.log` contain only the OpenROAD startup header and `Error: cts45_tile.tcl, 9 CTS45 frozen high-RC 2x and placement density 0.45`. This was masked in the console by the later, expected independent-audit message `Missing or duplicate integrated floorplan marker`. It is a **safety guard mismatch**, not a routing/congestion observation.

### Original artifact integrity

- Candidate: artifact 12693000294, ZIP SHA-256 `e69bc519eec8e621bbd7f4c69ab19eca83b074fab90407615263931291737c1f`.
- Optimized fifth-stage serial: artifact 12690453278, ZIP SHA-256 `06331a9aa8cfcec35981717607d1429736b71471aa6c24a3eed617667f780d94`.
- Source workflow run: https://github.com/sushxnthd/vektor/actions/runs/40406533602
- Original reference density-0.45 route run: https://github.com/sushxnthd/vektor/actions/runs/40359299905

Both ZIP hashes were independently verified against the downloaded original bytes. Both `cts45_tile.tcl` files contain the explicit assertion `$env(V296_PLACE_DENSITY) ne "0.45"` followed by the error above. The density-0.35 shell runner sets `V296_PLACE_DENSITY=0.35`, so the guard necessarily fails. The parent `tile_slice_flow.py` generates this guard from the canonical frozen Tcl. The old density-0.45 experiment is preserved.

## Controlled, transparent execution repair

The original preregistration remains **unchanged**. For a new diagnostic attempt, derive a separately named `cts45_tile_density035.tcl` from the canonical generated `cts45_tile.tcl`, changing **only** the exact expected-density assertion and corresponding error message from `0.45` to `0.35`. The original Tcl, original density-0.45 runner, physical commands, 3.5 ns clock, 2x RC, floorplan, routing policy, source RTL, fifth-stage serial-only optimization, and prior artifacts must remain byte-for-byte unchanged. The trial runner changes only its density assignment and its reference to this separate diagnostic guard Tcl. All original and derived file hashes must be recorded and checked.

This is a disclosed **execution-protocol amendment** required to run the intended density-only physics intervention, not evidence that the frozen density-0.45 signoff was met. It corrects a guard expectation; it must not relax any timing, electrical, area, DRC, or workload acceptance threshold. The original frozen iteration-3 DRC thresholds remain fixed without retuning.

A second hosted run must show that both contestants pass the density guard and reach the same iteration-3 checkpoint. Until then the packing-causality hypothesis is **untested**. If the amended diagnostic still fails before the checkpoint, report INCOMPLETE and investigate its actual error, rather than treating a tool failure as a scientific negative.

## Architectural status

V296 remains the sole provisional architecture mechanism; V287 is retired. The original density-0.45 V296 detailed route was right-censored with 7,930 outstanding DRC at completed iteration 8, while serial eventually routed but failed setup/hold/capacitance. No routed feasible equal-resource V296 GPU speedup, power advantage, or 5090 equivalence has been established. Kernellum PR #119 and sealed prospective holdouts are untouched.
