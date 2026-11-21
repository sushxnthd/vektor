# Frozen V317 RF arbiter streaming/age-transfer gate (2026-11-01)

This is a **falsification extension** of the existing exact maximum-cardinality RF-bank selector challenger on draft PR #34, not a second active architecture mechanism. The rejected register-forwarding hypothesis stays rejected. No extra ports, slots, forwarding, or bank bandwidth.

## Model frozen before evaluation

Four persistent issue slots, each with a FIFO of independent two-register-read requests. Two read ports per bank, 16 bank indices, one request/slot/cycle. At each integer cycle, each slot receives at most one request via a Bernoulli arrival with fixed probability p; a newly arrived request may issue that cycle. Each scheduler sees the same pre-generated arrival traces. Requests do not have dependencies, caches, writeback, execution latency, collector capacity or physical clock effects. This is **synthetic RF service**, not GPU IPC.

Compare three policies: (1) source-faithful fixed-slot-priority greedy arbiter; (2) existing maximum-cardinality exact selector with highest-mask tie-break; (3) independent maximum-cardinality selector with oldest-request-first tie-break, for a stronger fairness-aware control. All use identical four slots and bank-port resources; logic area and timing are **not** assumed equal. Track throughput, admitted demand, completed-request latency p50/p99/max, pending backlog, and per-slot service. Use deterministic 30,000-cycle streams, discard first 3,000 cycles for rate metrics, and report undrained backlog explicitly. Do not silently drop queued work.

## Prospective regimes and predictions

1. **Frozen predicted no-win:** each slot repeatedly addresses a private pair of banks: (0,1), (2,3), (4,5), (6,7), p=0.55 per slot, seed=317110. All requests can coissue. Predicted throughput ratio exact/priority = 1.000 and identical latency.
2. **Frozen predicted possible win:** each request independently chooses both banks uniformly from {0,1,2,3}, p=0.48 per slot, seed=317111. Hypothesis: myopic exact selector improves steady-state completed work by at least 1% versus fixed priority; this is a **testable prediction**, not an observed result. If it fails, record the failure.
3. **Frozen unseen transfer:** p=0.52 per slot, seed=317113; with probability 0.70 each request chooses both banks uniformly from {0,1,2,3}, otherwise both from {4,5,6,7}. Do not tune any policy on this transfer.
4. **Adversarial fairness control:** four slots perpetually offer (0,1), with all slots backlogged. Compare age/tie-break and per-slot service. This is a synthetic worst case, not a measured GPU traffic pattern.

## Analytical two-bank theorem to test

For a finite batch containing a requests of type (0,0), b of type (1,1), and c of type (0,1)/(1,0), the optimal drain time is max(a,b)+ceil(c/2). Every cycle can pair one (0,0) with one (1,1), or two mixed requests, but cannot mix a same-bank request with a mixed request. Test source-priority and maximum-cardinality policies on randomized longer finite batches and compare with this independent closed-form bound. Scope: finite batches with no arrivals or dependencies, not general streaming.

## Kill and reporting rules

If the exact selector's predicted >=1% gain fails, or age fairness worsens severely, retain it only as a rejected challenger. Do not claim a hardware speedup regardless of synthetic success until matched standard-cell area/timing, collector occupancy, realistic dynamic bank traces and wire/load sensitivity are established. Preserve all failed predictions and avoid rebranding grant-count differences as throughput. Do not modify Kernellum during this primary test.
