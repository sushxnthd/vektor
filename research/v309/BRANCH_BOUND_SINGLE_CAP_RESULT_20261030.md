# V309 independent single-cap branch-bound result (2026-10-30)

**Status:** Independently hosted full-corpus PASS. Source-conditional computational reconstruction, **not a GPU hardware mechanism or throughput improvement**. The historical March 2020 tracer source is not proven to be the exact archive producer. All Rodinia families are previously explored, not prospective holdouts.

## Frozen protocol and immutable evidence

- Pre-outcome [branch-bound protocol](BRANCH_BOUND_SINGLE_CAP_PROTOCOL_20261030.md), committed as `53c5ac4` before the solver and hosted result.
- New independent [branch-and-bound solver](sector_branch_bound.py) and [targeted unchanged-baseline replay](sector_branch_bound_targeted_audit.py).
- Original antichain DP and original corpus auditor are **not modified**. The wrapper intercepts only their one UNKNOWN case, independently solves it, then returns the original result so previous counts remain unchanged.
- SHA-256-pinned original Purdue V100 Rodinia archive: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
- [Hosted GitHub Actions #41010015909](https://github.com/sushxnthd/vektor/actions/runs/41010015909): **PASS**. [Immutable JSON artifact #12957018279](https://github.com/sushxnthd/vektor/actions/runs/41010015909/artifacts/12957018279).
- **15,383** exhaustive small-mask and tractable full-32-lane brute-force comparisons passed; **3,219** were nonpoint cases. Explicit resource-cap and 64-bit-overflow refusal passed.

## Prospective targeted result

The original 3,000-state antichain DP returned `state_cap` after 6,119 transitions on a BFS instruction. Its address-token digest was preserved and independently matched.

| Frozen quantity | Result |
|---|---:|
| Printed mask | `0x8545688` |
| Width | 4 bytes |
| Serialized address tokens | 18 |
| Compatible original active-mask completions | 319,770 |
| New solver nodes visited | **10,405** |
| New solver status | **exact** |
| Old conservative row sector interval | 1–10 |
| Exact row sector interval | **9–10** |

The new search uses a feasible incumbent and admissible suffix-union cardinality bounds. It does not use the antichain DP's dominance representation. The original mask completions are a combinatorial count, not a GPU execution count, and solver nodes are not directly comparable to full mask completions as performance measurements.

## Full-corpus conservation and corrected interval

| Source-conditional measurement | Previous antichain | New targeted bound |
|---|---:|---:|
| Trace files | 210 | 210 |
| Global-memory-proxy rows | 240,465 | 240,465 |
| Aggregate 32-byte sector lower bound | 1,586,186 | **1,586,194** |
| Aggregate upper bound | 1,595,385 | **1,595,385** |
| Interval width | 9,199 | **9,191** |
| Point-identifiable rows | 235,076 | 235,076 |
| Remaining antichain-capped rows not solved by alternative | 1 | **0** |

The targeted solver raises the lower bound by only **eight sectors**, a **0.0870% reduction in the previous uncertainty width**. The row itself remains non-point-identifiable (9–10 sectors). The improvement is real under the historical-source hypothesis but **small**. It does not establish cross-family generalization, and it cannot be translated to measured GPU memory traffic.

## Scientific interpretation and stop condition

The previous cap was computational, not proof of intrinsic non-identifiability. Independent search now yields sharp extrema for the sole capped row under the same producer model. This closes the current antichain resource-limit issue without raising its limits or rewriting old evidence.

**Do not continue optimizing this decoder merely to increase a synthetic metric.** The next hard gate is identifying the actual archive tracer producer and validating per-workload sector/cycle behavior against hardware counters or a cycle simulator. The strongest ideal fixed-address coalescer already attains the touched-sector minimum, so no new coalescer hardware is justified.

**Decision:** V309 remains one open qualification workstream in draft PR #26. No new hardware mechanism promoted; V287/V296 and prior retired avenues remain retired. No RTL timing/area, power, GPU IPC, bandwidth, RTX 5090-equivalence, or world-class completion claim is supported.
