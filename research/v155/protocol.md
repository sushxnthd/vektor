# V155 SCIENCE and ARCHITECTURE

## SCIENCE ledger
Question: Can a registered signed-accumulation cutset improve the area-delay-throughput Pareto frontier of Vektor's FP32 execution finisher versus an equal-latency buffered baseline?

Frontier: V151 passes 24,220 RTL vectors, 14,459 generic combinational cells, 383 generic levels. V154 cutset passes the same corpus, 15,404 generic combinational cells and 215 maximum stage levels. Generic metrics are not mapped physical PPA.

Exact objective: LANES=1, TAG_BITS=8, identical two-stage elastic capacity and output rate; compare oracle correctness, whole-module mapped cell area including registers, and combinational path proxies with one pinned Nangate45 library and identical Yosys commands. Physical timing and workload throughput remain separate future gates.

Strongest internal equal-resource baseline: V151 with raw-input and output elastic registers. Same lanes, latency, tags, masks, and stalls. Strong external matched CVFPU/HardFloat comparison is required before competitive claims.

Mechanism: cutting after signed accumulation shortens the longest combinational cone but adds interstage state. Predict faster independent FP32 at sufficiently improved Fmax; predict a dependency-latency reversal when chain length or stall fraction dominates.

Decisive falsification: any mismatch on the 24,220-vector oracle or lack of area-normalized mapped throughput improvement. Library-mapped structural depth alone does not establish success.

Publishable threshold: novel mechanism (ordinary retiming excluded), at least 5 percent independently reproduced equal-resource benefit versus strongest open baseline, quantitative crossover, holdouts, independent checker, novelty audit and uncertainty.

Architecture threshold: at least 10 percent mapped Fmax improvement, no more than 10 percent mapped area cost, and no more than 5 percent slowdown on dependent, divergent, or memory-stalled kernels.

Reformulate after three substantive runs without improved evidence or a new boundary. Infrastructure failure is not scientific failure. Allocate roughly 10 percent of cheap probes to workload-latency reversals.

## ARCHITECTURE ledger
Affected block: post-multiply Wave32 FP32 finisher. Build work: two-stage buffered V151 control and CI mapping. Research evidence: compare complete one-lane sequential blocks; keep raw mapping logs even on failed runs. Decision: retain V151 pending mapped STA and realistic kernel results; do not promote V153 based only on generic depth. Next build gate: tagged scoreboard and architectural writeback.

Evidence class: RTL and open-library mapping, not physical placement/routing, power, or silicon. No novelty and no RTX 5090-class equivalence claim.
