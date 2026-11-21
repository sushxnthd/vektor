# V317 staged-service boundary extension, frozen before test implementation (2026-10-31)

This is an analytic synthetic follow-up to the earlier staging protocol, **not** a real GPU prospective workload. The hypothetical removal of the B read from AB is not implemented in hardware.

Equal-resource abstraction: three independent single-read-port banks, issue/completion cap two instructions/cycle, unlimited operand buffers, arbitrary staging across cycles, all operands initially ready, no control/timing/occupancy cost. Define a,b,c as numbers of AB,BC,CA instructions and N=a+b+c.

Capacity lower bounds:
- L0 = max(ceil(N/2), a+c, a+b, b+c)
- L1 = max(ceil(N/2), a+c, b, b+c)
- G_bound = L0/L1, **not** a universal exact achieved speedup.

Frozen predicted feasible schedules (witness required, no hindsight tuning):
- Bank-B limited predicted win (a,b,c)=(2,2,0): baseline 4 cycles, candidate 2; gain 2.000x.
- Balanced predicted no-win (2,2,2): baseline 4, candidate 4; gain 1.000x.
- Unseen count-transfer (2,1,0): baseline 3, candidate 2; gain 1.500x.

Independent witness validator must check bank-port exclusivity, exactly-once reads, all instruction completion, at most two completions/cycle, and matching the lower bound. Any failure rejects the exactness assertion for that workload. No inference about RTL, cache behavior, real bank mapping, or GPU throughput is permitted.

Boundary: reducing B-bank demand can only help this optimistic staged-service capacity envelope if the original B demand a+b is a **strict** maximizer over the unchanged issue/A/C constraints. The realized benefit also requires an implementable read-elimination mechanism, bounded-buffer feasibility, and physical timing/power survival.
