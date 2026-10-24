# V296 prospective third-round matched timing/electrical closure — frozen 2026-10-23 BEFORE execution

## Existing evidence and reason for this separate test

The completed **two-round** cap-margin experiment (Actions run 39967273689; report `CAP_MARGIN_SIX_CASE_FALSIFICATION_20261023.md`) remains a **failed** preregistered six-case physical gate: all six were electrically clean, but the original-control nominal case missed the common 3.5 ns setup target by 39.100 ps. V296 retained 13.989% / 13.564% controller-area savings and +0.388 / +0.489 ns modeled setup-margin advantages against the fastest control at nominal / high RC. These results must **never** be relabeled as a two-round pass.

**Sole active mechanism:** V296 pairwise RF-bank admission. No RTL mechanism change; V287 retired. Workload holdouts sealed.

## Frozen prospective predictions

1. A **third, symmetric** post-second-route `repair_design -cap_margin 20 -slew_margin 10` and `repair_timing -setup` followed by detailed placement and global routing will remove the original nominal 39.100 ps setup deficit, without introducing new max-slew/max-cap violations.
2. V296 will remain at least **10% smaller** than the smallest control, and retain at least **+0.30 ns** modeled setup slack over the fastest control, **in both RC regimes**. These stricter quantitative predictions are evaluated regardless of whether the basic gate passes.
3. The original high-RC control is near the setup boundary (+3.946 ps) and may fail under further changes; that outcome must be reported, not dropped.
4. Same-clock issue throughput improvement remains **0%** because issue decisions are functionally equivalent. No workload holdouts may be opened on this result.

## Fixed implementation protocol

Start from the **unchanged** `cap_margin_repair.tcl` two-round experiment, with the same pinned Yosys/OpenROAD/Nangate45 toolchain, original / optimized / V296, nominal RC=1.0 and high RC=2.0, 140×140 µm die, 120×120 µm core, 3.5 ns clock, 0.005 pF load, 0.45 placement density, 0.25 ns max transition. After its final global route, for **every** variant and RC case, perform exactly:

```tcl
estimate_parasitics -placement
repair_design -cap_margin 20 -slew_margin 10
repair_timing -setup
detailed_placement
estimate_parasitics -placement
# record area/slack/slew/cap
global_route -guide_file THIRD.guide -congestion_iterations 30
estimate_parasitics -global_routing
# record area/slack/slew/cap and violating endpoints; save THIRD.def
```

Do not add conditional passes, change constraints, or omit any control. Reuse the initial script through `source` without editing its previously frozen evidence path.

## Fail-closed gate and retirement

Require all six final third-route cases to have zero max-slew/max-cap violations, nonnegative setup slack at 3.5 ns, complete final DEF and all required stages, V296 smaller than **both** controls and with better setup slack than **both** controls. Independent checker must also evaluate the quantitative 10% / 0.30 ns predictions separately. **If equal symmetric repair erases the candidate's area or timing advantage in either RC regime, recommend retiring V296.** If a control still fails setup, report **PHYSICAL_GATE_FAIL** without relaxing the target.

Even a pass is only **global-route provisional**: no detailed-route SPEF, CTS/hold, power, tile, unseen-workload, or silicon result. The completed two-round experiment and its failure remain immutable.
