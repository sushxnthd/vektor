# V296 fixed-word two-port RF cone: prospective falsification protocol (2026-10-27)

**Status: preregistered before implementation/results.** V296 pairwise bank admission remains the sole provisional architecture mechanism. V287 remains retired. This is an *implementation-only* intervention on the same symmetric, one-cycle-retimed, 16-bank, two-read-port-per-bank flop-RF proxy, not a new architecture mechanism and not a full GPU.

## Physical motivation and frozen evidence

The independently SHA-verified density-0.35 routed pair (GitHub Actions 40427986118) failed physical signoff. Candidate extracted setup slack -0.220829 ns (needs +0.270829 ns to reach +0.050 ns guard), hold -0.010023 ns, three capacitance violations, zero DRC, final cell area 17213.92 um^2. Optimized fifth-stage serial control setup -0.711405 ns, hold -0.013032 ns, zero capacitance violations, zero DRC, area 17994.90 um^2. Both are physically infeasible. Independently reproduced extracted-SPEF worst paths (Actions 40457095368) run from scheduler RR state to staged operand capture; V296 includes a 15-buffer segment with 0.358260 ns path increment, which is *not* a removable-delay estimate.

## Hypothesis and precise intervention

The existing bank-decode slice builds a per-bank dynamic first/second-request address selection and then a per-operand return crossbar. Its flop-RF proxy has exactly **two words per bank**, one bit of word address, and two read ports. For this **specific shallow bank**, two static physical read ports can be connected to word 0 and word 1, with the same read values broadcast to the return network. Every admitted operand selects its original word by its wave-ID low bit. The dynamic per-bank first/second priority address mux and operand-rank logic can therefore be removed **without adding read ports, issue slots, registers, or RF storage**. Preserve the balanced bank-return tree, existing 32-wave bank decode, and both independently instantiated schedulers. Use the same implementation for PAIRWISE=1 and PAIRWISE=0.

This is a *deliberately narrow RF-proxy experiment*: fixed-word ports are not an acceptable general SRAM design for banks with more than two words. If the physical gain relies on this shallow-bank shortcut, it cannot support a production GPU architecture claim. Measure switching activity of both always-available word outputs in subsequent power sensitivity. The experiment can falsify the old RF-proxy cone but cannot establish generalizable GPU benefit.

## Frozen test ladder and kill criteria

1. **Functional/cycle gate.** Over at least 2048 randomized, hotspot and collision-heavy cycles after all 32 RF words are initialized, require exact equality of issue IDs/grants and one-cycle-delayed executed_data for *both* PAIRWISE values against the existing decoded implementation, plus independent direct-index RF oracle, no X, no more than two logical bank reads per bank, and identical read-before-write behavior. Fail closed on any mismatch.
2. **Matched synthesis gate.** Same pinned Nangate45/Yosys/ABC and same 3.5 ns clock for decoded pairwise, decoded serial, fixed-word pairwise, fixed-word serial. Require equal sequential state (388 flops expected from previous mapping), no extra ports, and mapped area growth <=10% for either contestant. Record area and logic-depth changes, including regressions. A mapped advantage is not a physical win.
3. **Paired pre-CTS gate.** Use identical pinned fourth-stage physical generator and OpenROAD/Nangate45/RC policy, density 0.45, 260x260 um die, 240x240 um core, 3.5 ns clock, 2x RC, same fourth-stage repair, without changing timing, electrical, floorplan or tool policy. Candidate must reach **>= +0.050 ns pre-CTS setup slack** with zero cap/slew and nonnegative hold to justify a new routed trial. Preserve all failed/incomplete logs.
4. **Full matched routed gate (later, only if 1-3 survive).** Both implementations must receive strongest independently optimized equal-resource serial control and identical placement density, 3.5 ns clock, 2x RC, full CTS, detailed routing, extracted SPEF, setup >=+0.050 ns, hold >=0, zero cap/slew/DRC, final area <=30000 um^2, switching/power proxy and sensitivity to wire/load. Do not infer feasibility from pre-CTS, relative slack, or smaller area. Reject the fixed-word repair if any required gate fails; preserve the original V296 mechanism as provisional only.

## Prospective workload boundary (sealed, not evaluated here)

**Predicted conditional win:** enough independent resident waves, low bank hot-spot overlap, bank-port pressure below two reads per bank, no bandwidth saturation, and a *measured physically feasible* area/frequency or equal-budget tile-packing improvement. **Predicted no-win:** bandwidth-limited or dependent low-occupancy work, or any workload with insufficient compatible waves, or a clock/area/power penalty that erases any tile-level gain. At identical issue grants and identical clock, this refactor has **zero admission-throughput gain** by construction. The prior controlled-generator phase-correlation law is not a measured GPU throughput claim; holdouts remain unopened.

## Reproducibility and noninterference

New source/test/generator/workflow must be isolated under distinct fixed-word names, leaving original RTL, artifacts, frozen thresholds, other PRs, and Kernellum #119 untouched. Keep one V296 branch and draft PR #13. Never force-push, merge, claim RTX-5090 equivalence, or treat this tiny flop-RF as production SRAM.
