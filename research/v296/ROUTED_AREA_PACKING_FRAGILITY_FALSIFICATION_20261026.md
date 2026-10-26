# V296 routed-area packing fragility and physical no-go (2026-10-26)

**Evidence tier:** retrospective exact-arithmetic sensitivity of *already reported routed single-slice standard-cell area*, not a prospective prediction, independently placed replicated tile, or measured GPU throughput. The existing draft PR #13 and V296 mechanism remain unchanged. V287 stays retired.

## Source and admissibility

Matched post-CTS detailed-route, extracted-RC run [40309580865](https://github.com/sushxnthd/vektor/actions/runs/40309580865). Previously reported and audited candidate artifact 12648648864 (ZIP SHA-256 `057d4fe6d4bf67164857c54c9635c302e163da6b486f59515b7b8151578d8388`); independently optimized fifth-stage serial artifact 12655030936 (ZIP SHA-256 `1ea4affb6c1f583a775aa9ee084a9c6dcd0b7856d5b8fa1850693f2f05617f67`). This pass uses the *frozen scalar values*, not a fresh raw-ZIP audit. Do not substitute mapped areas from another topology or compare unlike evidence tiers.

| Frozen metric | V296 pairwise | Fifth-stage serial |
|---|---:|---:|
| Routed cell area (µm²) | 17,857.644252 | 18,953.830505 |
| Extracted setup slack (ns) | −1.047895 | −1.859922 |
| Extracted hold slack (ns) | −0.036622 | −0.019796 |
| Max capacitance violations | 3 | 3 |
| Max slew / DRC violations | 0 / 0 | 0 / 0 |
| Physical gate, setup ≥ +0.050 ns, hold ≥ 0, cap/slew/DRC = 0 | **FAIL** | **FAIL** |

The candidate requires at least **1.097895 ns** setup improvement at the existing 3.5 ns constraint *plus* hold and capacitance repair. The serial control requires 1.909922 ns of setup improvement. Neither is a feasible routed implementation.

## Exact routed-area packing boundary

Let `A=17857.644252` and `S=18953.830505` µm² denote measured **single-slice cell areas**. For an imaginary fixed cell-area budget equal to `N` serial slices, the optimistic copy-count law is

`n_V296(N) = floor(N*S/A)`, and `N_first_extra = ceil(A/(S-A)) = 17`.

At `N=17`, 17 serial slices cost **322,215.118585 µm²**, while 18 V296 slices would cost **321,437.596536 µm²**. The entire hypothetical 18-slice advantage rests on **777.522049 µm²** of unused area, or **43.195669 µm² per candidate slice**. This permits a uniform candidate area increase of **only 0.2418889568%** before the eighteenth candidate slice no longer fits. It is an *area-budget* sensitivity, not an estimate of real multi-slice routing overhead.

| Adverse candidate-only area change | V296 copies under 17-serial budget | First serial budget with an extra copy |
|---|---:|---:|
| 0% | 18 | 17 |
| +0.20% | 18 | 17 |
| +0.24% | 18 | 17 |
| **+0.25%** | **17** | **18** |
| +1.0% | 17 | 20 |
| +2.0% | 17 | 25 |
| +5.0% | 17 | 93 |

A symmetric adverse change of V296 +0.25% and serial −0.25% also removes the eighteenth copy. These are hypothetical area perturbations; none was measured. This analysis does **not** assume that 17/18 copies can fit the original single-slice die, and does not invent a tile floorplan.

## Independent reproduction and falsification

Run `node research/v296/routed_area_packing_fragility.js --self-test`. The dependency-free checker uses integer-scaled six-decimal area values, independent repeated-addition copy enumeration over 201 budgets and five perturbation pairs, boundary tests, physical feasibility gates, deliberately invalid-input rejection, and nonadvantage negative controls. The executable self-test passed in the research runtime before committing. Its scalar source must remain pinned to the original physical evidence; this checker is not an independent SPEF/DEF archive verifier.

## Decision

**Reject the inference that a 5.78% routed single-slice area saving establishes a robust 17→18-slice GPU advantage.** The arithmetic opportunity exists only at a 0.242%-thin unallocated-area margin, with no demonstrated replicated placement, wires, shared interconnect, power grid, memory macros, bandwidth, or feasible clock. The physical gate is already failed for both contestants. The previously frozen high-occupancy win and bandwidth/low-occupancy no-win synthetic regimes remain conditional and unopened as real holdouts.

**Next decisive gate:** await the ongoing symmetric bank-decoder four-way synthesis and paired pre-CTS experiments; reject the decoder repair if its candidate does not achieve +50 ps pre-CTS setup or exceeds the preregistered mapped-area threshold. If it survives, obtain paired post-CTS detailed-route extracted-RC closure and a physically replicated equal-resource tile against the strongest fifth-stage serial control. Preserve all failures and do not claim RTX-5090 equivalence.
