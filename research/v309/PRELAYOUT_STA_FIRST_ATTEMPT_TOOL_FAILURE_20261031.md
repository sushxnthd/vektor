# V309: first prelayout STA attempt rejected as tool-interface failure (2026-10-31)

[Hosted run #41158430070](https://github.com/sushxnthd/vektor/actions/runs/41158430070), source commit `6b8615f8c31706880d32ccf520e188dbf6583367`, **failed** the independent delay audit. This is **not** a timing falsification of the architecture.

The pinned Nangate45 Liberty download and hash verification, matched Yosys standard-cell mapping, and OpenSTA installation all completed. However the Ubuntu 22.04 OpenSTA 2.0.17 build rejected `report_checks -group_path_count` and `report_check_types -max_slew -max_cap -max_fanout` as unsupported arguments. Its executable returned zero despite reporting Tcl errors; the independent checker correctly rejected the missing constrained arrival-time path. Raw evidence: [artifact #13025707529](https://github.com/sushxnthd/vektor/actions/runs/41158430070/artifacts/13025707529).

Repair commits replace the unsupported report options with `report_checks -path_delay max` and explicitly fail the workflow on `Error:` lines. The originally frozen input slew/output load corners and optimistic 1.097348334x timing kill threshold are unchanged. This repair **does not** establish cap/slew signoff: the installed OpenSTA build cannot provide the originally requested electrical violation command, so that requirement remains open for a later tool.

No hardware timing numbers or speedups may be inferred from the failed run. The next source-pinned hosted run must produce valid constrained paths and pass the independent parser before the frozen timing kill can be evaluated.
