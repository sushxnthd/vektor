# Frozen RTL hypothesis Vektor-085b (before CI)

Original dynamic-index RF arbiter passed directed iverilog and Yosys generic-gate synthesis, but yielded **18,752 generic cells** and three memory-to-register warnings in run 38054349966. These are **not ASIC area or timing**.

**P11 DISCRIMINATION / CAPABILITY-BUILDING:** rewrite fixed-priority grants using a bank-major static loop and no variable-index integer array. Predict >=50% fewer generic mapped cells with the identical Yosys command and parameters, while preserving grants on 10,000 deterministic randomized vectors. Reject if equivalence fails or cell reduction is <50%. No novelty, 2.56 GHz, area or power claim.

Cheapest next: Yosys SAT equivalence and parameterized edge-case tests, then process-qualified timing.
