# V296 one-shot symmetric upstream physical repair: frozen protocol (2026-10-28)

This is the **last bounded repair attempt for the existing integrated V296 tile-slice hypothesis**, not a new GPU architecture mechanism. The existing 2026-10-28 extracted-RC experiment #40675850164 is a negative baseline: V296 setup -1047.895 ps, hold -36.622 ps, 3 max-cap violations, area 17857.644252 um2; strongest fifth-stage serial setup -1859.922 ps, hold -19.796 ps, 3 max-cap violations, area 18953.830505 um2. Both fail the +250 ps setup guard, >=0 ps hold and zero-cap gate. Neither is a feasible comparator. No results from the older D4/D8 deferred-write trials may be mixed into this comparison.

## Intervention, frozen before execution
Retain the original `v296_tile_slice.sv`, 32 resident waves, 4 issue slots, 16 banks, exactly 2 read ports per bank, one global write port, same 3.5 ns clock, 2x extracted RC, density 0.45, floorplan, output loads and serial's extra fifth-stage pre-CTS repair. After the existing symmetric post-CTS setup/hold repair and **before detailed routing**, apply to BOTH contestants, in the same order:

1. tighten maximum fanout to 8;
2. detailed placement and re-estimate placement parasitics;
3. `repair_design -cap_margin 40 -slew_margin 40`;
4. `repair_timing -setup -slack_margin 2.200` (ns);
5. `repair_timing -hold -slack_margin 0.050` (ns);
6. continue unchanged detailed placement, global route, detailed route, SPEF extraction and independent audit.

A derived Tcl and runner must be SHA-locked to the original canonical scripts, with fail-closed source anchors. No source RTL edits, clock relaxation, area ceiling relaxation, asymmetric control downgrade or post-result retuning are permitted.

## Predictions and decision
**Prediction:** this aggressive physical intervention is unlikely to make *both* implementations feasible at the frozen constraints. The serial controller's setup deficit is 2109.922 ps, versus 1297.895 ps for V296. A positive result is allowed only with complete post-route extracted-RC artifacts and **both** contestants satisfying area <=30000 um2, setup >=+250 ps, hold >=0 ps, zero max-cap and max-slew violations and zero DRC. Also require >=1% area advantage and >=50 ps setup lead for the predeclared *non-GPU* physical-Pareto hypothesis. Incomplete, tool failure, or timeout is **censored**, not physical failure or a win.

At matched clock and latency, V296 and optimized serial are exactly admission-equivalent, so predicted **issue-throughput gain is 0** for both unsaturated and bandwidth-saturated regimes. No frequency, power, SRAM, GPU-tile or RTX-5090 equivalence follows from a physical area result. Even a hypothetical feasible physical result cannot establish a useful-throughput gain under a single-slice 30000 um2 ceiling.

**Stop rule:** If the completed matched run fails the feasibility/Pareto gate, reject the integrated V296 performance hypothesis. Do not repeat the same repair sweep with relaxed parameters. If censored, preserve logs and seek only a clearly justified, bounded evidence recovery, not open-ended CI iteration. Preserve the existing branch, draft PR #13 and all prior negative evidence. V287 remains retired. Kernellum PR #119 and its prospective holdouts are untouched.
