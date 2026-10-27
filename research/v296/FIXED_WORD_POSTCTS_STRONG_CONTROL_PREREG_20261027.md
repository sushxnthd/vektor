# V296 fixed-word symmetric full-route trial: frozen protocol (2026-10-27)

**Frozen before full-route outcomes.** Sole active architecture mechanism: V296 pairwise bank admission. This is a symmetric implementation-only RF proxy refactor, not a new architecture mechanism. V287 remains retired.

## Motivation and sealed prior evidence

Original ZIPs from Actions 40457696916 passed SHA-pinned matched pre-CTS audit: fixed-word pairwise area 12806.570 µm², setup +230.183 ps, hold +112.255 ps, cap/slew zero; fixed-word serial area 15103.746 µm², setup −193.882 ps, hold +113.217 ps, cap/slew zero. Candidate passes the previously frozen +50 ps pre-CTS gate. This does **not** establish post-CTS or extracted-RC timing closure.

## Physical experiment and invariants

Generate the existing, independently audited `bank_decode_postcts_flow.py` integrated tile physical runner, then change **only** the RTL source/top from `v296_tile_slice_bank_decode` to `v296_tile_slice_fixed_word` for both PAIRWISE=1 and PAIRWISE=0. Preserve the same original generated `cts45_tile.tcl`, 260 µm die/240 µm core, placement density 0.45, 3.5 ns clock, 2× resistance/coupling/ground RC, propagated CTS, detailed route, SPEF extraction, and same physical library/tool versions. **The serial control must retain its independently optimized fifth-stage setup repair** (`V296_CONTROL_EXTRA=1` and 250 ps setup repair margin); candidate extra repair must remain 0. Keep 16 banks, two read ports per bank, same RF storage, and identical pipeline latency. Do not modify RTL, floorplan, electrical limits, or constraints to rescue the result.

## Frozen kill criteria

1. Both contestant logs must complete post-CTS, detailed routing and extraction with reproducible DEF/SPEF, with an independent provenance and physical audit. Right-censored/failed runs remain incomplete, never zero violations.
2. Candidate extracted setup slack **>= +0.050 ns**, hold slack **>= 0**, zero capacitance violations, zero slew violations, zero DRC, final cell area **<= 30000 µm²**. Reject this fixed-word repair if any fails.
3. Compare against the strongest serial fifth-stage optimized control. A relative setup/area lead over an infeasible control is not a physical Pareto claim. A credible matched advantage requires **both** to meet their physical gates, with at least 1% candidate area saving and 50 ps extracted setup lead; otherwise classify infeasible/unsupported.
4. The candidate has a 180.183 ps pre-CTS setup-degradation budget to its +50 ps guard. Record whether post-CTS/extracted penalties exceed it, without treating this as a prior prediction of routed slack.
5. No clock-frequency, GPU throughput, power, or RTX-5090-equivalence claim. The shallow two-word-per-bank RF shortcut cannot be generalized to deeper-bank SRAM. Preserve sealed workload holdouts until physical feasibility is demonstrated.

## Noninterference

Reuse persistent `research/v296-pairwise-bank-conflict` and draft PR #13. Preserve previous negative evidence, all other research PRs and Kernellum #119. Do not force-push, merge, change other workstreams or consume paid resources.
