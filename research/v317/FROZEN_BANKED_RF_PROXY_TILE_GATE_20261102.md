# V317 frozen banked RF-proxy integration gate (2026-11-02)

## Provenance and mechanism
This prospective protocol precedes new RTL and physical outcomes. Continue **only** the existing fixed-priority V317 pairwise bank-credit replacement on `research/v317-sass-provenance-gate`, draft PR #34. The source is the unmodified `vektor_issue_control`; pairwise is the existing grant-equivalent `vektor_v317_issue_control_pairwise`. Both must share identical scheduler, operand-bank mapping, 16-bank dual-read RF proxy, write port, registered operand sink, synthesis constraints, die/core, and pinned OpenROAD toolchain. No new scheduler or policy.

## Explicit physical scope
Use a **flop-mapped proxy** with 16 banks, four 8-bit words per bank, **two read ports per bank**, one global write port, 4 issue slots x 2 operands, and a registered 64-bit operand-data sink. The proxy must implement actual per-bank two-read selection, with overflow detection; it may not silently implement unlimited per-bank reads. Reads from granted operands only. This is a small standard-cell register array, **not** a characterized SRAM macro, GPU register file, realistic datapath, or a full tile. All reports must call it an RF proxy.

## Frozen challenges
1. Functional equivalence: 4,096 randomized/directed cycles, identical writes, compare grants/waves and registered operand data cycle-by-cycle; bank-port overflow must remain zero. Include same-bank and 2-bank hot spots. A mismatch or overflow kills the integration result.
2. Matched physical route: Nangate45, pinned official ORFS image, same 16-bank RF proxy, same area-oriented synthesis and 3.0-ns target, 0.1-ns uncertainty, 10-fF output loads, identical 240x240-um die and 8..232-um core. Record actual physical settings and any route failures.
3. Prediction **no-win**: at identical clock, ports, RF depth, and workload, both controllers must emit exactly the same grants and operand data, so intrinsic issue throughput ratio is **1.000x**. Any observed gain from a changed grant pattern is a correctness bug.
4. Prediction **conditional physical win**: the pairwise implementation will save **at least 2.0% of routed standard-cell area** relative to the legal matched source under the 3.0-ns target. This is an intentionally demanding dilution test of the prior 7.55% control-only advantage at 2.2 ns. If either route fails timing/electrical closure, report this prediction **unresolved**, not passed.
5. Require zero final detailed-route DRC, setup/hold, max-slew, max-cap and fanout violations for both. Independently parse source physical reports and preserve raw artifacts.

## Kill/retention
If area saving is <2.0%, reject any claimed material RF-proxy area win. If source and pairwise grants differ, reject equivalence. If neither variant is legal, reject a physical-performance claim; repair matched setup without quietly changing constraints. Even if this test passes, it cannot establish SRAM macro timing, GPU IPC, multi-corner signoff, activity-calibrated power, full tile area, or RTX-5090 equivalence. The strongest equal-resource alternative remains the legal source controller, not a crippled 2-ns baseline. The next hard gate is actual SRAM macro or characterized banked memory and realistic datapath placement.
