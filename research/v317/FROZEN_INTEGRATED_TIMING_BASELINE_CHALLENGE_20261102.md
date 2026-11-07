# V317 frozen timing-oriented equal-resource source challenger (2026-11-02)

## Lock and scientific question
Continue the sole fixed-priority pairwise bank-credit mechanism on existing branch/PR. The completed frozen integrated 32-wave result at source SHA 20c5165651d0a941d3c60f918e4255961b8a2a90 showed source -13.550 ps setup slack and pairwise +65.469 ps at 2.0 ns, but the source was area-oriented synthesized (ABC_AREA=1). This follow-up asks whether a **stronger timing-oriented synthesis control** erases the apparent timing win. It is not a new architecture mechanism.

## Protocol frozen before running new physical experiment
- Two identical 32-wave RTL variants, source and pairwise, using exactly the same source files, 356 sequential cells, scheduler, bank mux, feedback, IO and clock constraints.
- Same pinned official ORFS Nangate45 digest sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8; 120x120-um die, 112x112-um core, 2.0 ns target, 10 fF outputs, one typical corner, extracted RC.
- Set **ABC_AREA=0** identically for source and pairwise to allow a timing-oriented Yosys/ABC mapping alternative. Preserve logs proving the option was honored. If the option is ignored, call the experiment inconclusive rather than claiming stronger baseline.
- Run complete synthesis, placement, CTS, detailed route, extraction and timing for both. Upload all logs/reports, including failed runs. No changes to RTL, no new RF ports, no SRAM.
- Record exact tool image digest, source SHA, max slew/cap/fanout, setup/hold, antenna, DRC, mapped/routed area, wire, and default-activity power proxy.

## Prospective hypotheses and kill rules
P1 risky source-repair prediction: timing-oriented synthesis will reduce the source's prior 13.55-ps setup deficit, possibly closing 2.0 ns. A worse source timing result falsifies this repair hypothesis, not the equivalence claim.
P2 risky implementation prediction: pairwise retains a positive routed area advantage after matched timing-oriented synthesis. If area parity/reversal occurs, **kill the area-advantage claim for this stronger control**.
P3 timing advantage is NOT guaranteed. If source closes 2.0 ns with comparable area/power, the prior pass/fail contrast does not constitute a unique timing-enabling architectural effect. If pairwise fails setup/electrical/DRC, reject physical superiority for this setting.
P4 guaranteed semantic no-win regime: at equal clock, bank ports, RF capacity and offered traffic, both have identical accepted grants and **1.000x intrinsic service throughput**. Neither a faster controller nor lower area establishes GPU IPC without actual tile critical-path/area reinvestment.

## Evidence tier and future controls
This is a matched **synthesis-objective** challenger, not yet a full equal-area optimized Pareto frontier, multi-seed proof, PVT signoff or tile-level GPU measurement. After results, require multiple placement seeds, realistic SRAM/port integration and activity-calibrated power. Do not revive V287 or claim RTX-5090 equivalence.
