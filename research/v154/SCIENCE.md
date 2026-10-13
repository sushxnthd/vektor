# V154 SCIENCE — cutset timing test

Active question inherited from V153: Does a signed-accumulation pipeline boundary reduce worst stage depth and improve matched mapped area-normalized throughput?

Frontier: V151 14,459 generic cells / 383 levels; V152 LOD failed (19,981 / 439); V153 24,220 exact RTL vectors passed in 34,986 cycles with stalls, tags and masks. These are build results, not a new law.

Exact V154 objective: same-tool generic cell and topological path measurements for V151, V153 prepare, and V153 finish. Compare max stage path with 383; include pipeline-register cost. Follow with mapped timing and equal-resource throughput.

Mechanism prediction: max stage depth <383, with 138 bits/lane of intermediate state and +1 cycle latency. Falsify if either stage >=383 or mapped area-normalized throughput fails to improve. Strong equal-resource baseline: V151 with matched elastic storage, lane count, constraints and external CVFPU/HardFloat comparison before any competitive claim.

Publishable: novel mechanism plus >=5% independently replicated matched mapped throughput benefit on unseen compute/memory/divergent kernels. Architecture relevance: >=10% mapped Fmax at <=10% area cost and <=5% dependent workload slowdown. Kill after three substantive runs with no improvement or informative boundary.

No novelty claimed. V154 adds synthesis evidence, not a GPU equivalence claim.
