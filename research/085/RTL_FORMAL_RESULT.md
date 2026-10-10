# Vektor-085b formal RTL and synthesis result — 2026-10-10

**Preregistered P11 PASSED:** Bank-major statically indexed grant RTL reduced generic Yosys cell count from **18,752** to **2,036** under the same default parameterization and synthesis command (`proc; opt; techmap; opt; stat`). Difference = 16,716 cells, **89.1425%** reduction. Original Yosys run: https://github.com/sushxnthd/vektor/actions/runs/38054349966 . Optimized run: https://github.com/sushxnthd/vektor/actions/runs/38054472444 . 10,000 deterministic randomized Icarus Verilog output-equivalence vectors passed.

**Preregistered P12 PASSED:** Yosys `equiv_make; equiv_simple; equiv_status -assert` proved **76/76 equivalence cells**, zero unproven, for the default parameters. Source run: https://github.com/sushxnthd/vektor/actions/runs/38054563107 . This is **formal combinational equivalence between two grant implementations**, not formal proof of correct RF bank grants, fairness, forward progress, or a sequential writeback reservation table.

Evidence classes: **SYNTHESIZED (generic gate count only)** and **FORMALLY VERIFIED (bounded combinational implementation equivalence)**. There is **no** process-qualified standard-cell area, place-route timing, clock frequency, power or silicon measurement. This is a Vektor-specific RTL implementation improvement, not an original GPU architecture or scientific novelty claim.

**Mechanism:** dynamic-index integer arrays caused large mux/decoder overhead in Yosys; a bank-major static loop reduces mapping complexity while preserving grant semantics.

**Next decisive experiment:** formal bank-capacity/validity assertions across parameterizations; implement and verify a sequential future-writeback reservation table, and measure real synthesis timing/area. Full RTX 5090-class gate remains **INCONCLUSIVE**.
