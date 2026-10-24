# V296 fourth-round high-RC electrical repair: prospective protocol (2026-10-24)

**Status:** frozen before implementation or evaluation. **Only active mechanism:** V296 pairwise bank-conflict admission. V287 remains retired. This is a *new* three-implementation high-RC experiment and does not retroactively alter the failed six-case detailed-route gate or open workload holdouts.

## Causal hypothesis
Read-only OpenSTA/SPEF replay reproduced the 33 maximum-slew violations and independently mapped **all 33** to the single 79-sink `issue_wave0[0]` net (INV_X32, 0.127312 pF, worst 0.281187 ns vs 0.250 ns limit). Hypothesis: a fourth **pre-detailed-route** electrical repair round with a stricter slew guardband splits/rebalances the fanout enough to eliminate the extracted violations without erasing the area/timing advantage. This is a *testable* physical hypothesis, not a guaranteed fix or new architectural mechanism.

## Frozen intervention and controls
- Rebuild original, optimized one-hot, and V296 from their same RTL/netlists using the exact existing pinned Yosys, OpenROAD, Nangate45 LEF/Liberty, OpenRCX and `hilomap` technology; **high RC only**, `V296_RC_SCALE=2.0`, extracted-RC multiplier `2.0`.
- Source the **unchanged** three-round `cap_margin_third.tcl` placement/repair/global-route flow. Apply exactly **one additional** identical, unconditional pre-detailed-route repair to **each** implementation: `estimate_parasitics -placement; repair_design -cap_margin 20 -slew_margin 25; repair_timing -setup; detailed_placement; global_route; estimate_parasitics -global_routing`. No design-specific commands, no clock/RC/load/max-transition relaxations. The only new knob is **25% rather than 10%** slew margin in this fourth round.
- Perform detailed route, require complete routing and DRC=0, extract SPEF with the same calibration, then measure post-extraction setup/hold slack, max-slew/max-cap count, cell area, and worst violators. Save DEF, SPEF, reports and logs for **all three**.
- Preserve `3.5 ns` shared clock, `0.25 ns` max transition, `0.005 pF` output load, original floorplan and I/O constraints, and the 20% cap margin.
- A missing case, invalid metric, unsupported tool command, or missing DEF/SPEF **fails closed**. Existing independent detailed-route checker remains unchanged. No auto-merge.

## Prospective predictions and decision
- **Prediction P1 (falsifiable):** high-RC V296's 33 post-route max-slew violations fall to **zero**, with zero cap and DRC violations and nonnegative extracted setup and hold.
- **Prediction P2 (falsifiable):** V296 remains at least **10% smaller** than the *smaller* of original and optimized control and retains at least **+0.20 ns** extracted setup slack lead over the *faster* control. This uses the measured pre-repair reference area budget `0.9*6939.142150-5985.266061=259.961874 um2` only as a **conditional** guide; the actual comparison must use *new same-run* controls.
- **Strong falsifier:** any remaining V296 slew/cap/DRC violation, negative V296 setup/hold slack, area saving below 10%, or timing lead below +0.20 ns means this fourth-round strategy **fails**. No fifth repair round without a new prospective mechanism/experiment and new control optimization.
- Even if P1/P2 pass, classify **TARGETED_HIGH_RC_PROVISIONAL_PASS**, **not** the frozen all-six gate, signoff, equal-resource Pareto victory or GPU throughput gain. The original/optimized controls may still miss the frozen 3.5 ns clock.
- An equal-area optimized-control Pareto sweep is still required before V296 can be accepted; allow the control additional timing optimization up to the same common area ceiling and retire V296 if it catches up. The existing frozen predicted-win/no-win workload holdouts stay sealed.

**Current physical evidence:** immutable detailed-route run 39995731088, independent read-only replay 40018972185, and live-state reproduction 40019129042. No result from this prospective fourth-round experiment existed when this protocol was frozen.
