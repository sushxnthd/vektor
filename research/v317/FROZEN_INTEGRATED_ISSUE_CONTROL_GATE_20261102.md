# V317 frozen integrated issue-control physicality gate (2026-11-02)

## Purpose and mechanism lock
Continue the sole active fixed-priority pairwise bank-credit implementation on `research/v317-sass-provenance-gate` and draft PR #34. Do not revive V287/V296. The prior 40-FF registered arbiter route is a CONTROL-BLOCK result. This experiment must include the **existing 32-wave steal scheduler, 32-way bank selection, acceptance feedback, and matched input/output registers** before treating the saving as relevant to the issue-control subsystem. This still excludes register-file SRAM, read ports, data-path and clock distribution and is NOT a full GPU tile.

## Frozen matched design
- Source control: instantiate unmodified `rtl/vtile/issue_control.sv`, including `vektor_steal_warp_scheduler` and `vektor_rf_bank_arbiter`.
- Pairwise control: duplicate only the original issue-control interconnect, replacing the arbiter instance with `vektor_v317_rf_pairwise`; keep the exact same scheduler, bank mux, feedback and flop boundaries.
- Both variants: 32-bit wave_valid, 32-bit wave_ready, 128-bit src0 and src1 bank inputs; 4 accepted issue slots and four 5-bit wave IDs, registered at the output. Input vectors also registered, with equal reset and timing constraints. Do not change issue policy, RF ports or scheduler.
- Pinned official ORFS Nangate45 container digest `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`. Matched 120x120 um die / 112x112 um core, 2.0 ns target, same input drive, 10 fF output load, one typical corner. Preserve failed flow logs and all output reports.
- Source/pairwise RTL equivalence test: randomized ready/valid and banks with shared cycle inputs, directed same-bank and hotspot vectors, and matched reset. Any mismatch is immediate NO-GO.

## Predictions frozen before route
P1: Pairwise and source issue-control outputs are cycle-equivalent in simulation for every tested stimulus. Mismatch kills the implementation claim.
P2: At the integrated issue-control level, the pairwise variant is predicted to have lower mapped and routed standard-cell area. This is a risky prediction, not guaranteed by the isolated 733 um2 saving: synthesis may share/restructure other logic. If area advantage vanishes or route is illegal, mark NO-GO for this integration.
P3: Do NOT predict that the isolated 2.66x control-block period ratio survives. With scheduler and bank mux included, the integrated critical path may dominate both. Report the two actual extracted-RC periods and the limiting paths. If timing regresses or the route is electrically illegal, do not claim integrated performance benefit.
P4 (negative control): Both implementations have exactly the same accepted issues/cycle under identical state, bank-port budget and clock. No intrinsic GPU IPC improvement, even if integrated area/timing improves. If shared bandwidth or RF SRAM dominates, an area saving alone need not add a tile.

## Independent acceptance / kill rules
Require complete source-pinned RTL simulation and two complete matched physical routes, with final DRC, antenna, setup, hold, max-slew/cap/fanout counts all reported. Missing electrical checks mean inconclusive, not pass. Reconcile source SHA and tool digest. Preserve negative results. The next step after this gate is measured workload traffic and a realistic RF SRAM/clock/power integration, not extrapolation to RTX 5090. A failure of the 2.0 ns timing target is evidence, not a reason to silently loosen the constraint.
