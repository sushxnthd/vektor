# V309: source-pinned standard-cell area and prospective IID law results (2026-10-31)

**Independently hosted result: PASS at both frozen gates.** [GitHub Actions run #41157943917](https://github.com/sushxnthd/vektor/actions/runs/41157943917), source commit `e39c708bd480e4ad4969994d300c5a88145b5fc5`, completed every step successfully. The run's artifact preserves Icarus, Yosys, mapped JSON, pinned Liberty, model predictions, raw holdout histograms and independent audit output. **This is standard-cell synthesis, not placed-and-routed electrical timing or a measured GPU gain.**

## A. Stronger baseline and mapped standard-cell comparison

The previously preregistered 109,076-case independent RTL oracle/equivalence test passed. The same original greedy, compact same-policy greedy and factored exact-max controller were mapped to the same **NangateOpenCellLibrary typical corner**, source Git blob `90e4afb274cfc6514c587c434c77903d554117d1` (verified by `git hash-object`), SHA-256 `8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`.

| Controller | Policy | Generic cells | Generic logic edges | Nangate45 mapped cells | Nangate45 area (library units) | Maximum mapped-cell input fanout |
|---|---|---:|---:|---:|---:|---:|
| Original greedy | Priority greedy | 1,321 | 49 | 747 | 798.798 | 66 |
| **Compact greedy** | **Exactly same priority greedy** | **260** | **16** | **178** | **251.370** | **7** |
| Factored exact-max | Maximum-cardinality | 331 | 18 | 224 | 303.772 | 9 |

The **correct strongest-baseline mapped area ratio** is `303.772 / 251.370 = 1.208465608x`, a **20.85% mapped area premium**, not an area saving. The preregistered 2.0x compact-baseline mapped-area ceiling **passes**. This comparison uses the same 36 input bits, four grant bits, 16 banks, two read ports/bank, and no extra pipeline stage.

Fanout is a load proxy only. Neither `ltp` generic logic edges nor Nangate45 mapped cell area establish critical-path delay, capacitance, slew, setup/hold, extracted wire parasitics, power, or physical signoff. In particular, the candidate has **18 versus 16 generic path edges** and **9 versus 7 maximum mapped-cell fanout**; a timing disadvantage remains plausible.

## B. Prospective positive-law predictions on unseen synthetic regimes

The [pre-outcome frozen protocol](BANK_EQUALITY_MOMENT_LAW_PREREG_20261031.md) derived `p(q)` and `g(q)` analytically from the eight operand-bank equality partitions and power sums `S_r=sum_b q_b^r`. It did not fit to holdout outcomes. The [independent hosted checker](https://github.com/sushxnthd/vektor/blob/research/v309-external-ptx-bottleneck-gate/research/v309/bank_equality_moment_law.py) verified all 4,140 partitions, mass normalization, and the exact conservation law.

| Frozen unseen IID regime | Analytic predicted issue ratio | Observed independent 100k-opportunity ratio | Absolute error | Frozen direction/error gates |
|---|---:|---:|---:|---|
| Uniform banks 0..7 | 1.007648758 | 1.007885820 | 0.000237062 | PASS |
| 95% hot banks 0..1 | 1.097348334 | 1.097064999 | 0.000283335 | PASS |

These predictions are mathematically nontrivial **pre-outcome** conditional issue-admission forecasts, unlike the tautology `E[M]=E[G]+p` measured after outcomes. They are classical combinatorial calculations, not a claimed new general-purpose theorem. Both distributions are synthetic and iid, not trace-derived GPU workloads.

The ideal unbottlenecked throughput condition is `r_f * R_issue > 1`. At the hot2 predicted ratio, the candidate must retain more than **91.13%** of the compact baseline's frequency, before occupancy, queue, scoreboard, downstream bandwidth or control costs. At uniform8 it must retain more than **99.24%**. A matched extracted-RC timing result is therefore decisive.

## Decision

**Do not kill the factored RTL yet:** it survives functional, generic-cell and matched standard-cell **area** gates, and the prospective IID issue law survived two unseen synthetic regimes. **Do not promote a physical speedup:** electrical/timing signoff, wire/load sensitivity, real-workload bank traces, occupancy, fairness and integrated tile consequences are missing. The next hard test is matched physical delay under fixed slew, output load and wire parasitics against compact greedy. If realistic frequency retention multiplied by actual admitted-work advantage is <=1, kill the mechanism, even though the area and synthetic gates passed.

The rejected brute-force implementation, V296 physical no-go and V287 retirement remain preserved. No RTX 5090 equivalence claim.
