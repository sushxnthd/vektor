# V309 source-conditional format-0 sector identifiability gate (frozen before full-corpus evaluation, 2026-10-30)

## Motivation and hypothesis
The 2020-03-09 Accel-Sim tracer snapshot prints M=A&P but serializes format-0 addresses in ascending order for the **unmasked** active-lane set A. The 22,504 previously classified format-0 rows with more addresses than visible lanes have *unknown address-to-visible-lane association*. The earlier report excluded them. We test how many sector counts are nevertheless identifiable, without guessing a producer commit or physical GPU transactions.

## Frozen algorithm and predictions
For each format-0 row, let n be serialized address count, k=popcount(M), and h=n-k. Enumerate source-compatible A supersets of M with popcount(A)=n when the combination count is bounded. Each A maps the k visible lanes to a subsequence of the n address tokens; compute the distinct 32-byte sectors touched by visible accesses of the recorded width. Exact min/max over all compatible A are sharp. For large sets, use rigorously conservative per-visible-lane candidate-token intervals and sector-set union/intersection bounds; never treat approximate intervals as sharp.

**Predicted identified regime:** if n=32, A must contain all lanes, so visible-lane addresses and sectors are uniquely recovered despite hidden predicates. **Predicted ambiguous regime:** with M={lane 1}, n=2, and token addresses in disjoint sectors, A={0,1} and A={1,2} are both compatible and can assign different sectors to lane 1; sector *count* may nevertheless be invariant at 1. For a genuinely non-identifiable count, use width 4, tokens 0x101f and 0x1040: lane 1 can select a crossing access (2 sectors) or a noncrossing access (1 sector).

## Limits, thresholds, controls
- Fixed original archive SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`; 210 trace files; 240,465 active global-proxy memory rows.
- Exact enumeration cap: 4,096 source-compatible A choices per row, and at most 2,000,000 enumerated masks in total. Larger rows use safe bounds, never a partial enumeration.
- For fallback, possible token ranks for visible lane l derive from mandatory M lanes before/after l and optional hidden-lane capacity. Union of intersections across each visible lane is a guaranteed-sector lower bound; union of all candidate token sectors is an upper bound. Apply simple per-lane cardinality bounds as well. Bounds must contain every exact exhaustive oracle case.
- Exhaustive small-width (up to 6 lanes) independent brute-force test against all A supersets and multiple adversarial address patterns, plus source-incompatible malformed-record rejection.
- Report full-corpus global and per-family exact/ambiguous/fallback counts and conservative **full-corpus sector-count interval**; compare to the previously partial 1,542,900–1,543,271 conditional interval without claiming measured transactions. Never claim a speedup, a new hardware mechanism, or unconditional producer identity.
- Strongest hardware baseline remains an ideal fixed-address coalescer, already optimal for unchanged addresses. No V287/V296 revival; no new mechanism promotion on data-integrity evidence alone.

## Kill criteria
If the source-conditional exact decoder cannot reproduce exhaustive independent small-mask cases, if the archive invariants fail, or if its results are inconsistent with the prior format-0/format-1 conservation, reject the result. If few ambiguous rows are resolved, preserve the negative result rather than inventing a hardware gain. Rodinia is exploratory, not a prospective GPU-architecture holdout.
