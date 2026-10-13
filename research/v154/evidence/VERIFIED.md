# V154 verified synthesis result (2026-10-13 UTC)

Actions run 38459477252 SUCCESS; artifact 11845560121.
Icarus RTL 24,220/24,220 frozen vectors PASS; tags/masks/backpressure, 34,986 cycles.
Yosys 0.33 generic synthesis, W=64, identical command options:
V151 baseline: 14,459 generic cells, longest topological path 383.
V153 prepare: 7,318 cells, path 195.
V153 finish: 8,086 cells, path 215.
Maximum per-stage generic depth 215: 43.86% reduction versus 383.
Sum of combinational generic cells 15,404: +6.54% versus V151, EXCLUDING pipeline registers, clock distribution, interconnect and physical mapping.
Intermediate state 138 bits per lane (4,416 bits for Wave32) plus tag/mask/valid.

Frozen corpus SHA256: 18f8f27a5aac0309776b576b281368dff522820512f46019af9fbec78b2d8a71.
Raw artifact: https://github.com/sushxnthd/vektor/actions/runs/38459477252/artifacts/11845560121

SCIENCE: conventional pipelining, no novelty; area-delay Pareto and physical timing unproven.
ARCHITECTURE: candidate timing cut is promising but V151 remains baseline until technology mapping, matched buffering, and workload holdouts.
