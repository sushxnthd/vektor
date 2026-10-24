# V296 single-case live extracted-route slew-endpoint diagnostic (frozen 2026-10-24)

**Separate diagnostic experiment.** Sole mechanism V296; V287 retired. The six-case extracted gate from run 39995731088 remains **FAILED**. No controls, clock, RC, area budget, or retirement thresholds are modified.

## Motivation and reproducibility hazard
The original detailed-route artifact includes routed DEF and SPEF but not the full live postrepair OpenROAD/STA database. Replaying that state from pre-repair synthesized Verilog loses repair-added instances (`max_cap*`, `load_slew*`); DEF-only replay has triggered a pinned Resizer crash. Neither failure is evidence that the original 33 high-RC slew violations disappeared. Read-only SPEF parsing independently reproduced load-concentration statistics but cannot identify actual slew endpoints.

## Frozen experiment
- Run **only V296/high RC** through the **unchanged original** synthesis, three-round symmetric pre-route repair, detailed routing and extracted-RC Tcl sequence. Use the same Yosys, pinned OpenROAD 2024-12-14, Nangate45 models at revision `eda8e552974d47a12616294dddf4012d892548d3`, 3.5 ns clock, 2x RC, and 0.25 ns max transition.
- **After** the original extracted metrics, while the live OpenROAD/STA state still exists, print the complete `report_check_types -max_slew -violators -format end` block, cap block, area, extracted setup/hold, and routed DRC. No new repair or resizing after detailed route.
- Prospective reproducibility targets from the frozen original artifact: **33 slew violations**, **0 cap**, **0 DRC**, **5985.266061 um2**, **+0.361922 ns setup**, **+0.283003 ns hold**. The independent checker uses the preregistered tolerances **0.01 um2** area and **0.005 ns** for each slack.
- A mismatch fails the exact replay gate; preserve the raw report and treat it as implementation/tool reproducibility evidence, not as electrical closure. A matched endpoint table must be derived from the reported violating pins, not inferred from high capacitance alone.
- The diagnostic does **not** establish a repaired clean V296 or a matched-resource win. The next experiment must freeze targeted post-route repair and independently optimized controls under a common area ceiling before evaluating PPA.

**Kill boundary unchanged:** retire V296 if fully clean equal-resource optimization eliminates its strict controller area/timing dominance. No workload holdouts opened. No GPU performance, power or signoff claim.
