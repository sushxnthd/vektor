# V155 SCIENCE ledger

Active question: Can the signed-accumulation cutset beat the equal-latency buffered V151 FP32 finisher in mapped area-delay-throughput?

Frontier: V154 RTL correctness 24,220 vectors and maximum generic stage depth 215, versus V151 383. No physical timing.

Objective: same one-lane, two-stage elastic interface, same library and synthesis flow; measure whole-module mapped cell area, mapped delay, and end-to-end throughput.

Baseline: two-stage buffered V151; stronger external CVFPU/HardFloat comparisons remain required.

Hypothesis: splitting accumulation and rounding shortens critical combinational timing without unacceptable storage overhead. Prediction: independent throughput can rise with clock rate; same-latency controls must have equal cycle counts at equal clock.

Falsification: oracle mismatch or no mapped area-normalized throughput benefit. Publishable threshold: novel mechanism, at least 5 percent replicated gain on unseen workloads and independent checker. Architecture threshold: at least 10 percent mapped Fmax at at most 10 percent area cost and at most 5 percent dependent workload regression.

Stop condition: reformulate after three substantive uninformative experiments. Wildcard: 10 percent on dependency and backpressure boundaries.

Result: 24,220 RTL passes for both, 0.1786 percent less mapped area for cutset, 161 DFFR_X1 in each. This falsifies the expected extra flop-count penalty in this optimized netlist, not the scientific null. No mapped timing or novelty yet.
