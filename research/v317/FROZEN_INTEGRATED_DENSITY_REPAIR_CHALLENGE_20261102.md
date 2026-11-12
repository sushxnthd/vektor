# V317 prospective legal-source density-repair challenge (frozen 2026-11-02)

## Motivation and immutability
The independent six-route [held-out audit](RF_INTEGRATED_SEED_CHALLENGE_FALSIFICATION_20261102.md) found that source missed 2 ns by just 3.063 ps at seed 7, while pairwise closed all three frozen seeds. Source could be repairable by a legal placement tuning choice, without changing the RTL or adding hardware. The test is adversarial against the claim that pairwise is necessary for timing closure. The seed 7 selection is **post-hoc tuning** (best source slack in the previous set), **not a new unseen holdout**.

## Freeze before results
- Keep same source and pairwise RTL, 356 FFs, Nangate45 typical, pinned ORFS image, 2.000 ns SDC, 10-fF loads, 120 x 120 um die and 112 x 112 um core, ABC_AREA=1, GPL_TIMING_DRIVEN=1, GPL_RANDOM_SEED=7.
- Change only `PLACE_DENSITY_LB_ADDON` from the opened baseline 0.20 to **0.05 and 0.35**, separately for source and pairwise. These are both legitimate OpenROAD lower-bound density add-ons; [ORFS variable documentation](https://openroad-flow-scripts.readthedocs.io/en/latest/user/FlowVariables.html) and [implementation](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/flow/scripts/util.tcl) confirm the addon changes actual target density. Do not merely change `PLACE_DENSITY` because the addon overrides it.
- Four routes, all logs/RC/report JSON preserved. Record actual computed placement density in global placement logs. A parameter not taking effect invalidates the intervention.
- Legal means successful route AND zero final DRC/antenna, nonnegative setup/hold slack, zero setup/hold/max-cap/max-slew/max-fanout violations. A make exit code of zero alone is insufficient.
- Compare each matched-density pair, then best **legal** source against best **legal** pairwise across density settings and earlier seeds. Keep failures and unsuccessful repairs.

## Frozen falsification targets
1. A source route with setup slack >=0 and all electrical checks clean disproves the restricted assertion that source is intrinsically incapable of closing 2 ns at this die/core and library.
2. Pairwise may lose some area/power advantage when source is tuned; measure, do not assume a win.
3. If source stays setup-illegal, this is evidence only against these two density settings and this seed, not proof of impossibility.
4. Same-clock intrinsic scheduling throughput remains exactly 1.000x by RTL equivalence. No tile throughput or power advantage is established without SRAM/datapath/bandwidth/activity.

## Next independent holdout
If density tuning yields a promising source repair, freeze a new seed and load regime **before** rerunning it; do not count this tuning sweep as prospective transfer. If not, pursue matched physical timing repair and multi-corner constraints without replacing the active V317 pairwise mechanism.
