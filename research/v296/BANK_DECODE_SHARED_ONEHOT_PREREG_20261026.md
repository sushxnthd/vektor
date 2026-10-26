# V296 symmetric bank-index decoder topology experiment (preregistered 2026-10-26)

**Mechanism:** V296 pairwise bank arbitration remains the sole active candidate; V287 remains retired. This experiment changes only the shared **32-wave-to-4-bit RF bank-index lookup implementation**, identically in V296 and the strongest serial-onehot comparator. It is not a new architecture mechanism and must not rewrite the original RTL, holdouts, or physical evidence.

## Evidence motivating the experiment

- Matched post-CTS detailed-route OpenRCX run 40309580865, original candidate artifact 12648648864 SHA-256 `057d4fe6d4bf67164857c54c9635c302e163da6b486f59515b7b8151578d8388`, serial artifact 12655030936 SHA-256 `1ea4affb6c1f583a775aa9ee084a9c6dcd0b7856d5b8fa1850693f2f05617f67`.
- Candidate extracted setup −1.047895 ns, hold −0.036622 ns, cap violations 3, slew 0, final cell area 17857.644252 µm². Strong serial setup −1.859922 ns, hold −0.019796 ns, cap 3, slew 0, final area 18953.830505 µm². Both **FAIL** frozen +50 ps setup, nonnegative hold, zero cap/slew/DRC gate. Area saving 5.7835% and setup lead 812.027 ps do not establish a viable design.
- Symmetric operand-capture pre-CTS experiment: V296 −0.025959 ns, serial −0.406435 ns at 3.5 ns. The measured V296 critical path ends at staged RF operand data and launches from scheduler RR state. Its +50 ps guard shortfall is 75.959 ps **before CTS/route**.
- These two physical tiers cannot be numerically subtracted to claim retiming benefit. The serial fifth-stage control repair must remain enabled in any final routed comparison.

## Frozen intervention and controls

Replace only the combinational `lookup_bank` function in a **copy** of `v296_tile_slice_operand_capture.sv`: instead of a variable 128-bit shift, use 32 parallel equality-masked 4-bit bank nibbles, reduced in a fixed balanced 32→16→8→4→2→1 OR tree. Do not change scheduler, issue semantics, RF capacity (16 banks × 2 reads), global write port, data width, RF contents, arbitration parameter, output latency, reset, clock, or physical constraints. Run this exact topology for both PAIRWISE=1 and PAIRWISE=0. A reduction in lookup depth is a **hypothesis**, not a measured fact; decoding and routing fanout may worsen area/timing.

**Stage A functional gate:** Icarus SystemVerilog testbench comparing original independent direct-index RF oracle, original operand-capture pairwise and serial, and both decoder variants over 2,048 cycles with writes, collisions, hotspot banks, and randomized bank maps. Require identical issue IDs/grants and one-edge-delayed execution outputs, zero bank-port overuse, no X outputs.

**Stage B mapped gate:** identical Nangate45/Yosys/ABC four-way synthesis of original retimed pairwise/serial and decoder pairwise/serial; record mapped area, flip-flops and logic depth. Reject decoder as an implementation repair if mapped area increases by more than 10% for either contestant or if functional gate fails. Logic-depth reductions alone are not proof of physical improvement.

**Stage C physical gate:** same pinned tools, 260×260 µm die/240×240 µm core, 3.5 ns clock, 0.45 placement density, 2× RC, original fourth-stage pre-CTS diagnostic, same setup/hold/electrical reporting. The decoder is worth full post-CTS evaluation only if candidate pre-CTS slack reaches at least +50 ps and serial is compared with its fifth-stage repair at the final tier. No selective density/clock/constraint tuning. If candidate remains negative at the pre-CTS guard, mark this repair **falsified**; preserve negative evidence.

**Final physical gate:** require both contenders' matched post-CTS detailed-route extracted-RC setup ≥ +50 ps, hold ≥0, zero cap/slew/DRC, area ≤30,000 µm². Include independently optimized serial fifth-stage control, sensitivity to wire/load, and true equal-resource tile-level comparison. No speedup claim if either design is infeasible.

## Prospective workload predictions, still unopened

- **Predicted conditional win:** abundant independent resident warps, bank-distributed reads, sufficient RF and memory bandwidth, and physically feasible area-reinvestment into one additional candidate slice under a fixed consumed-area budget. No same-clock/same-slice admission gain.
- **Predicted no-win:** bandwidth saturation or low-occupancy dependent warps; retiming adds one execution cycle and can erase any hypothetical area-packing advantage.
- A valid predictive law must include compatibility/bank collisions, overlap, ports, occupancy, dependency latency, control overhead, bandwidth and feasible clock. Existing sealed real-workload holdouts remain sealed.

**Decision policy:** This is an explicit *attempt to falsify a symmetric timing repair*. No GPU tile, SRAM macro, measured power, real Fmax or RTX-5090-equivalence claim is authorized by RTL, mapped, or pre-CTS success. Preserve draft PR #13; no merges, force pushes or changes to Kernellum PR #119.
