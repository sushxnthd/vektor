# V317 frozen legal-load transfer gate (2026-11-01)

## Purpose and scope
This is a **prospective**, narrowly scoped falsification of the V317 pairwise fixed-priority bank-credit implementation's pre-route Nangate45 timing advantage. The older 2/20/40/60/80/100 fF sweep is opened calibration evidence; the **10 fF** and **30 fF** loads below have not been evaluated by this protocol. The 24 and 26 fF probes are exploratory boundary localization, not holdouts. Keep the same source RTL, pairwise RTL, Nangate45 Liberty commit/blob, Yosys synthesis recipe, OpenSTA script, input transition (0.02 ns), output load units (fF), and four-slot/sixteen-bank configuration.

## Frozen directional predictions, before opening the new runs
- **Predicted-win legal-load regime, 10 fF**: source-fixed and pairwise-fixed both pass every reported max-transition check; pairwise has a strictly lower worst grant-output data arrival, with **at least 0.40 ns** advantage. These are cell-delay and electrical checks only, not throughput claims.
- **Predicted-no-win electrical regime, 30 fF**: source-fixed and pairwise-fixed both violate at least one max-transition constraint. Any raw cell-delay advantage at this load is **electrically inadmissible**; do not report it as a physical win.
- **Exploratory 24/26 fF**: report complete electrical status and raw timing, but do not score predictions at these loads.
- **Never** interpolate or extrapolate a legal crossover from electrically failing loads. Max-capacitance remains unverified in this legacy OpenSTA version.

## Falsification and integrity
Independent checker must parse bounded timing and concrete max-transition tables for every label/load. Missing rows, errors, unconstrained paths, nonpositive arrival, absent limits, or violated 10-fF legality fail the gate. If 30 fF is electrically legal for either variant, the frozen no-win prediction is falsified; preserve that outcome. If the 10-fF timing margin is <0.40 ns, the win prediction is falsified. Check both prediction outcomes even if one fails; emit JSON with raw values before exit failure. The checker must not silently relabel an invalid load as a valid speedup.

## Analytical boundary (conditional, not measured)
At fixed bank ports, identical grant decisions imply **1.000x intrinsic scheduling completions/cycle**. For a fixed pairwise implementation to be superior in total tile throughput, its area savings must actually allow additional resource replication or its cell timing must improve a **measured** critical tile path; neither is established. The unmeasured extra routed delay difference must satisfy
`(wire_pairwise - wire_source) < (cell_source - cell_pairwise)`
for the cell-delay ordering to survive, with all max-transition, max-capacitance and setup constraints independently passing. Report the 10-fF measured headroom as a conditional bound, never as routed closure. Source-fixed mapped area 798.798 um^2 and pairwise-fixed 259.616 um^2 are **previous** pinned mapped synthesis results, not new placement.

## Strong controls and kill rule
Keep rotating-priority and oldest-first controls as fairness baselines; their prior synthetic queue advantage does not justify a novel mechanism, and their electrical legality has not been repaired. Pairwise fixed is an **implementation optimization** and remains the sole active V317 implementation question. No V287 revival, no new architecture mechanism, no RTX 5090 equivalence. Preserve negative results, the draft PR, and Kernellum PR #119. Next physical gates are matched buffering/remap, max-capacitance checks, placed/routed RC, power and tile-level performance.
