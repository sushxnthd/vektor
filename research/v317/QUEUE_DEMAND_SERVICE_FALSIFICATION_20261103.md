# V317 queue-demand service falsification — 2026-11-03

## Claim tested
A larger instantaneous bank-service capacity does **not** imply a larger completed-work rate when offered demand is insufficient, or when the observation window includes enough idle time to drain both systems.

## Reproduction
`python3 research/v317/queue_demand_service_falsification.py`

Deterministic 1,000-cycle fluid/integer-request queue with arrivals before service; baseline serves one request/cycle and a hypothetical zero-cost oracle serves two. The capacity doubling is an illustrative upper-bound countermodel, **not** a measured V317 hardware speedup.

| Frozen control | Offered arrivals | Baseline completed / residual | Oracle completed / residual | Completed-work ratio |
| --- | --- | --- | --- | --- |
| Low demand | 1 per cycle for 1,000 cycles | 1,000 / 0 | 1,000 / 0 | 1.0 |
| Saturated | 2 per cycle for 1,000 cycles | 1,000 / 1,000 | 2,000 / 0 | 2.0 |
| Burst then drain | 2 per cycle for 100 cycles, then zero for 900 | 200 / 0 | 200 / 0 | 1.0 |

Conservation invariant: `completed + residual_backlog = total_arrivals`. For an arrival rate λ and capacity μ in a stable, sufficiently long stationary system with no drops, throughput is bounded by `min(λ, μ)`; finite-window completed work also depends on initial/final backlog. In the simple constant-rate saturated model, the oracle/base completion-rate ratio is `min(λ, μ_oracle)/min(λ, μ_base)`. This is a *queue-level necessary demand boundary*, not a V317 performance law.

## Consequence / gate
The prior V317 bank-service oracle headroom cannot be reported as GPU IPC or sustained throughput. A credible workload-level validation needs measured ordered arrival traces, occupancy/backpressure, queues, stalls, memory traffic, issue dependencies and clock/electrical penalties. Report both steady-state completions and backlog/latency, with equal-resource controls and identical workload arrivals. The real matched compact-greedy baseline already falsified V317's positive area/electrical claim, which remains binding. No mechanism promotion, no RTX-5090 equivalence, and no inference about V296/V287.

## Evidence tier
Script executed locally with all assertions passing before GitHub commit. Hosted CI not verified. Toy deterministic queue, no RTL, synthesis, GPU traces, or physical design.
