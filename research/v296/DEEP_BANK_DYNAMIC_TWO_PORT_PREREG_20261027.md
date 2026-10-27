# V296 dynamic two-port deep-bank transfer: prospective protocol (2026-10-27)

## Status and isolation
V296 pairwise bank admission is the **only** active architecture mechanism. This is an implementation transfer test, not a replacement mechanism. V287 remains retired. Preserve draft PR #13, branch `research/v296-pairwise-bank-conflict`, all earlier negative evidence and sealed workload holdouts. The fixed-word two-static-output shortcut was already falsified for depth >2; do not resurrect it.

## Frozen experiment before hosted RTL/synthesis outcomes
- Instantiate **16 banks**, **exactly two dynamic read ports per bank**, **one global write port**, **four issue slots**, **8-bit data**, and depths **4, 8, 16** words per bank (word-address bits 2, 3, 4).
- Apply the *identical* deeper bank RF, retimed operand capture, balanced return network, and write interface to the V296 pairwise and optimized V295 serial issue cores. The only architectural difference is the admission logic.
- Derive word addresses deterministically from the low word-address bits of each issued wave ID; this is a functional stress proxy, **not** an actual GPU ISA operand address generator. Independently initialize every word and vary writes during randomized conflict-heavy operation.
- Run an independent direct-index oracle for both implementations. Require cycle-exact issue equivalence, one-cycle delayed execution equivalence, read-before-write semantics, no uninitialized observed data, and <=2 admitted reads per bank. At least 2048 randomized cycles per depth plus deliberately bank-conflicted cases. Fail closed on any mismatch.
- Run four matched Nangate45/Yosys synthesis configurations for each depth where resources allow: V296 pairwise and V295 serial, with the same RF depth, ports, data width, input/output boundary, and timing assumptions. Record flop count, mapped area, logic depth and tool/library SHA. **Do not** infer timing closure from mapped logic depth.
- A synthesis result is **not** a physical feasibility result. Post-CTS routed extracted-RC setup >=+50 ps, hold >=0 ps, zero capacitance/slew/DRC violations, and area <=30,000 um^2 must be checked under the original 3.5 ns, 2x RC constraints for both contestants. Do not relax these limits.
- Strongest feasible equal-resource serial control is required before declaring an architecture Pareto advantage. If either implementation fails signoff, classify as infeasible/indeterminate rather than claim a win.
- Freeze prospective workload win/no-win regimes *before* their execution: (A) high bank-conflict compatibility, high occupancy, low memory-port pressure as predicted win; (B) low compatibility or externally bandwidth-capped as predicted no-win. No GPU throughput claims until measured-clock and traffic-constrained workload validation.
- Record negative results and compiler/simulator/RTL limitations. A flop array is **not** a production multiported SRAM macro; realistic wire, banking, macro and energy transfer remain open.

## Structural sensitivity
For a conventional balanced binary word mux implementation with D words, B=16 banks, P=2 read ports and W=8 bits, the **illustrative** count of 2:1 mux-bit nodes is B*P*W*(D-1). This is not a technology-independent cell-area lower bound and must not be used as one. Report both the memory-bit growth B*W*D and the mux-tree proxy. Distinct same-address requests still consume two read slots, so no hidden broadcast/extra port may be assumed.

## Kill and evidence tier
A failure of independent RTL equivalence kills the dynamic RF implementation immediately. A routed electrical failure rejects that implementation even if synthesis is favorable. A candidate-only physical pass is not a matched feasible speedup. Until routed signoff and workload transfer, report only functional/mapped evidence, never RTX-5090-equivalence.
