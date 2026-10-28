# V296 exact bank-admission equivalence: a falsification (2026-10-28)

**Decision:** V296's pairwise-count admission arbiter is combinationally **admission-equivalent** to the strongest V295 serial once/twice one-hot arbiter under the frozen four-request, 16-bank, two-read-port-per-bank contract. It cannot claim a higher wave-issue count at equal clock, occupancy, latency and request trace. Physical area, timing and energy remain separate, unproven hypotheses. V287 remains retired.

## Sources, scope and method

Read `research/v296/v296_issue_core.sv` (`v296_pairwise_arbiter`) and `research/v295/v295_issue_core.sv` (V295 serial one-hot). Both use the same warp scheduler and acceptance feedback. Independently model V296 as counts of prior granted operands and V295 as two one-hot masks (`once` and `twice`). This is a source-derived combinational reference-model experiment, **not** RTL formal equivalence or a routed implementation.

Eight operand-bank labels have Bell(8) = **4,140** canonical equality partitions. Evaluate all 16 request-valid masks: **66,240** cases. A partition with k distinct bank labels represents (16)_k concrete assignments, and all weights sum exactly to 16^8 = **4,294,967,296**. There were **zero grant-mask disagreements** and **zero violations of the two-port constraint**. A separate 100,000-case explicit-bank random test also passed. Equal acceptance masks feed the same scheduler, so equal initial scheduler state and identical input traces yield equal acceptance traces by induction.

## Exact predictive law, iid-uniform model only

For independent uniform bank labels and independent Bernoulli(q) request readiness, the expected accepted waves/cycle for **both** implementations is exactly

`E[G(q)] = (17179869184 q - 383778816 q² - 409419776 q³ + 31800464 q⁴) / 4294967296`.

This polynomial is an exact weighted enumeration result, not a fitted GPU benchmark. It does not account for temporal bank correlation, closed-loop occupancy, latency or a bandwidth bottleneck.

| q | Both controllers: expected waves/cycle | Optimal feasible subset oracle | Oracle headroom |
|---|---:|---:|---:|
| 0.25 | 0.992954745 | 0.993011079 | 0.005673% |
| 0.50 | 1.966208207 | 1.966666089 | 0.023288% |
| 0.75 | 2.911864827 | 2.913434520 | 0.053907% |
| 1.00 | 3.822723184 | 3.826501634 | 0.098842% |

The optimal-subset oracle uses the **same two-port constraints** but is not timing/area-matched RTL. At q=1 the greedy controllers lose one wave to optimal on 0.377845% of iid assignments. An adversarial example: bank labels `[0,0, 0,0, 0,1, 0,1]`, valid mask `1101`; greedy admits slot 0, but slots 2 and 3 fit together. This is a failure of both existing arbiters, not a V296 win.

The law was checked at **unseen q values** using independent seeded 100,000-cycle explicit-bank Monte Carlo: q=0.33 predicted 1.30693129, observed 1.30606 (error 0.00087129); q=0.87 predicted 3.35383654, observed 3.35404 (error 0.00020346). This is synthetic holdout validation only, not unseen real workloads.

## Physical and research consequence

The necessary equal-latency throughput ratio is `R296/R295 = (f296/f295) × (T296/T295)`. For identical clock and workload admission state, `T296/T295 = 1`. Differences in physically achievable clock, area packing, energy, or occupancy could still matter, but require **two feasible matched routed contestants** and an independently validated full workload model.

Existing D4 V296 extracted-RC setup slack +66.661 ps, D8 +59.643 ps; the D4 serial comparator fails setup and hold, and D8 serial timed out (exit 124). The candidate's setup guard headroom is just 16.661 ps / 9.643 ps. The 30,000 µm² tile ceiling does not establish extra completed slices. No GPU throughput, power, SRAM macro, or RTX-5090-equivalence claim follows.

**Falsify the algorithmic-throughput hypothesis now.** Keep V296 as the sole provisional *physical* mechanism only while testing whether a matched serial control can complete and whether a real physically constrained area/clock/energy advantage survives. Diagnose D8 serial route timeout from its original artifact log, preserve negative results, and do not alter Kernellum PR #119.

Reproduce: `python3 research/v296/v296_partition_equivalence.py` (Python standard library). Outputs exact weighted results, independent oracle, adversarial witness and unseen-q simulation checks.
