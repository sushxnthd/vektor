# V296 balanced-return post-CTS endpoint diagnostic: prospective protocol (2026-10-26)

**Evidence tier:** newly preregistered, matched **post-CTS global-route checkpoint** experiment. This is not extracted detailed-route signoff and cannot validate a GPU speedup. Retain the timed-out run 40244774412 and all original artifacts unchanged.

## Motivation and sole mechanism

V296 pairwise bank arbitration remains the **sole provisional architecture mechanism**; V287 is retired. In the previously frozen balanced-return physical run, both implementations failed the +50 ps setup guard at the post-CTS global-route checkpoint (pairwise −0.270312 ns, serial −0.842638 ns), and both 180-minute detailed routes timed out. Another three-hour route without diagnosing its setup cone would be uninformative.

## Frozen experiment and controls

1. Reuse **exactly** the original RTL, Yosys command, Nangate45 files, OpenROAD binary, 260 µm die/240 µm core, 0.45 placement density, 3.5 ns clock, propagated CTS, setup repair, serial-only fifth repair, 2x RC scaling and routing-layer constraints. No per-variant retuning.
2. Generate a derivative of the original frozen `cts45_tile.tcl` that stops **immediately before** `detailed_route`; append non-mutating `report_checks` for the worst ten setup paths, setup and estimated hold slack, slew/cap violators, and a post-CTS global-route DEF. Preserve complete tool logs and checksums. Never modify the original Tcl, RTL or prior workflow.
3. Run **both** pairwise and optimized serial, on separate hosted jobs, with an identical 75-minute upper bound. Fail closed if a job errors, report markers are missing, or output DEF is missing. An incomplete or canceled run is an **incomplete test**, not evidence of a feasible clock.
4. Classify each reported critical path by startpoint/endpoint and by its cells: scheduler/grant, RF bank selection, executed-data output, or other. Compare candidate and serial; report where the critical path **actually** resides before proposing any RTL repair.
5. Do not treat global-route estimates, estimated hold, zero estimated slew/cap counts, or DEF as final routed electrical closure. Full detailed-route SPEF, extracted setup/hold, DRC, equal-resource comparison, and unseen workloads remain mandatory.

## Frozen predictions and falsifiers

- **Expected checkpoint reproduction**: pairwise slack approximately −0.270312 ns and serial approximately −0.842638 ns under identical tool versions. Any substantial discrepancy requires a tool/source-hash audit before interpretation; do not silently replace historical results.
- **Predicted setup failure**: both checkpoints remain below +0.050 ns; an unexpectedly positive result must be reported as a falsification, not assumed to imply final signoff.
- **Hypothesis under test**: at least one nonclosing critical cone involves scheduler-to-executed-data RF return selection. If not, reject that repair target and report the actual critical cone.
- **Equal-resource falsifier**: even a smaller mapped/global-route area and better estimated slack cannot establish V296 superiority while either design fails final timing/electrical closure.
- **Workload predictions remain frozen**: at equal feasible clocks, exactly zero admission-throughput advantage; bandwidth-unsaturated traffic can benefit *only* from independently demonstrated clock/packing differences, while saturated traffic has no useful-throughput win.

## Decision

This trial is a bounded **physical-path localization experiment**. It is not a routing repair, post-route extraction, or a world-class completion gate. Next RTL intervention must be justified by these measured critical paths, applied fairly to the strongest serial control, and separately preregistered before its outcome.
