# V301 physicality pre-gate: four-way equal-entry control (frozen 2026-10-29)

## Motivation and admissibility

The opened V301 H1 advantage (+16.866% vs two-way set2) might reflect an artificially weak two-way set-associative control rather than a necessary eight-way CAM. Introduce **set4**, two sets with four entries each, same eight total queue entries, four ingress lanes, one scoreboard write port, identical warp/epoch OR semantics and lossless producer backpressure. It is a *stronger implementation candidate*, not yet equal silicon area; compare gate/route cost before architectural claims.

No changes to V301's mechanism, branch, PR, opened H1-H5 observations or their thresholds. The new set4 control is a falsification of the full CAM's necessity.

## Prospective unseen test, fixed before execution

Seeds 201..220 (20 independent seeds), 5000 offered cycles each. Freeze all settings:
- N1: offered=.65, warps=64, hot=.45, epoch_period=37. Predicted **set4 materially closes** the eight-way vs set2 gap. If set4 reaches >=95% of V301's drain-time event rate, eight-way loses its strong-control advantage.
- N2: offered=.82, warps=128, hot=0, epoch_period=128. Predicted no-win for V301 against the two-bank control.
- N3: offered=.80, warps=16, hot=.80, epoch_period=29. Predicted set4 near-tie with V301 (within 5%).
- N4: offered=.40, warps=64, hot=.35, epoch_period=11. Diagnostic short-epoch sensitivity; no claimed win.

All policies use capacity=8, ingress=4; banked has two write ports (not matched physical area). Check exact event conservation for every policy and report the mean of per-seed event rates, the set4/V301 ratio and max backlog. Do not modify these thresholds after inspecting outcomes.

## Decision

If set4 reaches >=95% of V301 on N1 and >=95% on N3, classify the eight-way CAM as **unjustified at simulator level** unless matched routed physical data shows an unexpected advantage. If set4 is worse, proceed to RTL, synthesis and extracted-RC comparisons; never call the synthetic result a GPU speedup. Independent reference checking and a real scoreboard bottleneck are still required.

## Known confounders

The original simulator drains an unbounded upstream backlog and aggregates same-epoch sector OR bits. This tests controller queue pressure, not GPU IPC, request dependencies, scoreboard reset correctness, or GPU energy. The scoreboards are one-port by assumption, not established for a commercial SM. No equal-area assertion is made until synthesis.
