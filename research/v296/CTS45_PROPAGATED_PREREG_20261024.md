# V296 matched propagated-clock CTS gate — frozen before execution (2026-10-24)

## Starting point and falsification target
Sole active architecture: V296 pairwise register-bank conflict admission. V287 retired. Existing branch `research/v296-pairwise-bank-conflict`, draft PR #13. No new mechanism or workload holdout opening.

The matched high-RC 45%-placement **pre-CTS detailed-route** experiment 40083815972 reported:
- Pairwise: 5987.926155 um^2, setup +0.418903 ns, hold +0.282110 ns, 0 slew/cap/DRC.
- Serial one-hot: 6942.599828 um^2, setup -0.173046 ns, hold +0.267903 ns, 0 slew/cap/DRC.
These are **ideal-clock** measurements. They are not propagated-clock results. In particular, the control's negative setup slack cannot be used to infer CTS infeasibility.

## Frozen CTS protocol
Rebuild each design from the existing RTL, using the exact same Yosys synthesis, Nangate45 technology, 140x140 die, 120x120 core, 3.5 ns clock, 0.15 ns I/O delay, 0.005 pF output load, 0.25 ns maximum transition, 45% placement target, and high-RC 2x as detail45. Apply exactly the existing first through fourth electrical/setup repair stages, with a fifth repair opportunity for **serial one-hot only**, BEFORE CTS. Perform OpenROAD `clock_tree_synthesis` with the same fixed CLKBUF_X1/X2/X3 cell list, CLKBUF_X3 root, and 20 um wire unit for both designs. Propagate clocks and run identical post-CTS setup/hold repair, placement, global routing, detailed routing and OpenRCX parasitic extraction. Record pre/post-CTS area, final area, max/min worst slack, DRC, slew/cap violations, routed DEF and SPEF. A clock tree inserted AFTER detailed route is prohibited. All source/tool/model hashes and partial logs must survive failed cases.

**A single common area ceiling is not strict equal-consumed-area matching.** Any candidate advantage is limited to this matched floorplan, control-advantaged effort and clock target. Do not use the pre-CTS area or slack as a CTS measurement. No claims of signoff, GPU speedup or RTX-5090 equivalence.

## Prospective predictions
1. Candidate will route and satisfy propagated-clock setup >= +0.050 ns, hold >= 0 ns, controller area <= 7400 um^2, zero slew/cap/DRC violations.
2. If BOTH contestants are physically feasible, V296 will retain >= 10% controller area reduction and >= 0.200 ns setup-slack lead. Otherwise the comparison must explicitly abstain from claiming a feasible-control Pareto win.
3. If V296's own CTS physical gate fails, or if both pass but either advantage disappears, record a negative result and recommend retirement/redesign. An incomplete run is INCOMPLETE, not a failure of the scientific prediction. No adaptive relaxation of clock, density, RC or area.
4. The post-CTS model must report *actual* propagated-clock setup and hold; ideal-clock numbers are prohibited in the final comparison.

## Research limitations and next steps
Even a CTS pass is not tapeout signoff. Verify CTS clock-cell area, extracted parasitic sensitivity, equal-consumed-area alternatives, switching activity/power, actual tile frequency bottlenecks, workload-level throughput/traffic, unseen workload boundary-law predictions, independent audit and prior art. Workload holdouts remain sealed. World-class completion gate: NOT REACHED.
