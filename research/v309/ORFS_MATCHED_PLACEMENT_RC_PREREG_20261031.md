# V309 matched placed-RC prefilter: prospective protocol (2026-10-31)

**Status at commit:** protocol only; no placed result has been observed. This is a physical experiment on the **existing single factored exact-max bank-admission mechanism**, not a new architecture candidate. Do not resurrect V287/V296.

## Matched controls and fixed conditions
- Same Nangate45 ORFS platform, OpenROAD container, synthesis/placement flow, 36 input bits and four output bits; same 1.0 ns virtual-clock I/O constraint, 0.050 ns input transition, 0.020 pF output load.
- Competent compact-greedy same-priority implementation is the **primary baseline**. Original greedy is not an acceptable comparator.
- Two **identical** die/core geometries per candidate/control pair: dense die 30x30 um, core 3..27 um; relaxed die 45x45 um, core 4.5..40.5 um. Fixed floorplan geometry is a stress-test convention, not a claimed tile layout. Identical placement effort and placement density 0.65.
- Stop at ORFS placement; read each actual 3_place.odb, use Nangate45 metal3 signal-wire RC and OpenROAD `estimate_parasitics -placement`, then independently parse the maximum input-to-output data-arrival path and preserve electrical reports.
- Preserve complete ORFS logs, placed databases, source commit, container digest, versions, and failure outputs. The container image must be identified by digest at execution. Reproducibility is not established if external image/ORFS version drifts.

## Frozen predictions and kill conditions (before outcomes)
- Hot2 iid issue-admission ratio is 1.0973483338585934 from the previous prospective equality-partition law. At each matched placement, the **optimistic clock-limited upper bound** is `1.0973483338585934 / (D_candidate / D_compact)`. If the **worst** tested placement has an upper bound <= 1, kill the factored implementation for this predeclared clock-limited scenario; do not quietly replace the mechanism.
- Uniform8 predicted issue ratio is 1.007648758; at this near-no-win regime, even a small frequency, queue or occupancy penalty can erase gain. Do not claim throughput based on ideal issue counts.
- An upper bound > 1 does **not** pass the world-class gate. Require no max-slew/cap violations, realistic extracted routed RC, matched area/clock/power, and integrated trace-driven throughput including occupancy, scoreboard, ports and bandwidth. Any such gate can still kill V309.
- Do not equate OpenROAD placement-estimated parasitics with routed/extracted RC, GPU silicon, or RTX 5090 equivalence.

## Independent audit
The checker must reject missing placement markers, OpenROAD errors, missing paths, and required-time-as-arrival false positives. The electrical report is retained **but cannot be called clean** until an independent machine-readable violation-count audit is implemented. CI failure is evidence of a tool/physical blocker and must not be reclassified as a scientific pass.
