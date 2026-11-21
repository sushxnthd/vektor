# Oldest-protected oracle: exact small-bank fairness bound (2026-11-19)

## Evidence tier and hypothesis
This is exhaustive combinational Python enumeration, **not** a new scheduler mechanism, RTL simulation, P&R, finite-buffer throughput, fairness guarantee, or GPU IPC. It independently challenges the earlier unfair oracle by imposing a necessary condition for starvation avoidance: the oldest queued request must be served in the current batch. This is stronger than bounded-age service and can exclude implementable fair policies; it is an intentionally restrictive control, not a sufficient proof of long-run fairness.

Four ordered requests, two operands each, two reads per bank. Enumerate all B^8 operand assignments for B=2,3. Compare (1) greedy that scans all four requests and skips infeasible ones, (2) unrestricted max-cardinality oracle, and (3) max-cardinality oracle required to serve request 0. All use identical bank ports and four-slot window; oracle logic/area/timing are **not** equal-resource.

## Executed results
- B=2: 256 assignments; aggregate greedy/oracle/oldest-protected grants = **442/494/442**. Unrestricted oracle improves on greedy in **52** cases; oldest-protected improves in **0**. Thus every two-bank instantaneous oracle gain disappears under the oldest-served condition.
- B=3: 6,561 assignments; aggregate grants = **14,391/15,435/14,667**. Unrestricted oracle improves in **1,044** cases; oldest-protected improves in **276**. Aggregate grant ratios are 15435/14391 (~1.07255) unrestricted and 14667/14391 (~1.01918) oldest-protected. The latter is below the frozen 1.02 materiality gate even before clock, occupancy, bandwidth, or implementation overhead.
- These are **ratios of summed grants under uniformly enumerated independent batches**, not finite-FIFO throughput or actual scheduler IPC. Uniformly weighting all assignments is a specific synthetic workload.

## Interpretation / falsifiers
The previous unfair oracle's head-bypass counterexample is not a deployable win. Even an unimplemented zero-cost, oldest-protected maximum-cardinality policy has <2% headroom in these B=2,3 controls, and its combinational hardware overhead is ignored. No positive physical V317 claim is reinstated. The previously established compact-greedy area advantage and illegal routes remain binding.

Independent reproducibility: `python research/v317/rtl/oldest_protected_oracle_20261119.py`. Assertions pin both full enumerations. The checker was executed in the local container before commit, but hosted CI has not been verified. This is a **necessary instantaneous headroom test**, not a substitute for age-tail, finite-queue, electrical or matched-tile experiments.
