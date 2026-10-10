# Vektor-085b RTL synthesis foothold and formal preregistration

Date 2026-10-10. Frozen prediction P11 (before synthesis) was >=50% reduction in generic mapped cells with identical default parameters and 10,000 deterministic equivalence vectors.

**Observed:** original variable-index grant RTL: 18,752 Yosys generic cells (run 38054349966). Bank-major static-index equivalent: **2,036 Yosys generic cells** (run 38054472444). Reduction = **89.1425%**, ratio 9.21x. The 10,000-vector directed equivalence test passed. Both synthesized with `proc; opt; techmap; opt; stat`. This is a coding/synthesis efficiency result, **not** ASIC area, clock rate, power or architectural novelty.

**P12, preregistered before next CI:** a separate Yosys formal equivalence flow (`equiv_make; equiv_simple; equiv_status -assert`) should prove the two combinational grant modules equivalent for the default parameterization. If the proof fails or times out, the evidence remains randomized-only. Next test multi-parameter variants and formal safety invariants; investigate fairness/starvation and sequential WB reservation hardware.
