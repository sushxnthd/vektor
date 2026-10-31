# V309 antichain exact-sector full-corpus result (2026-10-30)

**Status:** Hosted full-corpus run PASS; qualified source-conditional *workload evidence*, **not** a GPU architecture mechanism. The March 2020 tracer-source snapshot has not been proven to be the producer of this archive. The eleven Rodinia families are exploratory and cannot be called unseen holdouts.

## Frozen experiment and provenance

- Pre-outcome protocol: [ANTICHAIN_DP_PROTOCOL_20261030.md](ANTICHAIN_DP_PROTOCOL_20261030.md).
- Code: [sector_antichain_dp.py](sector_antichain_dp.py) and [sector_antichain_full_audit.py](sector_antichain_full_audit.py).
- Authenticated Purdue V100 Rodinia archive SHA-256: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
- [GitHub Actions run #40996075234](https://github.com/sushxnthd/vektor/actions/runs/40996075234): **success**, all acquisition, SHA, 5,922 exhaustive small-mask oracle, full-corpus conservation, and artifact-upload steps passed.
- [Immutable run artifact #12951506603](https://github.com/sushxnthd/vektor/actions/runs/40996075234/artifacts/12951506603): source-conditional per-family and global JSON evidence.
- All 210 traces, 240,465 global-proxy rows (106,728 format-0 and 133,737 format-1), and the previous conservative interval were reproduced before accepting any tightening.

## Results: original conservative envelope versus bounded exact antichain DP

| Quantity | Previously reported | New independently hosted run |
|---|---:|---:|
| Aggregate sector-count lower bound | 1,580,660 | **1,586,186** |
| Aggregate sector-count upper bound | 1,595,620 | **1,595,385** |
| Aggregate interval width | 14,960 | **9,199** |
| Conditional point-identified rows | 234,425 | **235,076** |
| Conditional point-identification share | 97.4882% | **97.7589%** |

Interval width decreases by **5,761 sectors (38.5094%)**. Lower bound rises by 5,526; upper bound falls by 235. These are sector-count *bounds under a producer hypothesis*, not observed memory transactions.

- **4,454** format-0 rows were eligible for DP (the conservative bound was non-point).
- **4,453 / 4,454** completed with exact extrema; **one** returned UNKNOWN due to a state cap. There were **908,330** total DP transitions, under the predeclared 2,000,000 global budget.
- **3,014** rows had tighter intervals and **651** became point-identifiable.
- All eligible and tightened rows belong to **BFS**. Its envelope tightens from **78,474–93,131** to **84,000–92,896**. No other application's envelope changes.
- This concentration is a negative generalization signal: the algorithm's observed incremental value is not demonstrated across distinct application families.

## Falsifiable interpretation

For a printed predicate-filtered mask `M`, the unobserved original active mask `A` must satisfy `M ⊆ A` and `popcount(A) = n`, where `n` is the number of serialized format-0 address tokens. For each compatible `A`, the ordered address tokens map to the set lanes of `A`. The minimum and maximum union cardinality of touched 32-byte sectors over compatible `A` are the sharp source-conditional bounds.

The antichain DP retains undominated sector unions at each visible-lane and hidden-lane-count state. Subset dominance is sound because future union is monotone. A completed DP yields exact extrema; a resource cap returns UNKNOWN and retains the old conservative interval. This is a **computational identifiability result**, not an architectural speedup law.

Predicted no-win regime: distinct, nonoverlapping sector footprints with fixed visible count, where every compatible assignment touches exactly `popcount(M)` sectors. Predicted potential-win regime: repeated/overlapping sector footprints and hidden predication, where coarse independent lower/upper bounds can be sharpened by rank constraints. The present result supports the latter only on BFS; it does not establish prospective transfer.

## Limitations and next hard gates

1. **Producer identity**: verify the exact source/build that generated the archived SASS records, or explicitly retain conditional status. Do not promote conditional sectors to measured GPU traffic.
2. **Independent implementation (completed)**: [independent original-mask enumeration](sector_antichain_independent_oracle.py) verified **495 full-width (32-lane) fixtures** across **59,016 original-mask completions**, including 75 non-point cases, four footprint regimes, near-64-bit boundaries, translation invariance, and explicit overflow/resource refusal. [Hosted run #41002021914](https://github.com/sushxnthd/vektor/actions/runs/41002021914) **PASSED** on final code; [raw artifact #12954290173](https://github.com/sushxnthd/vektor/actions/runs/41002021914/artifacts/12954290173). This increases algorithmic confidence but does not validate the historical producer or physical memory transactions.
3. **Residual capped row**: the full-corpus JSON now includes the sole state-cap row's trace, line, mask, width, transition count, and address-token digest. Inspect this fingerprint and preregister a targeted sensitivity experiment; do not silently raise resource limits or selectively change thresholds after outcome inspection.
4. **Architecture**: obtain matched V100 counters or validated cycle simulation and prospective independent workloads before choosing hardware. V287/V296 and previously retired bank/coalescer avenues remain retired; no RTL, timing, area, power, IPC, bandwidth, or RTX 5090 claim follows.

**Decision:** Keep V309 as the sole qualification workstream in draft PR #26. No hardware mechanism promoted; no claim of world-class completion.
