# ARCHITECTURE V174

Decision: Retain V151 as functional reference and V153 as the cutset timing candidate. Do not conclude V153 reverses at 4.63 ns: the control design's input-launched path may become critical and move its timing envelope.

Metric: constrained period-minus-slack and mapped area-delay, at matched clock, library, latency, slew, load, and input delay. These are not routed PPA or measured throughput.

Next highest-information experiment: execute the already committed V173 seven-point matched OpenSTA sweep; report worst path class and the actual control crossover. Preserve the original V156 workflow failure and the later successful rerun. If the sweep is blocked, use path-restricted OpenSTA to measure control's worst input-launched path at the reference delay.

Science consequence: timing guarantee horizons are mathematically bounded, but a real crossover is not measured.

GPU build consequence: only integrate V153 after robust operand-arrival timing and full Wave32 equivalence; then continue tensor, memory/NoC, and compiler/ISA gates.

Wildcard: compare input-arrival distributions from a register-file bypass path versus a staged operand collector; do not change the active kernel without measured evidence.

Blocked: V174 remote OpenSTA and equal-total-area physical synthesis remain pending.
