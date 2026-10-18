# V210 RF fallback physical gate

Parent V209: deferred bank-aware backup wave selection. This is the second and final physical qualification attempt; previous V209 RTL, synthesis and STA were not executed. The V153/V156 FP32 cutset remains unqualified and retired.

Gate: functional equivalence, differential RTL simulation, generic synthesis, mapped electrical max-cap/max-slew, matched STA, area/power and unseen workload validation. If these cannot execute in V210, retire the mechanism; no GPU throughput, silicon or novelty claim.

Existing inherited RTL/simulator Actions passing on the branch are not V209/V210 candidate validation. The candidate is not integrated into main.
