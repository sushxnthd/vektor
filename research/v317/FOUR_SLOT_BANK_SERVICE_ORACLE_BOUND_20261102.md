# V317 follow-up: four-slot bank-service upper bound and negative transfer (2026-11-02)

## Provenance and scope

The [frozen protocol](FROZEN_FOUR_SLOT_BANK_SERVICE_HEADROOM_20261102.md) was committed at `f71e494` **before** writing the evaluator (`04c70b5`), independent checker (`8affb57`) or evaluating the frozen regimes. Reproduction: `python3 research/v317/rtl/bank_service_oracle.py > /tmp/vektor_headroom.json && python3 research/v317/rtl/audit_bank_service_oracle.py /tmp/vektor_headroom.json`. No external packages. Three frozen seeds, 20,000 batches each (60,000 per distribution), 4 candidates, 2 operands/request, 2 read ports/bank. The comparison is against *compact fixed-priority greedy* with identical bank-port limits. The exhaustive oracle is **not** an RTL mechanism; it ignores fairness, critical path, area, power, queues, wire, and memory latency.

## Frozen constructed controls

| Regime | Greedy grants | Oracle grants | Instantaneous service ratio |
|---|---:|---:|---:|
| Head-blocker win [(0,1),(0,0),(1,1),(2,2)], cap 4 | 2 | 3 | **1.500000x** |
| Disjoint, cap 4 | 4 | 4 | **1.000000x** |
| Same head-blocker, output cap 2 | 2 | 2 | **1.000000x** |
| All operands bank 0, cap 4 | 1 | 1 | **1.000000x** |

The 50% gain is **an adversarial four-request construction**; it is not representative workload evidence.

## Prospective stochastic regimes (60,000 independent batches each)

| Regime | Greedy mean grants | Oracle mean grants | Upper-bound ratio | Improvement probability |
|---|---:|---:|---:|---:|
| Uniform 16 banks | 3.820900 | 3.824817 | **1.001025x** | 0.003917 |
| Uniform 4 banks | 2.607683 | 2.729417 | **1.046683x** | 0.121733 |
| 65% hot-bank, 16 banks | 1.910500 | 2.101300 | **1.099869x** | 0.190800 |
| 65% hot-bank, cap 2 | 1.682633 | 1.833133 | **1.089443x** | 0.150500 |
| 70% same-bank operands, 16 banks | 3.534183 | 3.542233 | **1.002278x** | 0.008050 |
| Uniform 16 banks, 60% request-valid | 2.348400 | 2.348967 | **1.000241x** | 0.000567 |

**Frozen decision:** generic uniform-16-bank scheduling gain **fails the >=1.02x relevance threshold**, even for a perfect zero-overhead cardinality oracle. Hot-bank cap-2 is **not** a no-win regime under this generator: the frozen conditional <1.02x no-win test does not trigger; an oracle can recover cases where greedy admits only one request. The constructed cap-2 head-blocker control remains exactly no-win. Do not rewrite the frozen hypotheses.

## Compact exact boundary law

Let G be compact greedy grants, M be maximum-cardinality feasible grants, K the shared output cap, and p_K = Pr[min(K,M)>min(K,G)]. For **exactly four slots, two bank operands/request, two ports/bank, and fixed batches**, the greedy-to-oracle grant-count difference is always 0 or 1. Therefore, with E[min(K,G)]>0,

`R_K = E[min(K,M)] / E[min(K,G)] = 1 + p_K / E[min(K,G)]`.

Proof of the one-grant bound: If greedy admits >=2, an oracle cannot admit all four unless greedy would also have admitted all four, since feasibility is downward closed. If greedy admits exactly one A, every later valid request conflicts with A. When A uses two distinct banks, a conflicting request must use both ports of one of those banks, so at most two such requests can coissue. When A uses the same bank twice, every conflicting request consumes that bank, again allowing at most two. Thus M-G<=1. Output capping cannot increase this difference. If no request is valid both counts are zero.

This law is an **exact counting identity, not a novel hardware mechanism**. It predicts that any benefit requires nonzero probability of a priority-blocker event, sufficient issue demand, and an output port cap that does not erase the rescued grant. It does not predict p_K from arbitrary real workloads, and does not account for frequency/area/occupancy penalties. For equal per-request work, a *necessary but insufficient* physical condition for a real gain is `R_K * (f_candidate/f_baseline) * (occupancy_candidate/occupancy_baseline) > 1`, with additional tile, traffic and power limits.

## Independent checks and unseen draws

The separately implemented recursive dynamic-programming checker does not import the evaluator or enumerate 16 masks. It reproduced all four constructed controls, all reported aggregate arithmetic, and **256/256 exhaustive B=2 operand assignments** (52 allow an oracle improvement). Its 1,000 separately seeded held-out batches per regime gave ratios: uniform16 **1.000262x**, uniform4 **1.042912x**, hot65 **1.093048x**, hot65-cap2 **1.082346x**, samebank70 **1.001690x**, uniform16-valid60 **1.000000x**. These are new random draws from the *same synthetic families*, not cross-family real workload validation. A separate post-freeze exhaustive B=4 enumeration (65,536 operand assignments, equal-weight independent uniform banks) gives **1.046155x**, consistent with the preregistered 60,000-batch uniform4 estimate of 1.046683x; this additional check was not part of the original freeze.

## Research disposition and next hard gate

**Do not implement a general maximum-cardinality arbiter as a presumed GPU breakthrough.** On uniform 16-bank demand, even an impossible zero-area, zero-delay, zero-starvation oracle improves admitted operations by only ~0.103%. Concentrated bank conflicts can create ~4.7–10.0% *instantaneous* service headroom, but this is a conditional synthetic target and may disappear under fair scheduling, shared issue/output bandwidth, real SASS-derived bank distributions, and routing. The next candidate must freeze a bank-skew diagnostic from external workloads **before** outcomes, preserve the strong compact greedy baseline, and prove a physical/electrical legal net service benefit after area/timing/fairness costs. V317's previously failed RF-proxy area and electrical gates remain killed. No GPU IPC, SRAM-integrated tile, calibrated power, or RTX 5090 equivalence is established.
