# V317 integrated tile occupancy/traffic boundary: prospective falsification (2026-11-02)

## Provenance and evidence tier
Frozen before implementation at [protocol](FROZEN_INTEGRATED_ROBUST_TILE_OCCUPANCY_GATE_20261102.md), commit `acb0fe1`. Then implemented [calculator plus independent event executor](rtl/integrated_occupancy_boundary.py) at `10b001e`, [six independent tests](rtl/test_integrated_occupancy_boundary.py) at `c45ce27`, and [hosted workflow](../../.github/workflows/v317-integrated-occupancy-boundary.yml) at `5e6a492`. **Local Python tests passed 6/6. Hosted workflow outcome is pending verification.** All values below are reproduced from a 100,000-cycle seeded independent synthetic event executor, not actual GPU benchmarks.

The **only measured inputs** are five existing matched Nangate45 typical-corner routed 32-wave issue-control *area and timing-slack* pairs: physical seeds 7, 19, 37, plus density variants 0.05 and 0.35 at reused seed 7. They are **not five independent physical seeds**. All 356 sequential cells and no SRAM/datapath macros. The source implementation is not timing-legal at the original 2.000-ns target. This model gives the source an **unmeasured, zero-area-cost timing repair** and a 2.20-ns other-tile period, deliberately strengthening the source baseline. No integrated GPU clock, IPC or actual SRAM floorplan is measured.

## Robust discrete replication threshold
With hypothetical other-tile area 40,000 um2, the worst measured pairwise issue-controller area is 6,609.04 um2 and the **best** source area is 7,367.67 um2. Therefore every one of the five measured configurations has **24 source tiles versus 25 pairwise tiles** for each *integer* budget in the interval:

`1,165,226 <= B <= 1,184,191 um2`.

The lower boundary is `ceil(25*(40000+6609.04))=1165226`; the upper is `ceil(25*(40000+7367.67))-1=1184191`. Independent integer-count tests check both endpoints and immediately adjacent budgets. The width is **18,966 integer budgets**. This is a hypothetical area-reinvestment interval, **not** evidence a 25th GPU tile can be placed/routed or powered.

## Frozen positive and no-win regimes
For each physical row, `N_x=floor(B/(A_other+A_issue,x))`, `T_x=max(T_other,T_issue,x)`, and fluid throughput `Q_x=min(L,C,N_x*u_x/T_x)`. `u_x` is an assumed *effective active-and-accepted work fraction*; bank conflict, port capacity and occupancy are not separately identified. The **unconstrained** occupancy break-even is `u_pair/u_source > N_source*T_pair/(N_pair*T_source)`, which is `24/25=0.96` for the frozen common 2.20-ns clock.

| Frozen regime | Fluid prediction | Independent synthetic event-stream ratio | Interpretation |
|---|---:|---:|---|
| W1: B=1,175,000; u=.75 both; no shared cap | 1.041667x | 1.041601x | Conditional 25/24 tile win, not hardware IPC |
| N1: same; shared cap C=8 work/ns | **1.000000x** | **1.014762x** | **Frozen fluid no-win falsified under unqueued instantaneous service** |
| N2: pair u=.70, source u=.75 | 0.972222x | 0.972106x | Occupancy penalty overwhelms extra tile |
| N3: B=1,150,000; 24/24 tiles | 1.000000x | 1.000000x | No replication, no clock win |
| H1: pair u=.77, source u=.80 | 1.002604x | 1.002666x | Near the 0.96 break-even boundary |

The **N1 counterexample is retained, not retuned**. The simple `min(E[work],capacity)` fluid law silently assumes sufficient queuing/backlog or nonbursty service. In a system that drops unused per-cycle opportunities, `E[min(work,capacity)] < min(E[work],capacity)`; the pairwise extra tile reduces empty-capacity tails even though both *mean* offered rates exceed the cap. This is a **synthetic model-semantics effect**, not an architectural scheduling benefit or observed GPU behavior.

## Corrected queue-sensitive predictive boundary
For independently active tiles, `K_x ~ Binomial(N_x,u_x)`. If the shared bandwidth allows `c=C*T` work per cycle, `m=floor(c)` and `f=c-m`, the exact unqueued mean rate is

`Q_drop,x = ((1-f)*E[min(K_x,m)] + f*E[min(K_x,m+1)])/T`,

where `E[min(K,m)] = sum_{k=0}^N min(k,m)*binom(N,k)*u^k*(1-u)^(N-k)`. This equation predicts **1.014584x** for frozen N1, compared with **1.014762x** from the independent random stream. Four unseen stream configurations matched the exact clipped-binomial rate within 0.025 work/ns. With unlimited carry-over backlog and sustained mean arrivals above the cap, the **queued** event executor recovers **8.000 work/ns** for both variants (within 0.01 work/ns), restoring the frozen **1.000x** bandwidth no-win. The buffer semantics therefore decide which law applies.

The binomial assumption is itself a strong limitation: GPU occupancy and bank conflicts may be correlated across tiles, and the shared memory subsystem may have finite queues and backpressure. An actual tile trace, queue depth and bank/port model are required to transfer this boundary. The exact expression is a known probability identity, **not a claim of novel probability theory**.

## Decision and next physical gate
1. **Retain V317 as a routed integrated issue-control implementation optimization.** The measured area gap survives the five tested physical configurations. Do **not** promote the hypothetical 25/24 tile phase or synthetic traffic results into measured GPU speedup.
2. **Reject unconditional bandwidth no-win without specifying queue semantics.** The pre-registered N1 fluid prediction was falsified for instantaneous dropped opportunities, while surviving under queued work.
3. **Require legal original-source timing repair** and matched PPA before claiming a best-legal-baseline physical margin. The original misses 2 ns by only 1.48–6.60 ps across the cited density/seed settings.
4. Next integrate SRAM, actual register-file ports, bank traffic, scheduler activity and realistic queue/backpressure into a tile-level routed and workload-calibrated test; include multi-corner RC/timing and activity-driven power. If another path dominates and no usable tile replication is possible, the architecture throughput thesis is **NO-GO** despite the local controller optimization.

Reproduce locally with `python3 -m unittest discover -s research/v317/rtl -p 'test_integrated_occupancy_boundary.py' -v` and `python3 research/v317/rtl/integrated_occupancy_boundary.py`. No RTX 5090 equivalence claim. Kernellum PR #119 was not modified.
