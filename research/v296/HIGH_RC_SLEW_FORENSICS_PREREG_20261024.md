# V296 high-RC extracted-SPEF slew-endpoint forensics (preregistered 2026-10-24)

**Status: diagnostic experiment, not an architecture change or a repair.** Sole active mechanism remains V296. Prior six-case extracted-route gate stays **FAILED** and V287 remains retired.

## Fixed source and hypothesis
- Reuse immutable raw detailed-route artifact **12523741140** from run **39995731088** (head `624b967c2c2093b32b5841e9c5ffc105377bf159`).
- Inspect only `pairwise.high` (the measured **33 maximum-slew violations**), without new placement, routing, resizing, timing repair, synthesis, or modified RC.
- The original artifact reports V296 high-RC controller area **5985.266061 um2**, extracted setup **+0.361922 ns**, extracted hold **+0.283003 ns**, cap violations **0**, and detailed-route DRC **0**.
- Hypothesis to test: the violations can be attributed to specific pins and net/fanout structures, allowing a bounded repair experiment rather than a blind fourth repair round. No claim of clustered violations is made before endpoint inspection.

## Rehydration protocol
1. Use the artifact's `pairwise.v`, `pairwise.high.detail.def`, and `pairwise.high.detail.spef` unchanged; download the **same pinned Nangate45** Liberty and LEFs as the original workflow and record SHA256 digests.
2. Load LEFs, Liberty, synthesized Verilog, DEF and extracted SPEF in pinned OpenROAD; restore original 3.5 ns clock, 0.15 ns I/O delays, 0.04 ns input transition, 0.005 pF output load, 0.25 ns max transition, reset false path.
3. Print all `report_check_types -max_slew -violators -format end` entries and summary count. Also print max-cap report, extracted worst setup/hold and area. Record the original DEF and SPEF hashes both before and after.
4. Independent audit fails closed unless reported slew count is **33**, capacitance count **0**, setup and hold match original within **0.005 ns**, area within **0.01 um2**, and the violation report is nonempty. Report formatting may yield multiple rows per pin; **do not equate count with distinct nets** without a verified mapping.
5. Any replay mismatch is a **forensic reproducibility failure**, not evidence that the original 33 violations disappeared. Preserve all logs and do not relabel the frozen six-case gate.

## Falsifiers and follow-up
- If the pinned toolchain cannot reproduce the 33 violations, stop targeted inference and investigate SPEF/DEF/SDC provenance.
- If endpoint attribution succeeds, freeze a **matched** post-route electrical repair with independent control optimization and a common area ceiling *before* seeing its PPA. V296-only high-RC repair has at most **259.961874 um2** extra area to preserve >=10% saving against the **unchanged** optimized control; this is conditional, not an allowance to ignore equal-resource controls.
- Retire V296 if a fully clean repaired candidate loses the matched area/timing advantage or a best equal-resource control eliminates it.
- No workload holdouts opened; no tile frequency, GPU throughput, power, signoff, or RTX-5090 claim.


## Rehydration compatibility amendments (2026-10-24, before any successful replay)
- Initial run **40018003482** stopped because the cross-run artifact is unpacked under a named directory; the runner path was corrected without modifying physical inputs or acceptance thresholds.
- Second run **40018173410** passed the audit self-test and artifact download but stopped with `ODB-0251 Chip already exists`: `link_design` creates a chip before `read_def` tries to create the routed chip. The corrected replay loads the **routed DEF alone as the authoritative OpenDB physical netlist**, while still requiring and hashing the original synthesized Verilog for provenance. The Liberty and extracted SPEF are unchanged. This follows OpenROAD's documented DEF import path and does not alter any timing constraint, expected metric, or frozen falsifier.
- The two interrupted runs are **tool/replay failures**, not evidence of slew closure. No endpoint result is claimed until the corrected replay and independent audit complete.

- Third run **40018633959** successfully reproduced the independent six-case SPEF-load summary but the DEF-only replay hit a pinned OpenROAD Resizer segmentation fault at `rsz::design_area` because the STA network was not initialized by `link_design`. This is a toolchain failure, **not** evidence that any electrical violation disappeared. The next compatibility revision restores `read_verilog; link_design` and imports the unchanged routed DEF using `read_def -incremental`, an OpenROAD-supported option that reuses the existing chip rather than creating a second one. The original Liberty, SPEF, constraints, 33-count target, and acceptance criteria are unchanged.
