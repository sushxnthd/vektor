# V250 frozen protocol (2026-10-21)

Sole active kernel: four-entry tile-local integer-add atomic aggregator. No experiments or PPA claims yet.

1. Bottleneck: A saturated atomics at service rate mu take >= A/mu cycles. Combining k compatible operations reduces external requests toward A/k, but only if wait/compare/timing costs are smaller than saved service time.
2. Mechanism: combine 32-bit integer-add atomics with matching 16-bit addresses in a four-entry associative queue; retain contributor masks; preserve modulo-2^32 arithmetic. Scope: relaxed, no-return operations only.
3. Equal-resource baseline: strongest four-entry inter-warp hardware atomic combiner, plus compiler warp aggregation and simple FIFO, all with identical storage, ports and bandwidth.
4. Win boundary: A/mu-A/(k*mu) > batching wait + overhead. No win under random addresses or low service utilization.
5. Smallest RTL: four tagged queue entries, one input, one output, 32-bit sums and a contributor mask; independent conservation check.
6. Physical: Python oracle, RTL simulation, Yosys synthesis, electrical max-cap/slew, matched STA/area, switching proxy at several loads. No survival on cycle model alone.
7. Workloads: compute, low/high-contention memory and divergent active masks; record external transactions, latency, throughput, area and timing.
8. Falsification: arithmetic/order error, loss to equal-resource hardware combiner, or unqualified PPA within two substantive runs.
9. Frozen unseen: H+ seed 250101, 16 warps, 80% of atomic adds to one hot address, saturated interface, predict >20% traffic saving against noncombining FIFO conditional on queue residency; H- seed 250102, 16 warps, uniform 16-bit addresses, predict <2% saving and no throughput win. 2 percentage-point traffic tolerance. Neither guarantees a win against strongest hardware control.
10. Architecture: integrate only with independently verified incremental equal-budget Pareto improvement; otherwise retain existing atomic combining.

Prior art: warp-aggregated atomics and inter-warp hardware combining are known; first test is whether any distinct mechanism remains after matching strongest control. V249 retired; FP32 V153/V156 still electrically disqualified.
