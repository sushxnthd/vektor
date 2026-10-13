# V153 ARCHITECTURE

Affected block: Wave32 FP32 finisher after V148 multiplier and operand collector.

Candidate: register signed magnitude and exponent metadata before RNE pack, retain elastic ready/valid, tag and mask. Stage payload at W=64: 65 magnitude + 1 sign + 32 exponent + 1 tail + 1 opposition + 1 bypass + 32 bypass result + 5 flags = 138 bits per lane. This is a register-bit count, not physical area.

V151 single-stage correctness PASS; V152 balanced leading-one FALSIFIED; V153 two-stage differential verification and generic synthesis pending. Full scoreboard, RF writeback, mapped timing and realistic workload gate not passed.

Promote only with frozen 24,220 oracle agreement, exact tag/backpressure checks, lower per-stage delay, matched mapped timing/area and no severe dependent-workload slowdown. Otherwise retain V151 and test narrower cutsets.

Consequence: influences feasible FMA clock, scoreboard hazard latency, issue occupancy and RF backpressure. Standard retiming is not scientific novelty. RTX 5090 equivalence remains unestablished.
