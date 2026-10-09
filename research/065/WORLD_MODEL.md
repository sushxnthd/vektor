# Vektor-065 — Discovery Protocol V2 world model

Date: 2026-10-09. **All throughput numbers are synthetic software-model results.** The small RTL module passed directed Icarus Verilog simulation and Yosys generic synthesis on GitHub Actions run 37965611241 (2026-10-09). Physical PPA, full GPU benchmarks, and chip equivalence remain unverified.

## Mechanism, preregistration, outcomes, residuals

**DISCRIMINATION / CAPABILITY-BUILDING:** Replace the Vektor-064 ideal strong-ACK oracle with an explicit counted-replica contract. Every physical copy increments a per-slot outstanding count at the last possible replication point. Every terminal delivery/drop decrements it. A close event prohibits further copies. At least one copy must be delivered. Strong ACK requires close + delivered + zero outstanding. ACK itself must not replay or overtake the fence.

- **H1 — KNOWN within model:** Counted quiescence prevents false credit after tag reuse. Prediction zero; outcome **zero** in 144 structured strong-policy runs and 18 exploratory runs, 800 transactions each. Residual zero. Independent list-model comparisons 72/72 exact. Alternative explanation: safety is built into complete replica accounting, which may not hold in a real NoC.
- **H2 — FALSIFIED weak first-delivery retirement:** Prediction delayed copies can corrupt reused tags. Outcome 96/144 paired configurations with false credits, 41,123 total. Weak ACK is a deliberately unsafe comparator, not a production performance baseline.
- **H3 — KNOWN conditional cost:** Strong retirement waits for the last copy; predicted lower throughput in long-tail regimes. Median strong/weak ratio **0.91877**, minimum **0.09258**, maximum 1.0. Strong safety costs tag occupancy; this is not GPU IPC.
- **H4 — UNRESOLVED liveness:** If all packets are dropped, closed=1, outstanding=0, delivered=0 blocks successful ACK forever. Recovery needs bounded retry, abort, and reset fencing.
- **H5 — FALSIFIED unconditional safety:** An untracked duplicate created after the producer closes can arrive after reuse. The counter only proves safety if all future replicas are registered at the last replication point and ACK is reliable/non-replaying.
- **H6 — BELIEVED heuristic, partially supported:** Preregistered median relative error <10% for mean-occupancy approximation `min(1, tags/(2.5 + dup_p*(gap+1)/2))`. Outcome 216 held-out configurations, median **2.30%**, maximum **17.76%**; 26/216 exceed 10%. Residuals cluster near stochastic saturation. Not a novel queueing law.
- **H7 — ANOMALOUS utilization cliff:** Preregistered equal-mean service-time variance test: fixed six-cycle service versus shuffled half two-cycle/half ten-cycle service. At six tags, 12.73–12.76% relative throughput loss over three seeds; at twelve tags, 0.03–0.04%. Mean occupancy alone misses burst-induced tag exhaustion. This is a toy queueing result, not new GPU hardware.

## KNOWN

- A first-delivery response does not certify fabric quiescence under delayed duplicates.
- The per-slot tracker is synthesizable-style RTL and implements a **local** contract only; it does not prove transport-side event honesty.
- Exhaustive four-copy enumeration: 1,698 prefix states, 409 eligible strong-ACK states, 880 unsafe early weak-ACK states, 33 no-delivery permutations.

## BELIEVED

- Counted quiescence can work with bounded replication ownership and terminal accounting; tag-pool sizing should include service-time variance/tails.

## CONFLICTING

- Strict safety improves while long replay tails consume tags and lower throughput. More tags increase storage, control logic and possible timing cost. Neither actual transport PPA nor real workload latency distribution is known.

## FALSIFIED

- First response suffices for safe tag reuse under replay.
- Mean service lifetime reliably predicts throughput near capacity: 26/216 cases exceed 10% relative prediction error.

## ANOMALOUS

- Strong/weak modeled throughput ratio falls to 0.09258 in the smallest-tag/longest-gap tested regime.
- Exactly equal mean service times yield a >12% rate difference at six tags because of variance.

## UNTESTED

- Unbounded formal proof; ACK loss/replay, reset, cancellation, retransmission, real NoC replication ownership, multi-tile scaling, compiler workloads, physical PPA, GPU performance.

## VERIFIED RTL AND SYNTHESIS (component only)

- GitHub Actions: https://github.com/sushxnthd/vektor/actions/runs/37965611241 — model, independent replication, capacity tests, directed RTL testbench and generic Yosys synthesis all **PASS** at branch commit 70c4890bb7f3bf6e17c58c34886e540d547a8618.
- Yosys default-parameter tracker: **166 generic cells**, including 28 flip-flop-type cells. Generic gate count is **not** mapped physical area, timing, frequency or power. No formal proof is claimed.
- RTL checks are directed, not exhaustive: queue/fabric integration, ACK loss, reset fencing and replay remain unverified.

## Adversarial roles and prior art

Explorer: counted replica quiescence. Skeptic: hidden retransmit engine, replayed ACK, reset while packets remain. Experimentalist: equal-budget weak/strong paired synthetic traces, exhaustive four-copy orders, equal-mean variance probe. Analyst: retain large throughput regressions. Anomaly Hunter: stochastic capacity cliff and law residuals. Prior-Art Auditor: termination detection, flow control, replay windows, credit conservation and queueing variance are established; **no novelty claim**. Replicator: independently coded list model, 72 exact comparisons. Theorist: no post-ACK copies plus unique active ownership is sufficient only under a complete event stream.

## Single next decisive action

Verify RTL and generic synthesis in free CI, then implement a **two-sided** packet retransmission/ACK producer that guarantees counted terminal events under replay, loss, reset and backpressure. Prove conservation and replay safety before optimizing batch scheduling. No personal spending.
