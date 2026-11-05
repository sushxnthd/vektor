# V309 bounded exact antichain DP: frozen experiment (2026-10-30)

**Evidence tier:** historical tracer-source-conditional sector-count identifiability, NOT measured GPU traffic or architecture performance. The source snapshot is not proven to be the archive producer. V309 is qualification only; no hardware mechanism is promoted. Retired V287/V296 candidates stay retired.

## Pre-analysis prediction
The previous capped mask enumerator left 4,478 format-0 rows with conservative rather than necessarily sharp sector-count bounds. A distinct DP over reachable **sector-set antichains** may sharpen them without enumerating all original masks.

* Predicted-win synthetic regime: hidden-predicate masks and repeated/equivalent sector footprints across serialized address tokens. The union-set antichain can collapse many original-mask assignments.
* Predicted-no-win synthetic regime: all candidate visible token ranks have distinct nonoverlapping sector footprints and the same visible-lane count. The sector count is already constant and no improvement over a correct bound is possible.
* The **actual 11 Rodinia families are already inspected exploratory data**, not prospective unseen workloads. Report improvement only as within-corpus evidence.
* Pre-specified rejection: if exact DP never tightens a conservative interval, record a negative result; do not promote a hardware candidate.

## Independent algorithm and limits
For printed visible mask M and n address tokens, hypothesize unknown original A containing M with popcount(A)=n. For each visible lane, DP tracks the number of hidden original-active lanes placed before it and the union of sectors of selected address tokens. At equal hidden-count state, discard supersets for minimum and subsets for maximum. Both extrema are exact if all states complete. Prove correctness via state equivalence and dominance. Verify by exhaustive original-mask enumeration for all small masks (2–7 lanes), three address patterns, widths 4 and 8 bytes.

Fail closed on overflowing 64-bit address footprints. Budget: at most 3,000 retained states and 100,000 attempted transitions per row, plus 2,000,000 attempted transitions across the full-corpus fallback rows. When capped, retain the previous conservative bounds. Do not mislabel capped extrema as exact.

## Primary outcome
On SHA-pinned Purdue V100 Rodinia archive aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1, report (1) number of previously conservative format-0 rows made exact, (2) sector-interval reduction by family and overall, (3) capped and overflow rows, (4) strict containment of new bounds within previous bounds, (5) full 210-trace/240,465-global-row conservation. Preserve the original previous 1,580,660–1,595,620 interval for comparison.

## Limitations
These are per-instruction sector-set envelopes under an unverified historical tracer producer, not measured memory transactions, caches, bandwidth, stalls or GPU cycles. No same-corpus workload may be described as a prospective holdout. No hardware, timing, power, area or RTX-5090 claim is justified.
