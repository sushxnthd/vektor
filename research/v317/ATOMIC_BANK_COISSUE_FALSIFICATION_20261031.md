# V317: exact atomic bank-coissue falsification (2026-10-31)

**Decision:** the earlier per-bank *average* capacity law is an **optimistic fluid envelope**, not a valid general GPU coissue-performance predictor or a sufficient hardware no-win certificate. A matched-resource globally optimal instruction scheduler can exhibit a real difference *inside the specified synthetic model* even when the average-demand envelope predicts no difference. This does **not** establish a realizable register-read-elimination mechanism, measured GPU throughput, or novelty.

## Provenance and independent verification

The frozen protocol was committed at [afe0e77](https://github.com/sushxnthd/vektor/commit/afe0e77e8383622b9ea5b37cbe1377d842e3a125) **before** the exact solver and tests. The model was committed at [9cc21c9](https://github.com/sushxnthd/vektor/commit/9cc21c94809bc06d931c448ad313d542d55d50c3), the independent matching checker at [b2a0288](https://github.com/sushxnthd/vektor/commit/b2a0288b0b9eef808a8e22d74341b6990cdf9355), and an explicitly **exploratory, not preregistered** additional counterexample at [9bd2d43](https://github.com/sushxnthd/vektor/commit/9bd2d439bf74414ee974ccdb0fd201b37dde0517).

Six local independent unit tests passed (Python 3.13, no external packages), including 124 frozen workloads and 300 additional randomized instruction-mask workloads. The checker does **not** call the production dynamic-programming optimizer to calculate expected cycles; it constructs a labeled-instruction compatibility graph and computes exact maximum matching. Hosted GitHub CI is not yet asserted here.

## Frozen physical-resource abstraction

Three register banks A/B/C, one port per bank, two instruction issue slots, atomic same-cycle reads, zero control overhead, and unlimited reordering within a finite multiset. The strong comparator is the **globally optimal baseline schedule**, not FIFO or a weak greedy collector.

Baseline instruction masks: AB, BC, CA. The hypothetical candidate removes the B-bank read **only from AB**, leaving A, BC, CA. This assumes an unproven physical read elimination; no hardware correctness, cache hit, or compiler feasibility is asserted.

| Frozen workload (AB,BC,CA) | Average-demand predicted gain | Exact baseline cycles | Exact candidate cycles | Exact model gain |
|---|---:|---:|---:|---:|
| Predicted win (2,2,2) | 1.000x | 6 | 4 | **1.500x** |
| Predicted no-win (0,3,3) | 1.000x | 6 | 6 | **1.000x** |
| Prospective transfer (2,1,3) | 1.000x | 6 | 5 | **1.200x** |

The average-demand cycle lower bound is `max(ceil(N/2), max_b reads_b)`. It gives equal lower bounds before/after in all three cases, but those bounds are not achievable for the baseline in the win/transfer cases: all three baseline mask classes intersect pairwise, so **no two baseline instructions can coissue**, regardless of scheduling intelligence. After the hypothetical read removal, A and BC can coissue.

## Compact positive law, exact only for this synthetic mechanism

For counts a=n_AB, b=n_BC, c=n_CA and N=a+b+c:

    cycles_baseline = N
    cycles_candidate = N - min(a,b)
    G_atomic = N / [N - min(a,b)]

This is a compatibility/matching law under the frozen bank/issue abstraction. The 124-workload sweep enumerates all counts 0..4 except (0,0,0), independently verifies the law and DP optimum, and finds **50/124** workloads in which the mean-demand comparison predicts exactly 1.000x while optimal atomic scheduling improves by >1.02x. The synthetic exact gain ranges from 1.000x to 2.000x over this finite enumerated domain. The 300 randomized additional mask workloads test the optimizer, **not** unseen GPU throughput.

### Exploratory stronger counterexample: all average bank ratios slack

An additional, *post-freeze exploratory* four-class case includes three zero-RF-read instructions: counts (AB,BC,CA,none)=(2,2,2,3). Baseline total demand is 4 reads per bank over N=9 instructions, so every bank's average demand is **4/9 reads/instruction**, less than its 1/2 read/instruction capacity at issue width two. Thus every per-bank fluid ratio is 9/4 >= issue width 2, and the earlier V317 sufficient-no-win condition would fire.

Yet the independently verified optimal schedules require **6 baseline cycles versus 5 candidate cycles**, giving a 1.200x ideal model improvement. The mean lower bound is 5 cycles for both. This explicitly falsifies the previous **per-bank fluid no-win as a general certificate for atomic coissue throughput**, even with no nominally saturated bank. The old statement remains correct **only within its continuous resource-envelope model**, not as a general GPU no-win theorem.

## Adverse physical sensitivity

The same frozen (2,2,2) workload gives **1.000x** gain when issue width is reduced to one (6 versus 6 cycles), or when all three banks have two ports (3 versus 3 cycles). The model assumes atomic same-cycle port consumption, unlimited scheduling freedom, and no register-cache hits, dependencies, occupancy stalls, memory bottlenecks, electrical effects, area cost, power, or timing penalty. Any of these could eliminate the gain.

## Research decision and next hard gate

**Retain V317 only as a falsification/instrumentation branch and PR #34. Do not promote the hypothetical read-elimination candidate.** A credible architecture must prove how the B read is removed while preserving semantics, compare against a modern RF-cache-aware/compiler-aware equal-resource architecture, and use provenance-pinned dynamic physical bank masks and readiness. Then perform RTL equivalence, simulation, synthesis, matched PPA/electrical checks, wire/load sensitivity, power proxies, real workload throughput and prospective unseen predictions. No RTX 5090 equivalence claim is justified.

The previous [bank-skew report](BANK_SKEW_AGGREGATE_NO_GO_FALSIFICATION_20261031.md) and [conditional pooled-capacity report](CONDITIONAL_RF_CAPACITY_NO_GO_20261031.md) must now be interpreted as **fluid resource-envelope results only**; they cannot alone certify real coissue no-win.
