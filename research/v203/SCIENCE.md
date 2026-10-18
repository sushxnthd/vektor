# SCIENCE ledger — V203

Hypothesis: an instruction whose two source operands identify the SAME physical register consumes only one bank read, and fixed-priority bank contention then yields a predictable, alias-dependent issue gain.

Exact all-hot four-request law: E[G]=1+p*(1-(1-p)^3). Derivation: first request must be alias (probability p), and at least one of the remaining three must be alias (probability 1-(1-p)^3) for a second grant. Baseline E[G]=1. For p=0, equality; for p=1, E[G]=2.

Local Python evidence: five tests PASS; independent checker PASS 2,048 capacity cases; 9 frozen synthetic 4096-cycle traces. This is a model only. GitHub RTL CI should be inspected by SHA, not assumed.

No novelty claim: BOW (2020), Memento/Malekeh (2024), Triple-A (2024) already establish broad operand bypass/cache ideas. This specific trivial duplicate-source optimization is likely known. Publishable threshold: independent novelty, matched physically feasible Pareto frontier, unseen real workload verification. NOT MET.
