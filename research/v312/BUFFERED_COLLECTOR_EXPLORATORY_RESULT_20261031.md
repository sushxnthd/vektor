# V312 exploratory buffered-collector stress test (2026-10-31)

**Evidence tier: local Python execution, not yet independently hosted or GPU cycle-accurate.** The four regimes below were examined before this report and must NOT be represented as prospective unseen holdouts. Exact source is `buffered_collector_strong_control.py`; [hosted audit workflow](../../.github/workflows/v312-buffered-collector.yml) was queued when this report was written.

Model: four independent issue partitions, FIFO queue depth two, one issue/partition/cycle, sixteen banks, two reads per instruction and two ports/bank. A shared offered stream arrives with probability 0.95 per partition/cycle; 2,000 warmup and 30,000 measured cycles. The head-only policy sees one request; V312 may bypass a conflicting head to the second ready request; an independent one-hot buffered collector scans the same two ready requests. Equal resources and equal information **in this synthetic service model**.

| Synthetic workload | Head-only issues/cycle | V312 issues/cycle | V312/head | V312/strong buffered collector |
|---|---:|---:|---:|---:|
| 95% bank hotspot | 2.105933 | 2.105800 | 0.999937x | **1.000000x** |
| 70% hotspot / diversified | 2.798567 | 2.826200 | 1.009874x | **1.000000x** |
| Disjoint banks | 3.801100 | 3.801100 | 1.000000x | **1.000000x** |
| All-hot | 2.000000 | 2.000000 | 1.000000x | **1.000000x** |

For every simulated cycle the queue contents and cumulative statistics of V312 and the independent one-hot collector match exactly; bank-port capacity is audited using a separate numeric counter. This is an *implementation/policy equivalence under matched information*, not evidence that any particular production GPU uses this exact collector. The ideal one-opportunity hotspot admission ratio of 1.95x from the earlier screen does not transfer to this persistent-queue hotspot stream; backup requests are correlated with the head and queue occupancy matters.

**Interpretation:** the earlier 1.95x figure was a narrow admission result against a weak head-only comparator, not a sustained GPU throughput result. Even where fallback helps head-only, the same-information buffered collector reproduces it exactly. Combined with the independent matched Nangate45 area/timing no-go, this reinforces retirement of V312 rather than attempting a costly full tile implementation.

**Limitations:** no real register traces, instruction dependency graph, operand collector timing, scoreboard, warp fairness, energy, power or physical comparator area. A prospective new workload sweep would be required for a transfer claim. The physically frozen V312 kill remains decisive regardless of this exploratory test.
