# V293 — bank-local operand bypass topology (sole active E0 hypothesis)

1. Bottleneck: global 4-entry bypass cache may have long data wires; four bank-local one-entry caches exchange associativity for shorter wires.
2. Mechanism: four 1-entry local tag/data/valid banks, same four total entries and RF ports as control, no global hit crossbar.
3. Strong control: optimized global four-entry associative cache, plus an equal-budget partitioned/banked cache. Kill if banked control is equivalent.
4. Derived energy boundary: local wins iff (hL-hG)*ER + hG*EG - hL*EL + CG-CL > 0, where h are hits, ER is RF-read energy, E are bypass-hit energies and C are control energies. Fmax and area are independent mandatory gates.
5. RTL: 4 local 32-bit entries, tag match, valid/reset/update; matched global 4-entry control and same read/write interface.
6. Physical: Icarus, Yosys/Nangate45, OpenSTA, max-cap/slew, switching; 0.5/1/2x load and wire-length sensitivity.
7. Workloads: compute, memory, divergent; hits, physical RF reads, operand throughput, area/delay/toggle energy.
8. Falsify on functional failure, global/banked equal-budget dominance, no clean timing, or no robust energy/throughput Pareto region.
9. Unseen: freeze one high-bank-locality positive regime and one concentrated-bank four-address negative regime before evaluation.
10. Tile: only operand-bypass placement if validated; otherwise V-Tile unchanged.

Prior art: banked operand collectors, operand caches and forwarding are established; novelty unproven. No RTX 5090 comparison. Next run MUST implement matched RTL and physically characterize or kill, not package E0 wrappers.
