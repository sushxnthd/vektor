# V296: prospective fixed-topology RC and load sensitivity discriminator

Date frozen: 2026-10-23. **No fixed-topology measurements have been run.**
This supplements, rather than replaces, the frozen 3.5 ns all-nine-case closure gate in `ROUTED_RC_BOUNDARY_AND_3P5NS_PREREG_20261023.md`. V296 remains the only active mechanism. All workload holdouts remain sealed.

## Why a second sensitivity experiment is necessary

The existing low/nominal/high global-route experiments *rerun electrical and timing repair* at each RC setting. They are valid as an **adaptive implementation response**, but they are **not a fixed-circuit wire-sensitivity law**. In the new 3.5 ns evidence, the original controller improves routed slack from -0.051959 ns at RC=0.5 to +0.102248 ns at RC=2 while its area increases from 5867.694 to 6952.176 um2. Higher nominal wire RC cannot be interpreted as inherently improving timing: the resizer and route decisions changed. The candidate's area similarly grows from 5058.522 to 5799.066 um2 across the sweep.

## Frozen experiment A: fixed-topology sensitivity

1. Independently synthesize and electrically repair all three implementations at the **same nominal RC=1.0** and shared **3.5 ns** clock using the pinned Nangate45/OpenROAD versions, same die/core, and identical pin/load/transition constraints. Preserve complete postrepair **Verilog netlist, DEF, routing topology/guide, tool hashes and constraints** per implementation.
2. Freeze each implementation's nominal physical design. Across RC multipliers **0.5, 1.0, 2.0**, vary wire resistance and capacitance together **without synthesis, resizing, buffering, placement changes or route-topology changes**. The independent checker must verify identical cell/netlist/placement/route hashes across the RC sweep for each implementation. If the available OpenROAD flow cannot recompute parasitics without changing routing topology, mark the fixed-topology test **UNSUPPORTED**, not passed.
3. Independently vary output load around the baseline **0.005 pF**: **0.0025, 0.005, 0.010 pF** at nominal RC, holding the same topology. Check setup, max transition and max capacitance, including endpoint identities and fanout.
4. Report candidate and **both** controls' worst setup slack, exact violating nets, cell area, cell counts, estimated wire lengths, and capacitance proxy. No holdout workloads, frequency claims or power claims are authorized by these tests.
5. In parallel, retain the original *adaptive-repair* sweep as a distinct comparison: `(area, slack, electrical violations)` at each RC setting with full symmetric optimization. Never fit a single monotone RC coefficient to these two different experiments.

## Frozen decision boundaries

- Existing 3.5 ns physical gate: **fail** if any of the nine adaptively repaired cases has negative setup slack, nonzero slew/cap violations, or loses V296 area/timing dominance against the strongest control. No post-hoc exception for low RC.
- Fixed-topology sensitivity: **fail** if any supported RC/load condition introduces a V296-only electrical violation, or if the strongest control catches up in both area and timing. A failure may bound the valid operating region, but does **not** establish a positive law without independent confirmation.
- A positive architectural claim additionally requires detailed routing, extracted SPEF, corner-aware STA, equal-resource alternative, tile-level port/bandwidth and power proxies, prospective workload predictions, and independent reproduction.
- At the shared 3.5 ns clock and unchanged issue semantics, predicted throughput gain is **1.0**, regardless of positive setup-slack margin. Area-only density improvement is conditional on controller fraction of integrated tile area.

## Interpretation discipline

A larger *slack margin* is not a measured higher maximum frequency. Global-route RC is not detailed-route SPEF. An adaptive sweep that resizes cells is not a pure wire sensitivity test. A local controller-area saving is not a GPU area, power, or throughput saving. This protocol must not displace the existing failed low-RC electrical gate or open prospective holdouts.
