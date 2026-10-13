# V146 SCIENCE ledger (2026-10-13)

Active kernel: Does a two-response RF collector with writeback bypass preserve operand identity under stalls and duplicate sources, while enabling higher operand throughput than a one-response control?

Frontier: V144 dual-response combinational router; V145 fixed-parity topology falsified. Neither implements a registered collector.

Objective: zero mismatches over 1200 preregistered randomized cycles; generic synthesis evidence. The throughput/area Pareto is NOT yet tested.

Strongest equal-resource control: V144 two-response router with the same response width. V143 single-response design is a throughput reference, but interfaces differ.

Hypothesis: register operands once, multicast duplicate tags, gate irrelevant RF responses, prioritize WB bypass, and preserve tags/data under backpressure.

Predictions: no RF acceptance without a matching uncaptured source; a single response fills all matching duplicate slots; WB suppresses redundant RF acceptance; dispatch remains stable until ready.

Decisive falsification: any data/tag mismatch, spurious acceptance, lost response, bank-port violation, or changed dispatch operands under backpressure.

Publishable threshold: a novel GPU-performance mechanism beating strong prior art on unseen workloads and matched physical resources. Not met.

Architecture-relevance threshold: verified collector and measured integration cost, followed by executable FP32 FMA retirement.

Kill condition: repeated verification failure or cost/throughput regression versus equal-resource alternatives.

Evidence class: RTL candidate and testbench; CI simulation/synthesis pending. No novelty claim.

Wildcard: simultaneous WB/RF collision with duplicated sources under dispatch stall.

Next decisive experiment: run Icarus and Yosys; then integrate IEEE-754 FP32 FMA and scoreboard.
