# V317 frozen legal-clock crossover and equal-resource source challenge (2026-11-02)

## Research question and provenance
**Precommitted before new physical routing.** The original integrated issue controller misses the 2.000-ns setup target by 1.48 ps in the previously observed favorable seed-7 / density-add-on 0.05 route, while pairwise closes timing. Is the observed pairwise advantage still a defensible **area/power implementation advantage** when the source receives a legal relaxed-clock baseline, or does the difference disappear after both become timing-clean?

The single active mechanism remains fixed-priority pairwise bank-credit, grant-equivalent to the original. This challenge introduces **no new scheduling policy** and does not revisit historical V287. Both implementations have 1.000x intrinsic equal-clock service rate.

## Fixed experimental design
Use the existing pinned OpenROAD-flow-scripts container `openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`, Nangate45, existing `rf_integrated_issue_top.sv`, area-oriented ABC (`ABC_AREA=1`), `GPL_TIMING_DRIVEN=1`, `GPL_RANDOM_SEED=7`, `PLACE_DENSITY_LB_ADDON=0.05`, die `0 0 120 120`, core `4 4 116 116`, 10-fF output load, 100-ps clock uncertainty, identical I/O delays and driving cells. Freeze two **previously untested clock targets**, 2.050 and 2.200 ns, for both original and pairwise: **four full detailed routes**. Only clock period changes relative to the favorable previous density experiment. Do not select the best seed or change placement parameters after observing results.

The 2.200-ns target is a **hypothetical external tile critical path** already used in the earlier analytical tile model, not a measured GPU tile clock. Neither target implies 5090-equivalent performance.

## Frozen predictions and falsifiers
- P1: At 2.200 ns, **both** implementations will be setup-clean, DRC-clean and max-slew/max-cap/max-fanout-clean. If source fails, the predicted legal-source control is falsified.
- P2: At 2.050 ns, the source should be setup-clean, but the 1.48-ps previous miss is too close to imply certainty under remapping. Record any failure, not just successes.
- P3: In **each legally comparable pair**, pairwise retains **at least 7% lower routed standard-cell area**. If the legal original comes within 7% area, retract this frozen material-area claim.
- P4: Neither implementation has a same-clock grant/IPC advantage. A change in timing closure is **not** a throughput gain unless the system's limiting clock is established independently.

Preserve full logs, routing DB/GDS, STA setup/hold reports, electrical violation counts, default-activity power proxy, cell area, wire length, clock target, and return status for **all four** configurations, including failures. Explicitly separate setup-clean, electrical-clean, routed DRC-clean and macro-level conclusions. If either side is not fully legal, do not call that pair a legal area/power comparison.

## Decision
A clean source route at 2.200 ns kills the claim that pairwise is *necessary* for a feasible slower clock, even if pairwise saves area. If both are legal but the area advantage collapses below 7%, kill the physical-materiality claim. If area savings survive, retain only a controller implementation result pending RF SRAM, real floorplan, switching activity, multi-corner and measured GPU workload IPC. All raw evidence must remain independently checkable.
