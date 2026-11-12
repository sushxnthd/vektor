# V317 streaming RF-bank selector: prospective win falsified (2026-11-01)

**Decision: reject the exact maximum-cardinality RF selector as a throughput claim in the frozen non-overloaded regime.** Retain the code as a negative-control instrument on existing draft PR #34. This does not revive the previously rejected V317 register-forwarding mechanism.

## Preregistration and model

The prospective protocol was committed first at [a553905](https://github.com/sushxnthd/vektor/commit/a553905b3d692e36459fd8a3b6c75b39fb3c6690), before implementing or evaluating the streaming simulator. Four persistent issue slots each hold a FIFO of independent two-read requests. There are two reads per bank per cycle, no extra ports or slots, and identical pregenerated arrival traces for each policy. Each run covers 30,000 cycles with a 3,000-cycle warmup. There are no dependencies, collector limits, execution latency, register-file pipeline, memory stalls, physical clock effects or silicon timing. These are **synthetic bank-service cycles, not GPU IPC**.

Policies: (1) source-faithful fixed-slot-priority greedy; (2) exact maximum-cardinality with highest-mask tie-break, matching the RTL challenger; (3) exact maximum-cardinality with oldest-head-age tie-break. Age-aware policy requires additional comparison logic and is NOT established to be equal area or timing.

## Prospective results

| Frozen regime | Priority completed after warmup | Exact completed | Exact/priority | Priority p99 wait | Exact p99 wait | Age-aware p99 wait |
|---|---:|---:|---:|---:|---:|---:|
| Private bank pairs, p=.55 (no-win) | 59,068 | 59,068 | **1.000000x** | 1 | 1 | 1 |
| Uniform four-bank, p=.48 (predicted >=1% win) | 51,910 | 51,900 | **0.999807x** | 18 | 16 | 4 |
| Unseen mixed-bank transfer, p=.52 | 56,048 | 56,049 | **1.000018x** | 6 | 6 | 3 |

**Frozen prediction failed.** The exact selector completed 10 fewer requests in the 27,000 measured cycles in the predicted-win regime, not >=1% more. Its final backlog was one request, the same as fixed priority. The unseen transfer differed by one completion, not a meaningful advantage. The private-bank no-win prediction held exactly.

The age-aware tie-break reduces waiting tails without increasing service in these stable-load regimes. That does not make it a novel architecture mechanism.

## Strong simple controls and overload sensitivity (explicitly posthoc)

After inspecting the frozen result, two stronger controls were added: oldest-head-first greedy and cyclic rotating priority. These were **not preregistered as positive predictions**. The four-bank arrival model was also stressed at higher offered load. Selected results:

| p/slot | Policy | Completed/cycle after warmup | Final backlog | p99 latency (cycles) |
|---|---|---:|---:|---:|
| .48 | Priority | 1.922593 | 1 | 18 |
| .48 | Exact | 1.922222 | 1 | 16 |
| .48 | Age-aware exact | 1.922222 | 1 | 4 |
| .48 | Rotating priority | 1.922222 | 1 | 6 |
| .60 | Priority | 2.262704 | 4,521 | 7,102 |
| .60 | Exact | 2.310741 | 3,002 | 4,720 |
| .60 | Age-aware exact | 2.412333 | 6 | 8 |
| .60 | Rotating priority | 2.412296 | 7 | 30 |
| .75 | Priority | 2.426556 | 17,337 | 14,615 |
| .75 | Exact | 2.538148 | 14,029 | 12,661 |
| .75 | Age-aware exact | 2.656185 | 10,460 | 3,473 |
| .75 | Rotating priority | 2.540259 | 13,873 | 4,636 |
| .90 | Priority | 2.502630 | 32,801 | 18,274 |
| .90 | Exact | 2.619778 | 29,217 | 16,142 |
| .90 | Age-aware exact | 2.652333 | 28,288 | 7,801 |
| .90 | Rotating priority | 2.540148 | 31,689 | 8,746 |

At p=.60, the age-aware exact policy appears to avoid the runaway queue observed for the fixed and myopic exact policies. **However, the much simpler rotating-priority control achieves nearly identical completed-work rate and also keeps backlog bounded in this finite run.** Thus the result does not identify a novel maximum-cardinality mechanism. At p=.75 and p=.90 every policy has large growing backlog; throughput comparisons there do not establish a stable service regime. All p=.60/.75/.90 numbers are exploratory, not prospective holdouts.

A persistent four-slot (0,1) adversary shows deterministic starvation: fixed priority serves slots [1000,1000,0,0], highest-mask exact serves [0,0,1000,1000], while age-aware exact serves [500,500,500,500] over 1,000 cycles. Total issued requests are 2,000 for all three. A higher single-cycle grant count does not establish fairness.

## Compact negative boundary law

For a **finite two-bank batch** with a requests of (0,0), b of (1,1), and c of mixed (0,1)/(1,0), all requests requiring two physical reads and each bank having two ports, the exact minimum drain cycles are

\[
T^*(a,b,c)=\max(a,b)+\left\lceil c/2\right\rceil.
\]

Proof: A same-bank request consumes both ports of that bank and may coissue only with an opposite-bank same-bank request. A mixed request uses one port of each bank and may coissue only with another mixed request. The two groups therefore occupy disjoint cycles. Pairing opposite-bank requests gives max(a,b) cycles, and pairing mixed requests gives ceil(c/2). A work-conserving fixed-priority scheduler greedily takes these pairs and attains this lower bound, independent of initial request order. The claim is only for finite batches without arrivals or dependencies, **not** arbitrary four-bank or streaming workloads.

An independent long-batch checker verified 6,400 randomly generated two-bank batches of lengths 1..64 against the closed form, with zero discrepancies. The regression also enumerates all 4,096 two-bank four-slot masks/pair encodings to check physical port legality and exact-cardinality dominance.

## Evidence and next gate

Reproduction from repository root:

\`\`\`bash
python -m unittest research.v317.test_rf_streaming_age_falsification -v
python -m research.v317.rf_streaming_age_falsification > streaming.json
python -m research.v317.rf_streaming_strong_controls > strong_controls.json
\`\`\`

The initial five local tests passed. No new RTL synthesis result, standard-cell timing, electrical signoff, routed wire/load result or real GPU workload result is claimed in this report. The existing exact-selection RTL physicality workflow was still queued at last inspection. The highest-mask exact selector is rejected as a practical speedup based on the frozen workload evidence; additional synthesis cost can only weaken it. A physically credible mechanism must first beat rotating-priority and strong age-aware controls on representative dynamic traces and then close equal-resource physical timing.

Kernellum PR #119 was not modified. No RTX 5090 equivalence claim.
