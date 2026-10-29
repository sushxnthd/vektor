# V302 prospective protocol (frozen before holdout execution)

Date: 2026-10-29. Single active candidate: phase-bounded frequency-biased combining of reduction-only integer atomic adds. This is a research hypothesis, not a novel GPU invention or a validated speedup.

## Legal semantic scope
Only unsigned modular integer atomic additions whose return values are dead, whose addresses are not read or observed by any participant until a kernel-wide completion boundary, and whose visibility/ordering contract permits deferred updates. No general atomic, acquire/release, CAS, floating-point, external observer, or interleaved read may be combined. Flush all pending keys before the completion boundary. An explicit counterexample with a concurrent read is a mandatory negative test.

## Mechanism and equal-state controls
A 4-entry associative table accumulates key and sum mod 2^32 with a bounded 8-cycle residency. V302 uses saturating 2-bit hit frequency to choose the lowest-frequency eviction victim, breaking ties by age. The equal-resource control uses four identical entries and 2-bit replacement metadata but LRU selection. Both receive the same warp-local combined input and have one downstream atomic port. Also compare a four-entry non-combining FIFO and warp-local aggregation alone. Never compare against raw per-lane atomics alone. Do not count a logical update complete until its combined transaction is issued; finite input buffering/backpressure is required.

## Frozen scenarios, independent seeds and metrics
Evaluate eight previously unrun seeds (20261030..20261037), 10,000 offered cycles each, four warps x four lanes per offered cycle, finite 32-request input buffer and one downstream atomic transaction per cycle. Offered probabilities and key distributions:
- H1 predicted win: offered 0.8 per warp; five keys with weights [0.55, 0.15, 0.12, 0.10, 0.08].
- H2 predicted no-win: offered 0.35; 256 uniform keys.
- H3 phase reversal: offered 0.75; five keys with H1 weights, permuted to disjoint key sets every 128 cycles.
- H4 low load: offered 0.05; 32 uniform keys.
- H5 highly concentrated: offered 0.8; two keys with [0.8, 0.2].
Record accepted logical updates per offered cycle, serviced transactions, input stalls, final drain cycles, queue occupancy and per-key conservation. Report mean and seed spread. Drain is included in end-to-end throughput. Separate offered traffic from accepted traffic.

## Survival / kill criteria
- H1 V302 end-to-end logical throughput >=1.10x FIFO and >=1.05x LRU; the stronger LRU comparator is binding.
- H2 V302 >=0.98x LRU; H3 >=0.95x LRU; H4 >=0.98x LRU.
- All conservation/ordering-scope tests pass; no unbounded buffer or hidden throughput benefit from dropping requests.
- No RTL investment if H1 strong-control threshold fails or H3 regressions exceed threshold.
- If the novelty audit shows a prior equivalent, constrain the claim to an independently measured conditional boundary or kill it.
- Do not retune against these holdouts. Any revised mechanism needs a new version and new holdouts.

## Prior art / novelty risk
Warp-aggregated atomics are established and automatically optimized in some NVIDIA compiler cases: https://developer.nvidia.com/blog/cuda-pro-tip-optimized-filtering-warp-aggregated-atomics/ .
GPU atomic buffering is established: https://engineering.purdue.edu/tgrogers/publication/chou-micro-2020/ .
Reduction collision elimination is established: https://doi.org/10.1145/2602988.2602993 .
The use of LFU/LRU replacement is classical. No broad novelty is asserted.

## Evidence tier
This protocol is pre-evaluation only. No simulator results, RTL, synthesis, electrical validation, GPU IPC, area/power or RTX 5090 equivalence are claimed.
