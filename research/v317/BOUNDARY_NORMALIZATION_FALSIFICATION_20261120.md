# V317 boundary-law normalization falsification — 2026-11-20 UTC

**Evidence tier:** exact-rational analytic counterexample, independently arithmetic-checked; not a GPU workload, RTL, or PPA measurement.

Existing research branch `research/v317-sass-provenance-gate`, draft PR #34. No mechanism activation, no prospective holdout access, no V287 revival.

## Finding

A bandwidth **capacity ratio** between candidate and baseline is *not generally* an upper bound on **achieved throughput ratio**. In a two-resource fluid model, baseline issue capacity = 1/2 item/cycle, candidate issue capacity = 3/5 item/cycle, and both bandwidth capacities = 1 item/cycle. Baseline delivered = 1/2, candidate delivered = 3/5, throughput ratio = 6/5, while candidate/baseline bandwidth capacity ratio = 1. Thus `min(service_ratio * clock_ratio * occupancy_ratio, bandwidth_capacity_ratio)` incorrectly caps throughput at 1 in this case.

The correct necessary capacity ceiling for fixed units is `T_candidate/T_baseline <= min(C_issue_candidate/T_baseline, C_bandwidth_candidate/T_baseline)`. A candidate/baseline bandwidth *capacity* ratio can replace the second term only with an additional premise that the baseline fully saturates its bandwidth capacity (or an equivalent verified utilization adjustment). Resource-unit conversions, clock domain, occupancy, queue backpressure, and work-per-item must be defined before using the expression as a predictive boundary.

The previous V317 headroom gate is a **conditional screening heuristic**, not a universal necessary inequality. Its no-go decision does not depend on this invalid universal interpretation: the frozen alternating-middle-slot candidate's empirical development throughput geometric mean was 0.999935x, with no observed headroom. Do not generalize the rejection to untested mechanisms or workloads.

## Reproduction

`python3 research/v317/rtl/independent_bandwidth_normalization_counterexample_20261121.py`

Independent exact-fraction arithmetic for the central counterexample was executed in the working runtime. The committed full script was read back from GitHub; hosted CI execution of the full script is not yet established. Do not claim a CI pass.

## Next gates

Integrate this checker into the existing research CI after review, freeze a dimensionally consistent boundary with measured baseline utilization, then require prospective unseen workloads and matched physical timing/area/electrical evidence before architectural advancement. Preserve prior routed electrical failures and negative results. No RTX-5090-equivalence claim.
