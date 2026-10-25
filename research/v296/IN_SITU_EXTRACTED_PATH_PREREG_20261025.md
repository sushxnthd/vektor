# V296 integrated RF-slice: in-situ extracted critical-path experiment (frozen 2026-10-25)

## Motivation and prior negative result

The original matched post-route run 40156470550 **falsified physical feasibility for both contestants** at 3.5 ns: V296 setup/hold -1.047895/-0.036622 ns, serial -1.859922/-0.019796 ns; both had three cap violations. Reimporting its post-route DEF/SPEF to reconstruct path endpoints failed under pinned OpenROAD. The six-cap-violator physical topology audit succeeded. **This new experiment does not reconstruct the original routed paths**; it runs a fresh matched implementation and captures extracted critical paths directly while the original physical database is still live.

## Immutable design and physical procedure

Keep one active V296 pairwise bank-arbitration mechanism and the strongest serial one-hot control. Preserve 32-wave scheduler, four issue slots, 16 register banks with two read ports, same 8-bit execution slice, 3.5 ns clock, 260 µm die, 45% placement density, 2x OpenRCX, identical Nangate45 and pinned Yosys/OpenROAD. Preserve the original asymmetric **control-advantaged** fifth pre-CTS repair, matched CTS, detailed routing, timing constraints and all electrical repair commands. Generate the same Tcl for both variants, and insert ONLY `report_worst_slack` and `report_checks` after extracted `read_spef`. Assert by exact-source transformation that no physical command was changed. Preserve both raw logs, DEF/SPEF, netlists, hashes and independent physical audits.

## Frozen predictions and falsifiers

- Both contestants complete detailed route, extracted RC and independent physical audit. Missing artifacts or missing path endpoints are **INCOMPLETE**.
- In-situ reported worst setup/hold slacks must match same-run independently audited extracted slacks within 0.005 ns; otherwise **NO PATH ATTRIBUTION**.
- Report five extracted setup and hold path endpoints per contestant, and whether the fresh run reproduces the original setup and hold within ±0.050 ns. If not, flag drift; never label fresh paths as the original run's critical paths.
- The original physical feasibility gate remains +0.050 ns setup, ≥0 hold, zero slew/cap/DRC, ≤30,000 µm² for **both**. No relaxation, no cherry-picking, no architecture switch. The expected result remains physical infeasibility; an unexpected feasible rerun is reported, not silently reclassified as validation.
- Same-clock admission advantage is exactly zero. Neither this path probe nor a negative-slack comparison establishes GPU Fmax, measured power, equal consumed area or throughput. Holdouts stay sealed.

## Decision

Use new-run in-situ extracted path evidence to preregister a **separate matched, path-targeted electrical/timing repair** only if both paths and original-vs-new drift are understood. Preserve all negative evidence. V287 retired; Kernellum PR #119 untouched.
