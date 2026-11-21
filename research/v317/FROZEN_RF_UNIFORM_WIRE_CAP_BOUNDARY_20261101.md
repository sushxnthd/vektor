# V317 frozen uniform-wire capacitance adversarial boundary (2026-11-01)

## Evidence tier and noninterference
Existing active kernel: **pairwise fixed-priority bank-credit implementation** on `research/v317-sass-provenance-gate`, draft PR #34. This experiment changes **no RTL, grant semantics, cell mapping, scheduling mechanism, or architectural baseline**. It reuses the same pinned Nangate45 typical Liberty (Git blob `90e4afb274cfc6514c587c434c77903d554117d1`), unchanged source and pairwise RTL, Yosys/ABC synthesis recipe and matched BUF_X1 24-fF output stage. No Kernellum branch is modified.

## Why this test
Prior independent mapped-netlist audit found minimum **ideal-wire** internal max-cap margins of +0.680998 fF (original bank-mask) and +3.838028 fF (pairwise). These margins ignore interconnect capacitance. We must establish the exact adverse **uniform additional interconnect-capacitance** boundary before making physical claims.

## Predictions frozen before new checker and rerun
Let `c` be an *adversarial equal additional wire capacitance* in fF added to **every mapped-cell-driven net**, on top of its characterized sink-pin loads and four matched BUF_X1 input loads. No placement, extracted RC, or physical wire lengths are assumed.

1. **c=0 fF:** both mapped cores pass internal max-cap checks.
2. **c=1.0 fF (predicted win):** original bank-mask has at least one internal max-cap violation; pairwise has none.
3. **c=4.0 fF (predicted no-win):** both have at least one internal max-cap violation; **no design can claim max-cap electrical legality**.
4. Exact admissible uniform-wire thresholds equal the independently audited minimum margins, within 0.00001 fF: original 0.680998 fF; pairwise 3.838028 fF.
5. At `c=0.5 fF`, both remain internally legal. At `c=2.0 fF`, original fails, pairwise remains legal.

These are prospective **checker-transfer** predictions, not independent physical observations: the previous zero-wire margins make the thresholds analytically foreseeable. Any mismatch is a checker/flow inconsistency requiring investigation.

## Method
Build a standalone second-pass checker on the original mapped netlist and Liberty parser. Require one characterized output driver per internal mapped net; reject missing Liberty pins, ambiguous aliases, unknown cells, negative wire caps, unsupported net syntax and multiple drivers. Account for the four matched output-buffer input pin capacitances. Report the number of violations at c=0,0.5,1,2,4 fF, the worst 10 nets, exact uniform-wire headroom and the budget converted to **hypothetical** wire-length limits at 0.1 and 0.2 fF/um. Preserve the direct-primary-input grant[0] as **uncharacterized**; do not silently certify it. Require independent unit tests for threshold equality, positive/negative cap, and malformed input.

## Scientific kill criteria
A pre-route timing/area win does not imply routed timing or max-cap legality. At `c=4 fF`, both must be classified as electrical failures; do not claim a pairwise physical win. At `c=1 fF`, only a *conditional uniform-capacitance robustness advantage* is supported, **not** actual routing quality. If the checker disagrees with the existing independent audit, do not promote the result. No RTX 5090 equivalence or measured GPU throughput. Next mandatory gate remains actual placement/extracted parasitics, characterized input drive, setup/hold, and tile-level bottleneck evaluation.
