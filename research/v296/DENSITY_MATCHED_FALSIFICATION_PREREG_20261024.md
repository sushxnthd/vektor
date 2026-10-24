# V296 matched-floorplan placement-target falsification — preregistration (2026-10-24)

## Immutable motivation and decision

The four-way 65% target-density global-route experiment (run 40069058725) **failed**. V296 reached global route at 7,911.106 um^2, +0.004863 ns ideal-clock setup slack and two max-cap violations; the other controls stopped at earlier stages. The 45%-target extracted-SPEF V296 measurement (5,987.926 um^2, +0.418903 ns, zero electrical violations) used a different experiment and cannot be compared causally. This protocol tests the target-density dependence without changing the die, core, library, timing or RC conditions. Prior evidence is never overwritten.

**Only V296 pairwise bank-conflict admission is active.** V287 is retired. Same persistent research branch and draft PR #13. No workload holdouts opened.

## Frozen physical settings

Compare **pairwise V296, serial one-hot and original** at **two placement targets, 0.45 and 0.65**, independently synthesized from the same sources, with exactly the same 140 x 140 um die, 120 x 120 um core, 3.5 ns clock, 0.15 ns input/output delays, 0.005 pF output load, 0.25 ns max transition, Nangate45 library, pinned Yosys/OpenROAD, 2.0x wire RC, signal metal2–metal10, 20% capacitance repair margin and original Tcl. Every contestant gets four identical rounds; controls receive the additional fifth round (35% slew margin) as in the prior control-advantaged experiment. Only the placement target changes across the two density groups. Each of the six contestants executes in a separate job with retained partial logs and netlists.

The two **frozen predictive regimes** are:
- **Predicted-win feasibility regime**: at 0.45, V296 is expected to complete global route, satisfy A <= 7400 um^2, zero max-slew and max-cap violations, and have >= 0.050 ns ideal-clock setup slack. This is a falsifiable prediction; it is not an equal-resource victory or a GPU throughput win.
- **Predicted-no-win feasibility regime**: at 0.65, V296 is expected to repeat failure of at least one of the same necessary constraints. Any global-only pass at 0.65 falsifies this prediction; a missing or timed-out record is **inconclusive**, not confirmation.

The 0.45 and 0.65 groups are **not held-out workloads**. They are a prospective implementation-sensitivity test against earlier mixed-tier observations. Do not retrospectively call them blind holdouts. A new 0.55 density point, if pursued, must be frozen in a subsequent separate prospective test.

## Decision law and explicit gate

For a contestant j and target d define:
F_j(d) = 1[complete global route and A_j(d) <= 7400 and slew_j(d)=0 and cap_j(d)=0 and slack_j(d)>=0.050 ns].
Incomplete evidence yields F_j(d)=unknown, never zero or one. The 50 ps margin is a conservative *pre-CTS* guardband, not a guarantee of CTS closure.

Report the measured feasibility boundary for V296, **not** a universal monotonic threshold inferred from two points. At each matched density compare area and slack only if both designs reach equivalent global-route stages. Against the strongest feasible control, declare V296's **global-only Pareto advantage** only when both candidate and control have F=1 and V296 area is strictly smaller and its setup slack strictly greater. If no control is feasible, label it **no feasible-control comparison**, never an architectural victory. A common 7,400 um^2 ceiling is **not** strict equal-consumed-area matching.

The checker must independently validate contestant identity, density, clock, global-only marker, repair entitlement, final DEF, final metrics and non-finite values; preserve the last completed stage on errors; reject partial stages as matched PPA. Do not merge this result into the previous 65%-density failure.

## Falsification and next physical tier

Retire or redesign V296 if the lower-density experiment cannot achieve electrical/area/setup feasibility, or if a matched feasible control catches up in area and timing. A success at 0.45 is **only global-route necessary feasibility**; the next gate is matched detailed-route/SPEF, CTS, realistic switching-power evidence, strict resource matching and workload/tile-level predictions. No RTX-5090 equivalence or throughput gain claim.
