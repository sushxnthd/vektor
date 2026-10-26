# V296 multi-resource tile law: prospective empirical falsification (2026-10-26)

## Status and purpose
Preregistered **before running the new stochastic workload experiment**. V296 pairwise arbitration is the only active mechanism; V287 is retired. This experiment is a falsification of the previously conditional *mapped-area replication opportunity*, not a GPU throughput measurement or a physical repair. Preserve all previous routed and failed results, PR #13, and all real GPU holdouts.

## Frozen model and competing controls
Use unchanged independently measured four-way Nangate45 mapped areas A_v=9286.592 and A_s=9844.926 square micrometers, and the existing exact independent bank admission expectation q=957548877/320000000 waves/cycle for B=16 banks, P=2 reads/bank, four issue slots, p=0.8 valid probability, rho=0.2 same-bank operand probability. Both V296 and serial have **identical admissions at the same clock**; no issue-IPC benefit is attributed to arbitration. Equal-area budget N=17 serial slices permits at most floor(17*A_s/A_v)=18 candidate slices **only hypothetically**.

Model expected useful wave rate per nanosecond:
R_x = min( n_x * q * u_x / (T_x*(1+o_x)), B_bytes_per_ns / m_bytes_per_wave, P_shared_reads_per_ns / 2 ).
This assumes work-conserving shared fluid service, identical bank-demand distributions, independent slice occupancy, fixed bytes/wave m=4, no inter-slice wiring penalty, and enough other physical resources for replication. It is an **optimistic bound**, not physical evidence.

## Prospective win and no-win regimes
Freeze occupancy u=0.85, control overhead o=0.03, baseline T_s=3.5 ns, 17 baseline slices, 18 candidate slices, two reads/wave. Freeze four regimes before running validation:
1. **Predicted conditional win**: candidate T=3.5 ns, shared B=100 GB/s, shared read budget=100 reads/ns. Expected +1/17=+5.88235%.
2. **Predicted bandwidth no-win**: candidate T=3.5 ns, B=10 GB/s, read budget=100 reads/ns. Expected 0%.
3. **Predicted port no-win**: candidate T=3.5 ns, B=100 GB/s, shared read budget=4 reads/ns. Expected 0%.
4. **Predicted clock-regression loss**: candidate T=3.745 ns (+7%), B=100 GB/s, read budget=100 reads/ns. Expected 18/(17*1.07)-1, about -1.04%.

## Independent empirical validation
After preregistration, implement a seeded request-level discrete-cycle simulator that *independently* generates each wave's valid flag and two bank indices; admits in slot order only when neither bank exceeds two ports; models per-slice active probability u/(1+o); and drains a persistent backlog under both global caps. Do not use q as a simulator input; derive admissions from generated requests. Use paired common-random-number workloads (same first 17 slices) to reduce comparison variance. Freeze holdout seeds 41213 and 49531, 20,000 cycles each. Accept q error <=0.03 waves/cycle and relative candidate/baseline gain error <=0.02 absolute in each regime. Independently test two-port enforcement and a deliberately wrong one-port mutation. Keep the previous GPU workload holdouts sealed.

## Decision and physical limitations
If the conditional-win regime fails empirical prediction, falsify the simple fluid law or its independence assumptions. If the bandwidth/port regimes show a material win, investigate simulator error. No physical victory unless candidate and independently optimized serial both close routed timing/hold/electrical checks and strict matched consumed resources. A +7% clock regression should eliminate the optimistic 17-slice opportunity. The latest post-CTS critical-path diagnostic remains the priority for actual hardware repair; do not confuse this synthetic tile-boundary test with routed GPU evidence.
