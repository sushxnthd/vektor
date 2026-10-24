# V296 control-advantaged Pareto challenge, frozen before implementation (2026-10-24)

**Only active mechanism:** V296 pairwise bank-conflict admission. V287 retired. This is a NEW high-RC detailed-route experiment; it does not change the failed six-case extracted-RC gate or the fourth-round targeted pass. All workload holdouts remain sealed.

## Falsifiable question
Can the strongest one-hot or original arbitration control, given *more* physical optimization effort than V296, eliminate V296's measured high-RC area/timing advantage while meeting the same electrical and timing constraints? Prior control measurements were physically infeasible, so no equal-resource superiority has yet been established.

## Frozen contestants and physical constraints
- Original RTL `vektor_issue_control`; serial one-hot V295 with `PREDECODE=0`; parallel one-hot V295 with `PREDECODE=1` (new adversarial control); V296 pairwise. All retain identical scheduler, wave state, bank ports, issue interface and clock.
- Independently synthesize each from RTL using the same pinned Yosys/ABC, Nangate45 typical library, tie-cell mapping, placement and 140 x 140 um die/120 x 120 um core. No reuse of another variant's placed or routed design.
- Shared 3.5 ns clock, 0.25 ns maximum transition, 0.005 pF output load, high RC 2.0 in routing and extracted SPEF, fixed LEF/Liberty/OpenRCX, fixed pin layers and placement density.
- All four receive the existing three-round flow followed by exactly the previously tested fourth repair (20% cap margin, 25% slew margin) before detailed routing.
- **Controls only** then receive one *additional* unconditional `repair_design -cap_margin 20 -slew_margin 35`, `repair_timing -setup`, detailed placement and global reroute before detailed route. V296 does NOT receive this fifth pass. This is deliberately control-advantaged, not a claim of equal optimization effort. If the control-advantaged route still loses, the evidence is stronger, but not a global optimality proof.
- Complete detailed routing and OpenRCX SPEF for every contestant. Preserve logs, DEF, SPEF, DRC reports, technology hashes, synthesized netlists and per-stage metrics. Missing cases or malformed evidence fail closed. Pre-CTS ideal-clock hold is not post-CTS hold closure.

## Prospective hypotheses and decisions
- H1: V296 retains zero extracted max-slew/max-cap/DRC violations, nonnegative setup/hold, and at least 10% lower controller cell area plus >=0.20 ns setup-slack lead relative to the best control measured in this NEW run. If H1 fails, **retire or re-evaluate V296** rather than claim a win.
- H2: at least one control becomes electrically clean, routed and setup/hold feasible at 3.5 ns under its extra optimization. If none does, classify `NO_FEASIBLE_CONTROL`, **not** a Pareto victory, even if H1 holds.
- **Common physical area ceiling:** 7400 um2 for each contestant. A control above the ceiling is ineligible for equal-resource comparison. An area-feasible control is **area-matched** only if its area is <= the candidate's measured area, with no borrowing unused area from another design. If no feasible area-matched control exists, classify `NO_AREA_MATCHED_CONTROL`, not an equal-area victory.
- Kill V296 if any fully feasible control with area <= V296 achieves equal or better extracted setup slack, or if the candidate fails electrical/timing closure or its preregistered area/timing advantage against the strongest measured control disappears. If the controls are larger but clean, retain only a bounded area/timing Pareto observation, not a strict equal-area validation.
- No clock-frequency claim from setup slack alone; no throughput gain at the fixed clock. Keep the existing predicted-win and predicted-no-win tile/workload regimes frozen. No CTS, foundry signoff, dynamic power, or RTX-5090-equivalence claim.

## Independent audit
A separate fail-closed checker will verify all four distinct variant logs, frozen markers, complete detailed route, nonempty SPEF/DEF, finite extracted setup/hold, electrical counts and DRC, and report every feasible control plus both resource-matching and physical Pareto conditions. Scientific failure is retained as a result; no post-hoc constraint relaxation or silent removal of an inconvenient control.
