# Frozen finite-queue drain challenge to the RF arbiter issue-count gap (2026-11-01)

Status: preregistered before implementing the finite-queue checker or inspecting its results. Same V317 draft PR #34 and research branch; no second promoted mechanism. The prior exact-selection RTL remains an **uncosted challenger**.

## Hypothesis

A single-cycle exact/greedy grant ratio can overstate completed-work throughput because the greedy scheduler can issue deferred requests on the next cycle. Predict the frozen 3-request witness [(0,0),(0,1),(0,1)] has a 2.0x first-cycle grant-count ratio but **equal two-cycle full-drain makespan**. Predict [(0,0),(1,1)] has equal one-cycle makespan. Neither prediction is to be changed after evaluation.

## Predeclared experiment

1. Hold a finite batch of at most four independent instructions, each with two bank reads, 16 possible banks, and two physical ports per bank. No new arrivals, no memory latency, no dependencies, no replay, no collector pressure, and no warp fairness state.
2. At each cycle remove only requests granted by either the exact same fixed-priority RTL translation or the exact maximum-cardinality oracle. Continue until the batch is drained. Preserve original slot identities and priority across cycles.
3. Exhaust all 4,096 two-bank valid-mask/operand configurations. Report cases in which exact improves, ties or worsens drain cycles; report aggregate cycles over nonempty batches, and preserve any negative findings.
4. Perform the previously fixed-seed 10,000-case four-bank transfer without tuning; compare to the original per-decision 16,606/16,428 ratio.
5. Independently compute an optimal **multi-cycle** partition by enumerating legal per-cycle subsets and minimizing total completion cycles; this stronger same-resource baseline prevents attributing an avoidable scheduling artifact to a new mechanism.
6. All claims remain restricted to synthetic finite-batch issue/drain cycles. Do not equate them to real GPU IPC, energy, latency tails, or routed timing.

## Kill boundary

If the apparent first-cycle gain disappears in full-drain comparisons, reject it as a throughput claim even if exact RTL simulates correctly. If any benefit survives, it remains a scheduling upper bound pending matched area/frequency, realistic queue arrivals, fairness, occupancy, register-file bandwidth, and tile-level evaluation. Do not revive the already rejected V317 forwarding mechanism.
