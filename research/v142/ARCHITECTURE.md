# Vektor-142 — architecture ledger

V141's existing `vektor_wave32_operand_gate` already fans out one 1024-bit `wb_value` to all matching source comparators. V142 adds a registered Wave32 capture candidate and a dedicated directed multicast testbench. No FMA arithmetic in this block; it is a collector datapath component.

Decision: count **distinct producer Wave32 writebacks**, not logical dependent source slots, when estimating bypass bus traffic. Do not add bus slots merely because one instruction uses the same producer in 2 or 3 source positions. Do not choose the reservation cap based on the original V141 holdout alone. Include duplicate-read RF coalescing in the next equal-resource control.

Evidence: 480 frozen Python/C++ comparisons plus 360 targeted checks; glibc fmaf final states checked in software, one representative lane per wave. RTL source is a candidate; no V142 HDL simulation, generic cell counts, mapped area, timing, power or silicon measurement. Vektor-1A design and 5090 reference are targets, not measured equivalence. Gates: FP32, matrix, graphics, ray, memory, NoC, software, physical feasibility INCONCLUSIVE; reproducibility partial software evidence only.

Next decisive experiment: simulate `tb_wave32_broadcast_capture` with Icarus, synthesize candidate and V141 baseline with Yosys, then test realistic reuse traces and timing of 1024-bit fanout. Preserve failed P1/P2.
