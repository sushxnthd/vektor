# V278: Balanced bank-aware register allocation

Sole active architecture-science kernel. V277 is retired: its original positive R4/M2/K8 trace had 680 RF reads versus 640 for LRU; the two-bit reload-to-max control tied V277 at 680 with fewer modeled counter transitions. No characterized physical advantage was established. Frozen V277 holdouts remain unopened.

Mechanism: remap eight simultaneously live logical registers to eight physical registers, exactly four per bank, to minimize weighted same-bank source pairs. The RF bank ports, storage, datapath and RTL are identical to the fixed-hash control. Baseline: best of all seven balanced affine/parity bank assignments, chosen separately for each workload. Candidate: optimal balanced assignment among 35 partitions, selected by compiler without added runtime hardware. No extra registers, moves or spills permitted.

Law: if conflict fraction is c and other throughput ceiling is m, issue rate is min(m,1/(1+c)). Predicted gain is the ratio of rates after and before allocation. It is zero when another bottleneck dominates. An eight-register synthetic graph is not a GPU benchmark.

Physicality gate: confirm actual compiler register assignment preserves dependencies and register pressure; RTL simulation, unchanged mapped netlist, fresh cap/slew/STA and workload measurements. A prior-art audit of bank-aware register allocation is required before novelty claims. Frozen unseen positive: non-affine balanced complete-bipartite pair graph, mask 46, RF-bound; expected gain at least 1.0625. Frozen unseen negative: affine graph mask 170 or non-RF issue ceiling 0.25; expected gain 1.0. Neither has been evaluated. No breakthrough or integrated-tile change is claimed.
