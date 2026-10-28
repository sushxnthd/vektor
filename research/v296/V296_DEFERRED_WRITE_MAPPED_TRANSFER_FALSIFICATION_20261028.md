# V296: deferred-write retiming passes RTL but erodes mapped area advantage (2026-10-28)

**Decision:** semantic repair survives, but its mapped-area margin is now only 2.46% at D8 and 3.45% at D4. **Do not claim a physically credible architecture win.** This is a prospective RTL trial followed by a SHA-locked synthesis comparison, not timing/electrical signoff or GPU performance evidence.

## Prospective test and functional result
The [frozen protocol](DEFERRED_WRITE_RF_RETIMING_PREREG_20261028.md) was committed before RTL/synthesis outcomes. [Hosted Actions run #40626709496](https://github.com/sushxnthd/vektor/actions/runs/40626709496) passed the independent immediate-write oracle at D4/D8/D16, 2,048 randomized cycles and 6,608 accepted waves each, with 236/207/191 directed+random read/write collisions respectively. The symmetric [RTL](v296_tile_slice_deferred_write.sv) has exactly two dynamically addressed RF reads per bank, one global write port, and one extra operand latency edge; [independent Python checker](v296_deferred_write_checker.py) additionally passes 1,600 exhaustive two-edge cases and 120,000 seeded synthetic cycles. No arbitrary mid-flight reset or external RF visibility equivalence is claimed.

## Original-artifact mapped audit
All four original GitHub Actions synthesis ZIPs were downloaded and independently SHA-256 verified; a [fail-closed independent checker](v296_deferred_mapped_audit.py) reproduces the results from the original ZIP bytes, with [machine-readable output](V296_DEFERRED_MAPPED_AREA_AUDIT_20261028.json). A wrong-ZIP negative control was rejected. Across old and retimed experiments, Yosys is **0.9 (1979e0b)**, the Nangate45 library SHA is **8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1**, and both V296/V295 scheduler-core SHA values match. The only RTL top difference is the symmetric retiming implementation. Yosys `check -assert` and mapped synthesis completed for both contestants at both depths.

| Depth | Original V296 / serial mapped area (um2) | Retimed V296 / serial mapped area (um2) | Original area margin | Retimed area margin | Margin erosion |
|---|---:|---:|---:|---:|---:|
| D4 | 12,960.584 / 13,835.990 | 13,044.906 / 13,510.406 | 875.406 (6.327%) | **465.500 (3.445%)** | **46.825%** |
| D8 | 17,552.542 / 18,782.260 | 18,308.514 / 18,769.492 | 1,229.718 (6.547%) | **460.978 (2.456%)** | **62.514%** |

The D8 retimed V296 mapped implementation grew by **755.972 um2**, while the serial implementation changed by **-12.768 um2**. This is an empirical synthesis outcome, not a universal physical cost of retiming. The same flop-RF proxy is used for both; a production SRAM macro and actual wire/load are not modeled.

## Necessary physical break-even boundary
If H_pair and H_serial are candidate-specific physical overheads beyond the two mapped implementations, then preserving *any* V296 area advantage requires

`H_pair - H_serial < 465.500 um2` at D4, and
`H_pair - H_serial < 460.978 um2` at D8.

These are necessary mapped-to-physical area boundaries, **not** estimates of the overhead or sufficient conditions for feasibility. Both designs must independently close routed 3.5 ns timing, >=+50 ps setup, >=0 hold, zero cap/slew/DRC, and <=30,000 um2. The previous unretimed D8 V296 route failed setup by 734.592 ps and one cap check; no matched same-depth routed pass exists. It is invalid to extrapolate the retimed mapped-area delta into routed area or timing.

## Hard next experiment
Run **matched same-depth pre-CTS path analysis first**, including the optimized fifth-stage serial alternative. Require a measured register-to-register critical-path reduction large enough to justify the extra pipeline stage and survive the [exact occupancy break-even law](V296_OCCUPANCY_LATENCY_BREAK_EVEN_20261028.md): >1.9x clock improvement in the frozen N=2, B=2, q=.9 low-occupancy regime; >1.0009x in the bandwidth-saturated regime. If candidate area, electrical feasibility, or workload-level throughput fails, kill this retiming repair. Do not spend another 165-minute detailed-route attempt solely to increase timeout.

**Status:** V296 is the sole provisional mechanism; V287 retired. No real GPU trace, power, SRAM macro, or RTX-5090-equivalence claim. Kernellum PR #119 and sealed prospective holdouts unchanged.
