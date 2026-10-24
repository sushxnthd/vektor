# V296 prospective matched cap-margin repair discriminator — frozen 2026-10-23

**Mechanism:** V296 pairwise bank-conflict admission remains the only active architecture. V287 remains retired. This is a new, explicitly separate repair experiment; it does not rewrite or replace the original 3.5 ns nine-case and fixed-topology negative results.

## Hypothesis and predictions (frozen before execution)

Prior matched global-route experiments gave V296 nominal postrepair cell area **5299.784 um^2** versus **6165.348 um^2** for optimized one-hot control (14.039% less). A fixed-topology RC=2 test found **3 max-cap violations in both V296 and optimized**, with V296 still **+0.521799 ns** better modeled setup slack. Those are baseline observations, not outcomes of this experiment.

Hypothesis: **symmetrical preemptive electrical repair** at a 20% max-cap margin and 10% max-slew margin will remove routed max-cap violations without consuming V296's cell-area advantage. Apply **exactly two repair_design rounds** to all three designs, not only to the candidate or to designs that fail. Use one common 3.5 ns clock, Nangate45, 140x140 um die, 120x120 um core, 0.45 placement density, 0.005 pF output load, and identical synthesis/placement/routing scripts.

Prospective predictions:
- **Predicted-win regime:** nominal RC=1.0; candidate should remain smaller than *both* controls and have strictly better modeled setup slack with zero max-cap and max-slew violations.
- **Predicted-no-win/kill regime:** high RC=2.0; electrical margin may fail or repair overhead may erase area advantage. Report the result even if negative, without retuning.
- V296 and optimized control are functionally equivalent issue-decision mechanisms. **At the same 3.5 ns clock, predicted workload issue-throughput gain is 0%**, regardless of compute/memory/divergence regime. Do not reinterpret slack as measured frequency.

## Locked experiment

For each original / optimized / V296 and nominal / high RC, synthesize with the same Yosys/Nangate45 toolchain. Global place; run `repair_design -cap_margin 20 -slew_margin 10`, `repair_timing -setup`, detailed place; global route; record *pre-second-repair* electrical and timing. Re-estimate placement parasitics; repeat `repair_design -cap_margin 20 -slew_margin 10` on **all six cases**; detailed place, global route again, then record *post-second-repair* metrics and violating net names with OpenSTA `report_check_types -max_capacitance -violators -format end`. No conditional third pass, no changing constraints after outcomes.

## Pass/retire criteria

A **provisional** electrical result requires all six final cases: zero max-cap and max-slew violations, nonnegative setup slack at 3.5 ns, and V296 strictly smaller and strictly better setup slack than *each* control within each RC regime. A failed control cannot be excluded to manufacture a win. If candidate advantage disappears after equal repair, retire V296; if only electrical closure fails, preserve fail and pursue detailed diagnosis before any further repair (not an automatic pass). Independent parser must reject missing stages, wrong clock, missing final route and malformed numbers.

Even a pass is **not signoff**: global-route RC is not extracted detailed-route SPEF; no clock-tree, hold, power, tile or GPU-throughput evidence. Preserve sealed workload holdouts and all prior negative results. This experiment cannot establish novelty of pairwise hazard checking.
