# Vektor-083 preregistration (frozen before experiment)

Mechanism: a finite ready FIFO may decouple operand collectors from four-wide issue, but it consumes storage and introduces an additional pipeline boundary.

P1: four-wide issue and FIFO capacity are hard throughput ceilings. P2: a single-bank hotspot is unaffected by more queue capacity. P3: equal total instruction storage (collector slots plus queue slots) can reverse benefits from adding a queue. P4: FIFO depth has nonmonotonic performance under fixed storage. Controls: identical banked workloads, seeds, RF ports, issue width and total storage slots. Experiments: 630 controlled configurations and 90 minimally guided probes; heterogeneous holdout frozen before evaluation.

Class: DISCRIMINATION / CAPABILITY-BUILDING / SURPRISE. All numbers are simulated, not silicon results.
