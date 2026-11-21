# V317 prospective bank-coissue hypergraph falsification protocol (2026-10-31)

**Status: frozen before implementing the exact scheduling solver or opening computed outcomes.** This is a synthetic capacity-law stress test, not an architecture promotion, a measured NVIDIA result, or a demonstration that any read can be removed physically. Retain the existing V317 branch and draft PR #34.

## Hypothesis

Even a **per-bank mean-demand** throughput envelope can be too optimistic when one instruction must consume multiple bank ports in the same cycle. Equal-resource optimal instruction pairing is a graph/hypergraph packing problem, not just the minimum of average bank-capacity ratios. Test whether a hypothetical read elimination yields an actual optimal coissue gain despite the mean-demand envelope predicting none.

## Frozen hardware abstraction and equal-resource comparator

- Three independent register banks A/B/C, **one read per bank per cycle**; issue width **two instructions per cycle**; unlimited reorder freedom within a finite instruction multiset, zero control/clock overhead, no latency or cache effects.
- Every instruction consumes its specified bank-mask atomically in one cycle. All three baseline instruction classes have two reads: AB=0b011, BC=0b110, CA=0b101.
- The candidate hypothetically removes the B-bank read from **AB only**, changing its mask to A=0b001. All other instructions, physical bank ports, issue slots, ALUs, and scheduling freedom remain identical. This is an optimistic resource-envelope counterfactual; no implemented operand reuse, compiler transformation, or correctness proof is asserted.
- **Strong baseline:** globally optimal exact packing over all possible schedules, not head-of-line or greedy scheduling. Verify the exact optimizer independently using a separate brute-force partition enumerator.
- **Mean-demand comparator:** lower-bound cycles as max(ceil(N/2), max_b total_reads_b), and predicted gain as baseline lower-bound cycles / candidate lower-bound cycles. This is an optimistic fluid/aggregate bound and must not be described as a throughput guarantee.

## Frozen regimes and predicted outcomes

- **Predicted win:** 2 AB, 2 BC, 2 CA. Mean-demand cycle lower bounds are 4 before and after; mean-demand gain **1.000x**, but optimal packing takes 6 baseline cycles and 4 candidate cycles, predicting **1.500x**.
- **Predicted no-win:** 0 AB, 3 BC, 3 CA. No candidate-affected instructions; exact optimal cycles 6/6 and gain **1.000x**.
- **Prospective transfer:** 2 AB, 1 BC, 3 CA. Exact optimal cycles 6/5, predicting **1.200x**; do not use this regime to adjust the solver or law.
- **Frozen sensitivity:** all triples of counts 0..4, excluding the all-zero case, 124 workloads. Verify optimal cycles and the upper-envelope shortfall, and identify all cases in which the mean-demand gain is 1 but actual candidate gain exceeds 1.02. The sweep is synthetic and known before evaluation, not a real-workload holdout.

## Falsification and next gate

Kill/revise if any independent enumerator disagrees with the dynamic-programming solver, if any issue or bank capacity is violated, if the predicted exact cases fail, or if the equal-resource optimal baseline erases the claimed synthetic difference. This result, if confirmed, falsifies **per-bank average capacity as a sufficient coissue-performance predictor** under atomic multi-bank instructions. It does not establish a novel GPU architecture, dynamic physical RF demand, a hardware throughput gain, PPA, or RTX 5090 equivalence.

For real architectural promotion, obtain independently grounded dynamic instruction bank masks/cache behavior and demonstrate a physically realizable demand-reduction mechanism versus a modern equal-resource compiler/RF-cache-aware baseline, then RTL and matched PPA/electrical checks.
