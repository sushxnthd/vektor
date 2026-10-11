# Vektor-111 preregistration — 2026-10-11

Classes: DISCRIMINATION, CAPABILITY-BUILDING, SURPRISE. Evidence: host abstract SC model.

Mechanism: V110 aliases same-number addresses across distinct CTA-shared/thread-local instances, and imposes globally ordered epochs. V111 qualifies memory by (space, instance), uses CTA-local epochs, and includes CTA in Wave32 instruction homogeneity. Global conflicts retain conservative SC reference order.

Locked random experiment: 192 discovery seeds 111000..111191, 96 holdout seeds 811000..811095, 36 minimally guided surprise seeds 511000..511035 (11.1%). Six schedules per pair, plus 11 directed controls. Independent C++ and Python must agree. Predicted: disjoint shared/local instances can reverse; same-instance overlapping writes cannot; cross-CTA epoch does not synchronize; malformed waves fail; byte-replay outputs of admitted pair reversals remain unchanged.

Limitations: this is NOT a real GPU memory model or trace, and cannot establish scheduling speedup. Next: instrument Vortex SimX LSU and independently run RTL verification/synthesis.
