# Bounded-bypass service sensitivity — 2026-11-19

Evidence tier: executed local Python exhaustive combinational enumeration, with GitHub source persisted. **Not** RTL simulation, synthesis, routing, finite-buffer performance, or a physically credible mechanism.

The existing V317 four-request, two-operand, two-read-ports-per-bank model was enumerated for every ordered bank assignment: 256 for B=2 and 6,561 for B=3. The same scan-order greedy comparator was used. A candidate set with bypass budget K is legal when each selected request skips no more than K unselected older requests *within that one batch*. K=0 is a strict prefix policy, **not** the existing greedy policy; K=3 is the unrestricted zero-cost oracle. No output-port cap is assumed, consistent with the previous oldest-protected checker.

| B | greedy aggregate | K=0 | K=1 | K=2 | K=3 |
|---|---:|---:|---:|---:|---:|
| 2 | 442 | 352 | 456 | 494 | 494 |
| 3 | 14391 | 11745 | 15135 | 15435 | 15435 |

At B=2, K=1 / greedy = 456/442 = 1.031674; at B=3, K=1 / greedy = 15135/14391 = 1.051699. The zero-bypass strict-prefix restriction is *worse* than scan greedy. These exact counts are bounded instantaneous grant ceilings, not realized speedups; the K=1 policy is an oracle, not implementable scheduler RTL.

**Falsification target:** any claim that simply limiting per-batch bypass proves starvation freedom is false. Repeating a permitted bypass indefinitely can still starve an old request because the rule does not track bypass history. Any positive mechanism must add stateful age/bypass accounting, bounded buffers, and fair throughput tests, then beat the strongest equal-resource compact greedy under electrically legal matched routing. The earlier area dominance (compact 21,314.6 um2; pairwise 21,324.7 um2), electrical violations, and negative hot-bank finite-FIFO result remain binding. Do not revive V287 or assert RTX-5090 equivalence.

Reproduce: `python research/v317/rtl/bounded_bypass_service_20261119.py`. The script checks exact expected counts and monotonicity. This is exploratory, not a prospectively frozen unseen-workload validation.
