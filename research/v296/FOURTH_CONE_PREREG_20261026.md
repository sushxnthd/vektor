# V296 paired pre-CTS fourth-route critical-cone localization: prospective protocol (2026-10-26)

## Motivation and frozen negative evidence

Hosted post-CTS diagnostic run 40263375059 failed for both contestants. Immutable pairwise artifact 12626562335 (ZIP sha256 `6c1d43d33dab96fd67721479f5987ad68c12f323aeede396df31cc8b4eccacc5`) reached `cts45_postcts_global` at area 16509.556389 um², setup slack -0.270312 ns, but exited on `STA-0563` because `report_checks -group_path_count` is unsupported in the pinned OpenSTA. Immutable serial artifact 12627673135 (ZIP sha256 `ba1ab686ea81720bed3c4cf9cd9988ee0607e527b3670286e08be80eba234570`) timed out at 70 minutes during post-CTS setup repair; it had reached `cts45_clock_tree` at area 18785.451417 um², setup slack -1.003700 ns. Neither completed the matched post-CTS diagnostic. Both failures are preserved and must not be called an electrical win.

## Intervention frozen before execution

Run both variants through the **identical first four** pre-CTS optimization rounds and stop directly after `cts45_fourth_routed` and its global-route estimated parasitics. No serial-only fifth repair, CTS, detailed route or RC extraction is performed. Both share original RTL, die 260 um, core 240 um, 3.5 ns clock, 0.45 placement density, high RC 2x, 16 banks, two read ports/bank, four issue slots, and exact common Tcl prefix. No RTL or architecture mechanism is changed. This is a **cone-localization** experiment only: the fifth serial rescue is intentionally excluded, so its timing/area results cannot be used to claim a strongest-control architectural advantage.

The generated Tcl must contain a single `report_checks -path_delay max -fields {slew capacitance fanout} -digits 6`, a corresponding min path, setup/hold worst slack, and a fourth-stage DEF. Avoid unsupported `-group_path_count`. The runner must exit before CTS or detailed routing, and must preserve both successful and failed logs. Require exactly one common fourth-stage anchor; reject drift in the source Tcl/runner. Do not reuse or overwrite the original failed diagnostic.

## Prospective decision rules

1. PASS only if both paired jobs complete within 55 minutes each and their logs contain path startpoint, endpoint, complete path reports, and fourth-stage DEF. Reject incomplete, timed-out, or tool-failed jobs.
2. Map the measured endpoints to RTL cones with independently audited netlists. A new RTL intervention is permitted only after the path mechanism is identified and applied symmetrically to both contestants; retain optimized serial fifth-stage rescue for the *final* matched physical gate.
3. Any apparent slack or area advantage here is intermediate and cannot support a GPU speedup claim. Final decision still requires post-route extracted setup >= +0.050 ns, hold >= 0, no electrical/DRC violations, equal consumed area, bandwidth-constrained workload advantage, and unseen-regime predictions. At the same issue count and clock, V296 and serial admit identical waves.

V296 remains the only active mechanism; V287 is retired. Kernellum PR #119, all holdouts, and other branches remain untouched. No RTX-5090-equivalence claim.
