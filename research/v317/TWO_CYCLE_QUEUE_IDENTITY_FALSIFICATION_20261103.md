# V317 K=2 two-cycle queue-identity falsification (2026-11-03)

**Evidence tier:** exact small-bank enumeration and seeded synthetic finite-batch scheduling. NOT sustained GPU IPC, actual wavefront workload, dynamic RF-bank demand, routed area, electrical signoff or RTX 5090 evidence. Frozen protocol: FROZEN_TWO_CYCLE_QUEUE_IDENTITY_20261103.md, committed at 75015e3 before the prospective B=4 evaluation.

## Why the instantaneous no-win law is not a queue-level no-win law

Earlier V317 work correctly proved that, with an all-valid oldest request, K<=2 and work-conserving admission, compact greedy and degree-head always grant the same number of requests in one scheduling snapshot. They need not grant the same identities. Different residual queues can have different bank conflicts in the next cycle.

Directed three-bank witness (two read ports per bank, two reads per request, four initial requests, no arrivals on cycle 2):

| Request slot | Operand bank pair |
|---|---|
| 0 (oldest) | (0,0) |
| 1 | (0,1) |
| 2 | (1,1) |
| 3 | (2,2) |

Cycle 1: compact greedy selects slots 0 and 2, degree-head selects slots 0 and 3. Both grant two. Cycle 2: compact's residual requests (0,1) and (2,2) can both issue, while degree's residual (0,1) and (1,1) conflict at bank 1. **Two-cycle totals are 4 versus 3.** Neither scheduler drops work; degree leaves one request pending beyond the frozen deadline.

## Exact two-cycle residual-conflict identity

For any all-valid four-request batch, K=2 and two-port banks, both schedulers either issue the same single head request or each issue two requests. In the latter case, define I_p=1 if policy p's two residual requests cannot coissue on cycle 2, else 0. If both first-cycle masks are the same, I_g=I_d. For every batch:

    C_degree(2) - C_greedy(2) = I_greedy - I_degree.

For a population of batches the aggregate ratio is

    R = 1 + [Pr(I_greedy=1) - Pr(I_degree=1)] / E[C_greedy(2)].

This is an exact accounting/predictive identity given pre-service residual compatibility, not a validated independent workload-distribution model or a novel architecture mechanism. It exposes why snapshot cardinality equality cannot be extrapolated to temporal queue performance.

## Retrospective exhaustive B=3

All 3^8 = **6,561** ordered four-request operand vectors, all slots valid:

| Two-cycle measurement | Compact greedy | Degree-head |
|---|---:|---:|
| Completed requests | 23,496 | 23,292 |
| Residual pair conflicts after first cycle | 2,226 | 2,430 |

Degree wins 288 batches, loses 492, ties 5,781. Net deficit 204 completions. This retrospective enumeration informed the test design and is not an unseen holdout.

## Prospective B=4 holdout (frozen before evaluation)

Three independently seeded uniform four-bank populations, 40,000 batches per seed, all four requests valid. Each policy gets exactly two cycles with no second-cycle arrivals, the same ports and K=2. Frozen prediction: first-cycle grant counts identical for all batches; degree two-cycle aggregate ratio <=0.995.

| Seed | Compact greedy | Degree-head | Degree/greedy |
|---|---:|---:|---:|
| 503 | 150,122 | 148,417 | 0.98864x |
| 907 | 150,089 | 148,553 | 0.98977x |
| 1201 | 150,035 | 148,363 | 0.98886x |
| **Total** | **450,246** | **445,333** | **0.989088x** |

**Frozen predictions passed.** Degree completes 4,913 fewer requests (1.0912%) by the two-cycle deadline despite equal first-cycle grant cardinality in all 120,000 batches. Degree wins 3,875 batches, loses 8,788, and ties 107,337. Its residual pairs conflict in 31,530 cases versus 26,617 for compact greedy, exactly accounting for the 4,913 difference.

## Exploratory bank-count sensitivity (not preregistered)

One post-hoc seed (345), 20,000 batches per bank count, same two-cycle experiment:

| Banks | Greedy | Degree | Ratio |
|---|---:|---:|---:|
| 2 | 63,317 | 63,317 | 1.00000x |
| 5 | 76,813 | 75,911 | 0.98826x |
| 8 | 78,693 | 77,953 | 0.99060x |
| 16 | 79,684 | 79,327 | 0.99552x |

These sensitivities were selected after seeing the primary holdout; they are descriptive only.

## Independent reproduction and decision

The evaluator (rtl/two_cycle_queue_identity.py) and separately implemented checker (rtl/audit_two_cycle_queue_identity.py) passed locally on 126,561 independently replayed vectors, including all 6,561 exhaustive B=3 vectors and 120,000 frozen B=4 vectors. Both checked the per-batch exact residual-conflict identity. Reproduce:

    python3 research/v317/rtl/two_cycle_queue_identity.py > /tmp/v317-two-cycle.json
    python3 research/v317/rtl/audit_two_cycle_queue_identity.py /tmp/v317-two-cycle.json

**Decision:** Preserve the exact K<=2 snapshot theorem but reject its extension to identical finite-horizon queue performance. Degree-head is worse than compact greedy in the frozen two-cycle B=4 population, and already costs 734 versus 260 generic synthesis cells. Do not promote degree-head or V317 as a positive physical GPU mechanism. This result neither resolves earlier V317 RF-proxy electrical/area failures nor establishes a sustained streaming throughput disadvantage. The next useful physical step requires independently obtained bank-demand traces and a compact controller with measurable legal timing, area and tile-level value.
