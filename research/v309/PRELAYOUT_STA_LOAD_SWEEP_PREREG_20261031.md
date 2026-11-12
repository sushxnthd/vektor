# V309: preregistered prelayout Liberty STA / electrical-load sensitivity (2026-10-31)

**Status: protocol before any OpenSTA delay result.** Same one exact-max bank-admission candidate versus the strongest functionally identical compact-greedy control. The matched Nangate45 mapped-area gate and prospective IID bank-equality law passed in hosted run #41157943917; neither establishes timing or physical speedup.

## Frozen prelayout timing experiment

Use the same pinned NangateOpenCellLibrary typical corner, Git blob `90e4afb274cfc6514c587c434c77903d554117d1`, same Yosys mapping command and source inputs as the successful standard-cell area experiment. Export technology-mapped Verilog for compact greedy and factored exact-max, without adding sequential stages. Use OpenSTA on the hosted runner; record its package/version and reject missing tool support. This is **prelayout STA with zero extracted interconnect RC**, not routed timing.

Treat all 36 input bits and four output bits identically. Create a virtual 1.0 ns reference clock, zero input/output delays, set input transition and output capacitive load, then report maximum input-to-output combinational data arrival time and max slew/cap/fanout violations. Freeze three corners:

| Corner | Input transition | Output load |
|---|---:|---:|
| optimistic | 0.020 ns | 0.005 pF |
| nominal | 0.050 ns | 0.020 pF |
| stressed | 0.100 ns | 0.100 pF |

Report each controller's delay and candidate/baseline ratio per corner. Fail closed on missing valid paths, missing data arrival time, unknown timing arcs or unsupported checks. Preserve complete Tcl, mapped netlists, Liberty and raw logs.

## Frozen early kill criterion

The prospectively predicted hot2 issue-admission ratio is **1.0973483338585934**. Under the deliberately optimistic assumption of no occupancy, scoreboard, port, bandwidth or queue penalty, the candidate cannot win if `D_factored/D_compact >= 1.0973483338585934` at the **optimistic zero-wire** corner when both share an unpipelined critical issue-control stage. If this occurs, **kill the current factored RTL mechanism**; do not rescue it by citing the old unoptimized greedy baseline or synthetic issue gains. Report nominal and stressed corners regardless.

If it passes the optimistic delay threshold, **do not promote**. Next require matched placed-and-routed wire/load parasitics, input and output buffering, setup/hold and max-cap/slew checks under physical fanout, occupancy/traffic, fairness, and real-workload trace validation. An OpenSTA zero-wire delay is not a GPU frequency measurement, and even a timing win at this gate is not a tile-level performance claim.

The kill criterion is conservative as a research screening rule, not a theorem about every possible floorplan. Preserve any failure.
