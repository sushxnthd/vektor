# Vektor-137 — max-cardinality RF admission

Research branch only. Canonical 16-bank, two-read-per-bank, four-slot RF issue arbiter has a reproducible first-fit cardinality gap under identical resource budgets.

Preregistered exhaustive four-bank enumeration: 7,896/65,536 four-slot vectors improved by exact subset selection; no exact cardinality regressions. Independent C++ replication passed all 65,536 vectors. Seeded 16-bank discovery: 976/8,192 improved; independent holdout seed 138: 1,006/8,192 improved. Strongest gains concentrate in deliberately hot-bank/pair motifs. Under uniformly random 16-bank sources, improvement is rare. **Software-model results only; no RTL simulation, PPA, area, clock or GPU IPC validated.**

The alternative selects a maximum-cardinality feasible subset of the four requests, ties preferring earlier slots. It can displace earlier requests and requires fairness analysis. It is not yet a recommended replacement for the canonical greedy arbiter. Two RF reads are charged even when both source bank IDs match, consistent with canonical source. Three-source FMA operand delivery remains unvalidated.

Source: main `rtl/vtile/rf_bank_arbiter.sv` blob `ea38a7401c4916df302f7c2eb55f6c082399824a`. Next decisive gate: RTL simulation + generic Yosys synthesis, then multi-cycle fairness and equal-cost comparisons.
