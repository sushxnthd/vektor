# Frozen finite-FIFO age-head scheduling transfer gate (2026-11-02)

## Prior negative evidence and scope
V317's area advantage is **killed** by the smaller compact-greedy physical control and illegal RF-proxy electrical checks. The earlier 65%-hot-bank head-preserving instantaneous predicted win failed. This experiment does not revive V317 or promote a second active mechanism. It tests whether a **strictly finite on-chip FIFO** and guaranteed service of the oldest request preserve any *throughput* advantage of an optimistic head-preserving subset selector. No GPU IPC, physical RTL, SRAM, calibrated power, or RTX-5090 claim is authorized by this test. Keep one branch and PR #34.

## Frozen model
- Same offered request stream for both schedulers; two independently consumed bank reads/request, including two reads for identical-bank operands. Two read ports/bank, 4 oldest requests eligible, 8-entry finite on-chip FIFO, at most K output grants/cycle.
- One scheduler is age-ordered work-conserving greedy (strong compact-greedy policy); challenger enumerates all feasible subsets of the oldest 4, **must serve the oldest** and maximizes grants, tie-breaking lexicographically in favor of older requests. Both select grants under the output cap (not after selection).
- Arrivals are generated independently of scheduler outcomes; a full FIFO applies backpressure to an upstream offered-workload source. Pending offered requests are retained **outside** the on-chip FIFO in a simulated unbounded source queue; source backlog is reported and is not counted as physical hardware. There are no dropped requests. Each cycle: append offers to source queue; admit until FIFO full; select and serve; update age and conservation.
- Three seeds 42011, 42013, 42017; warmup 3,000 cycles then measure 12,000 cycles per seed, deterministic same trace for each policy. All requests individually feasible, and oldest is always served when queue nonempty; therefore no on-chip request may wait more than seven complete cycles in the 8-entry FIFO. Report both on-chip and end-to-end waiting (unbounded upstream backlog may make end-to-end latency diverge).

## Regimes and predictions frozen before outcomes
1. `uniform16`: 16 uniform banks, 4 offers/cycle, K=4. **No material win**: challenger/greedy completed-service ratio <1.02.
2. `hot65_16`: 16 banks, bank 0 chosen independently with probability .65 per operand, other banks uniform 1..15, 4 offers/cycle, K=4. **No material win**: ratio <1.02; earlier instantaneous hot-bank prediction already failed.
3. `structured4`: four-bank repeated stream `[(0,0),(1,1),(1,2),(1,2)]`, 4 offers/cycle, K=4. **Candidate predicted win**: ratio >=1.02, because in the initial four-request snapshot greedy grants 2 while the head-preserving oracle grants 3. This is a constructed stress regime, not evidence of representative GPU traffic. If steady-state fails, retain the negative result without retuning.
4. `structured4_cap2`: identical structured stream, K=2. **Exact no-win**: ratio =1.000000000000 (within 1e-12), because any oldest-preserving selector can match but cannot exceed age-greedy service under output cap <=2.
5. `uniform16_lowload`: 16 uniform banks, 1 offer/cycle, K=4. **Exact no-win**: ratio =1.000000000000 (within 1e-12).

## Independent audit and falsification
- Separately implemented recursive exhaustive subset checker for 4-request combinations; exhaustive four-bank 4^8 cases to verify greedy and head-preserving grant counts with K=2 and K=4.
- Verify each trace's offered/accepted/completed/upstream/FIFO conservation, FIFO capacity <=8, bank port legality, oldest service and maximum on-chip wait <=7 cycles.
- For a positive candidate, require >=2% sustained service improvement and no worse p99 on-chip wait than greedy. Report any tail regression even when throughput improves. The observed win must not be inferred from an instantaneous oracle ratio.
- An observed improvement here is only synthetic queue-level evidence; actual positive promotion additionally requires a bounded-cost RTL implementation and legal matched-resource timing, electrical and area results against compact greedy.
