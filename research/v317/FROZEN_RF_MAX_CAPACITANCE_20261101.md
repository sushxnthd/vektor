# V317 frozen mapped-netlist max-capacitance audit (2026-11-01)

## Scope and provenance
The existing matched BUF_X1/BUF_X2 pre-route OpenSTA experiment checked output transition, but not maximum capacitance. Reuse the exact source and pairwise fixed-priority RTL, Yosys/ABC mapping recipe, pinned Nangate45 typical Liberty SHA `90e4afb274cfc6514c587c434c77903d554117d1`, and existing V317 draft PR #34. Do not modify the architecture or claim placement/routing.

## Predictions frozen before implementation/evaluation
The pinned library has `capacitive_load_unit (1,ff)`. Its BUF_X1/Z `max_capacitance` is 60.6537 fF, BUF_X2/Z is 121.155 fF. These values are independently readable from the Liberty file and are not inferred from the earlier STA outcomes.

1. At 24 fF, BUF_X1 output load is below its characterized max-capacitance, so its **output pin** passes the capacitance check. This does not predict that all internal mapped nets pass.
2. At 100 fF, BUF_X2 output load is below its characterized max-capacitance and its **output pin** passes.
3. At 100 fF, BUF_X1 output load exceeds its max-capacitance and **fails**, even if a timing report happens to show a numerical delay.
4. The core internal-net audit is **prospective, outcome unknown**. Audit every mapped combinational output driver against sum of its mapped input-pin capacitances; include four external buffer input-pin capacitances at the core grant outputs. If any driver is overloaded, preserve the failure and do not claim an electrically clean design.

## Method and controls
Independently parse the full pinned Liberty cell/pin direction, capacitance and max_capacitance, and the synthesized mapped Verilog connectivity. Resolve simple assign aliases including vector concatenations. Refuse unsupported cells, ambiguous pin expressions, missing output-driver information, or absent max-cap attributes instead of silently passing. Check both source and pairwise at matched BUF_X1 and BUF_X2. Report worst margin, offending nets, coverage, and external output-buffer margin. Add negative tests with known overloaded fixtures, aliasing and malformed inputs. Do not use ideal-wire STA delay to infer routed timing.

## Kill criteria
If the nominally transition-legal repair has a max-capacitance violation, withdraw its electrical-legality claim. If all mapped pin capacitances pass, describe only **cell-level ideal-wire capacitance admissibility**, not wire RC, max-transition signoff after placement, setup/hold closure, power or GPU throughput. Existing tile-law conditional no-speedup boundary remains in force. No new mechanism, branch or PR; Kernellum #119 untouched.
