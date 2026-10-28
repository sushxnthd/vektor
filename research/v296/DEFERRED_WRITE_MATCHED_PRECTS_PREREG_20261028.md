# V296 deferred-write matched pre-CTS D4/D8 physical falsification protocol (2026-10-28)

## Frozen question
Can the already RTL-validated deferred-write retiming implementation meet the *same-depth* 3.5 ns timing/area boundary with the optimized fifth-stage serial controller? V296 pairwise admission remains the sole architecture mechanism; V287 is retired. No new arbitration algorithm, RF port, clock relaxation, placement density change, or area-budget increase is allowed.

## Locked experiment
- Derive the physical runner from the existing SHA-verifiable D4/D8 dynamic RF hold25 post-CTS experiment. Substitute **only** the already-tested `v296_tile_slice_deferred_write` source/top for `v296_tile_slice_deep_bank`, symmetrically for both PAIRWISE settings, keeping 16 banks, two dynamic read ports/bank, one global write, four issue slots and identical Nangate45/Yosys/OpenROAD tool/library provenance.
- Retain the full frozen pre-CTS physical Tcl through the *serial-only fifth-stage repair*, 3.5 ns clock, 2x estimated RC, 260 um die/core geometry, 0.45 placement density, 20% cap and 10%-35% slew margins, unchanged input/output delays. Stop **before** clock-tree synthesis and detailed routing. Report pre-CTS setup worst slack, top paths, area, cap and slew. A pre-CTS estimate is not routed extracted-RC signoff.
- Run all four combinations: D4 pairwise, D4 optimized serial, D8 pairwise, D8 optimized serial. Preserve tool failures and censored timeouts as failures, not successes. Do not compare different depths.
- A separate checker must verify complete logs, actual fifth-stage serial repair marker, correct source and constraint hashes, and nonnegative/missing values. Classify every depth as *infeasible*, *pre-CTS plausible*, or *indeterminate*; never infer a GPU win from the result.
- Keep the previously frozen occupancy boundary (N=2,B=2,q=.9 needs >1.9x frequency ratio if latency grows L1 to L2), and preserve sealed workload holdouts.

## Predictions and kill criteria
The registered address path may improve setup, but RF-return and write-delay paths can remain critical. A D8 mapped area margin of only 460.978 um2 means even modest differential placement/repair overhead may erase the advantage. If the deferred design or matched serial baseline cannot reach >=+50 ps setup and <=30,000 um2 at pre-CTS with estimated RC, do **not** advance that depth to full route. A pre-CTS pass is only a prerequisite, not a positive physical result. If neither depth survives, retire deferred-write retiming as a V296 implementation repair and preserve the falsification. Do not claim power, performance, SRAM macro, or RTX-5090 equivalence.

Existing RTL and mapped evidence: [V296 deferred-write report](V296_DEFERRED_WRITE_MAPPED_TRANSFER_FALSIFICATION_20261028.md).