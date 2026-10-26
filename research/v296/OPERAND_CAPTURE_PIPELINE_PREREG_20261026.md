# V296 symmetric operand-capture retiming: frozen falsification protocol (2026-10-26)

**Pre-outcome registration.** This is an implementation-level *repair experiment*, not a second architecture mechanism and not evidence of a GPU speedup. The original V296 pairwise and optimized serial one-hot architectures, original return-tree RTL, original failed routed experiments, and all real workload holdouts remain untouched. V287 remains retired.

## Intervention and physical hypothesis

The frozen fourth-stage pre-CTS result shows scheduler RR state -> RF selection -> execute arithmetic -> `executed_data` as the critical path in **both** contestants. At 3.5 ns and +50 ps setup guard, the pre-CTS deficits are 320.212 ps for V296 and 805.018 ps for serial, before CTS/route. Test one *symmetric* operand-capture boundary: register eight 8-bit RF operand values, four 5-bit wave IDs and four valid bits at the original execution edge; perform the original arithmetic into `executed_data` one edge later. Preserve issue grants, four slots, 16 banks, two read ports per bank, one RF write port, and identical RF read-before-write semantics. No speculative bypass of port constraints. Both architectures receive precisely the same retiming. The original non-pipelined controls remain unchanged.

The hypothesis is **not** that the extra registers necessarily help: the first stage still contains scheduler, bank lookup, arbitration, RF selection and crossbar. The second stage contains arithmetic. The test can falsify this split as insufficient, area-expensive, or timing-infeasible. Pipeline initiation interval is nominally one cycle; visible execution latency increases exactly one edge. Every cycle of original `executed_data` must equal the retimed output on the following edge (after reset warmup), including RF writes and conflicting-bank requests. Report the extra latency and flop/area cost explicitly; do not call this cycle-identical output equivalence.

## Ordered tests and kill rules

1. Four-way RTL regression against original pairwise and serial with the existing direct-index RF oracle, plus a delayed-output scoreboard for both retimed implementations, including random RF writes and same-bank conflicts. Check `issue_valid` and all four IDs cycle-for-cycle. If any scoreboard, port-accounting, or X-propagation check fails, reject immediately.
2. Same-library mapped synthesis of both retimed contestants and both non-pipelined balanced-return controls. Record flop count, area, graph depth and source hashes. Mapped graph depth is **not** STA or signoff. If extra area negates the claimed area edge against serial, mark area superiority falsified.
3. Paired, same-fourth-stage pre-CTS OpenROAD timing/area and critical-path report at 3.5 ns, identical placement density, RC and constraints. Preserve serial's independently optimized fifth-stage control for final comparison. If the pairwise stage-1 critical path still violates +50 ps guard, do not advance a frequency/speedup claim. If this short experiment fails or times out, preserve it as incomplete rather than inventing a result.
4. Only after passing the above, commission matched post-CTS/detailed-route extraction with zero negative hold, zero cap/slew/DRC violations and +50 ps setup guard, *including* strongest fifth-stage serial. If either is infeasible, reject feasible-Pareto claims. No RTL-only success can override physical failure.

## Frozen prospective workload boundaries

**Potential win**: independent requests with sustained occupancy, low bank collisions, enough bandwidth and no data dependencies, *only if* extracted clock and equal-consumed-area allocation favor V296 after retiming. With same feasible clock and same slice count, predicted V296-vs-serial admission gain is exactly zero.

**Predicted no-win**: shared bandwidth saturated, or dependency chains requiring execution completion before new issue. Even if frequency improves, useful throughput is capped by bandwidth or the extra one-cycle dependency latency. The current request generator has no scoreboard dependencies; it cannot establish the latter regime without an added dependency-aware simulator.

Any surviving claim must predict throughput from measured clock, resource packing, correlated bank compatibility, occupancy, port pressure, bandwidth, and the added latency/forwarding cost. Never use mapped area as proof of replicable tile area, nor capacitance proxy as measured power. Preserve unseen holdouts until a genuine physical pass.

**Evidence tiers:** RTL pass < mapped synthesis < pre-CTS timing < routed extracted closure < equal-resource workload transfer. V296 remains the sole active architecture candidate under falsification. No RTX-5090 equivalence or world-class completion is claimed.
