# V309 authenticated V100 source-conditional address identifiability result (2026-10-30)

**Status:** source-level provenance hypothesis supported by the observed trace cardinalities; **not proven producer identity**. The [full-corpus hosted audit #40986462858](https://github.com/sushxnthd/vektor/actions/runs/40986462858) **passed**. [Raw JSON artifact #12946638184](https://github.com/sushxnthd/vektor/actions/runs/40986462858/artifacts/12946638184) (verify artifact ID from hosted run before relying on this specific artifact link). No GPU throughput, hardware mechanism or RTX 5090 result is claimed.

## Why this test was necessary
The [2020-03-09 upstream tracer source](https://github.com/accel-sim/accel-sim-framework/blob/0e2fddcdef37fc59ad786553892b75567a5f2cdb/util/tracer_nvbit/tracer_tool/tracer_tool.cu#L660-L736) prints `active_mask & predicate_mask` but compresses memory addresses using `active_mask`. Consequently, the original active-lane mask is a hidden variable. The earlier report's rule that a contiguous printed format-1 mask identifies the lane addresses is **not valid under this source hypothesis**. A constructive, exact one-sector/two-sector counterexample is given in [the source-level falsification](LEGACY_PREDICATE_MASK_SOURCE_FALSIFICATION_20261030.md).

## Full authenticated corpus, with source-conditional classification
Frozen archive SHA-256: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Exactly 210 trace files and 240,465 LDG/STG/ATOM/RED global-proxy instruction rows were inspected.

| Class | Rows | Meaning |
|---|---:|---|
| Format 0, explicit addresses | 106,728 | Historical source model: one token per original active lane |
| Format 0, exact active mapping | **84,224** | Token count equals visible popcount, so original A=M |
| Format 0, hidden predicate/address mapping | **22,504** | More address tokens than visible active lanes |
| Format 1, base+stride | 133,737 | Hidden original first lane may shift the base |
| Format 1, exact 32B sector count | **133,366** | All source-consistent first-lane candidates give the same sector count |
| Format 1, non-identifiable 32B sector count | **371** | At least two source-consistent first lanes yield different sector counts |
| Of those 371, previously treated as decoded | **368** | Printed mask was contiguous; old decoder assigned one unqualified value |
| Of those 371, previously excluded | 3 | Printed mask was noncontiguous |
| Format 2 | 0 | No such rows in this corpus |

The 22,504 format-0 hidden-predicate rows carry **274,152 extra serialized address tokens** beyond the printed active-lane popcount. No format-0 source-incompatible row was observed by this count model.

Under the 2020 source hypothesis, **217,590/240,465 = 90.4872%** of global-proxy rows have an identified *32-byte sector count*, comprising 84,224 exact format-0 rows and 133,366 format-1 rows with invariant sector counts. This is **not** a claim that their absolute addresses or producer identity are identified. A further 371 format-1 rows have bounded rather than point-identified sector counts, and 22,504 format-0 rows remain address-mapping ambiguous.

For the 133,737 format-1 rows, the sharp source-conditional total is **1,194,830–1,195,201 sectors**, a 371-sector interval. Adding the 348,070 sectors in exactly recoverable format-0 rows yields **1,542,900–1,543,271** sectors across the 217,961 rows for which this source model provides exact or bounded sector counts. These are per-warp instruction sector sets summed across rows, not hardware transaction counts. The 22,504 unidentifiable format-0 rows are excluded from this interval, so it is **not a full-corpus sector interval**.

## Important correction to the earlier V309 memory result
The prior report gave 129,883 supposedly unambiguous format-1 rows and 32.9867% utilization on those rows. **368 of those 129,883 rows are not sector-identifiable under the historical source hypothesis**. The earlier point estimate must be labeled a conditional decoder result, not unconditional trace truth. Separately, 84,224 format-0 rows and 3,851 previously excluded sparse format-1 rows have source-conditionally identified sector counts. This is a qualified improvement in **trace interpretability**, not a GPU speedup.

## Workload heterogeneity
Format-1 sector ambiguity occurs in BFS (68 rows), LUD (240), and Pathfinder (63). Format-0 hidden-predicate ambiguity is especially prevalent in BFS (9,698), Streamcluster (7,716), Hotspot (2,766), and Backprop (2,048). These are exploratory, not prospective holdouts.

## Verification and boundaries
- [Frozen protocol](LEGACY_PREDICATE_MASK_PROTOCOL_20261030.md) committed before full-corpus evaluation.
- [Executable analyzer](legacy_predicate_mask_provenance.py) passed **2,295 exhaustive small-mask/width/stride envelope cases**, two constructive source-level counterexamples, authenticated SHA-256, and 210-file/240,465-row conservation.
- [Final hosted run #40986462858](https://github.com/sushxnthd/vektor/actions/runs/40986462858) **passed**. Initial hosted run #40986243894 failed only at a reporting assertion because zero-count format-2 was omitted from the sparse JSON; the corrected workflow retained the identical source model and results.
- This is not an independent full-corpus decoder. An independent reimplementation of the historical producer, archive-header version audit, and independent counters are still needed.
- The 2020-03-09 source is an **unverified producer hypothesis**, even though it explains both earlier parser anomalies. Neither a date match nor consistent cardinalities prove identity.
- Sector counts are not actual memory transactions or stalls. No cache, ordering, bandwidth, occupancy, physical timing, area or power benefit is established.

**Research decision:** preserve the source-conditional correction and continue V309 trace qualification. Do not promote any memory coalescer or other hardware mechanism. Retired V287/V296/V297–V308 stay retired; draft PR #26 remains the sole Vektor research PR. Kernellum #119 untouched.
