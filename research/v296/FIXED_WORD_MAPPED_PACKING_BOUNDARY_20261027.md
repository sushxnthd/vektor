# V296 fixed-word RF proxy: mapped-area advantage is fragile under tile packing (2026-10-27)

**Evidence tier: SHA-verified RTL + mapped synthesis + candidate-only fourth-stage pre-CTS. NOT extracted-RC signoff, NOT a GPU throughput win.** This is a sensitivity/falsification of the *implementation* of the sole V296 pairwise bank-admission mechanism. V287 remains retired. The older decoded density-0.35 implementation remains rejected.

## Frozen source and observed progress

[Hosted trial #40457696916](https://github.com/sushxnthd/vektor/actions/runs/40457696916), head `e6c13b1fad973f74502aeb5679656d87e3e66221`, used the preregistered fixed-word two-port RF cone. The 2048-cycle RTL test passed 4096 comparisons and 2048 one-cycle-delayed checks (6589 accepted wave events); both PAIRWISE variants matched their original decoded implementations and direct-index oracle. Four-way same-library mapped synthesis passed with exactly 388 flops per design (132 DFFR_X1 + 256 DFF_X1).

Original artifacts downloaded and independently SHA-256 verified:

- Four-way mapped synthesis [artifact 12714054823](https://github.com/sushxnthd/vektor/actions/runs/40457696916/artifacts/12714054823), SHA-256 `bb75e7eb91e13599d9fcc230caaef51b0c1c43d579128ac3100d2f78b02f7522`.
- Candidate fourth-stage pre-CTS [artifact 12716756605](https://github.com/sushxnthd/vektor/actions/runs/40457696916/artifacts/12716756605), SHA-256 `cebe917377f0a3195a43e9bdb3917a0b8036e198ed8444250d7fca019c10f349`.

The paired serial pre-CTS job was still running at this audit; it is **not** a serial physical result. Both original ZIPs are the source of truth, not the earlier PR status text. The independent [area/packing audit](fixed_word_area_boundary_audit.py) recomputes mapped area, flop count, topology depth, candidate pre-CTS metrics, and exact-decimal packing boundaries from those ZIPs. It fails closed on SHA mismatch, missing fields, unexpected state, and evidence-tier mismatch.

## Four-way matched synthesis (Nangate45, area in um²)

| Implementation | Mapped area | Sequential flops | Topological depth |
| --- | ---: | ---: | ---: |
| Decoded pairwise | 9398.312 | 388 | 254 |
| Decoded serial | 10176.894 | 388 | 286 |
| Fixed-word pairwise | **8095.178** | 388 | 251 |
| Fixed-word serial | **8615.740** | 388 | 273 |

The fixed-word implementation reduces pairwise mapped area by **13.8656%** and serial mapped area by **15.3402%** versus the corresponding decoded implementations. But the candidate's relative area advantage **shrinks** from 7.6505% to **6.0420%** against its *symmetrically optimized* serial control, a deterioration of **1.6085 percentage points**. This is not an architecture performance advantage. It shows the RF-cone change helps both contestants, and helps serial proportionally more.

## New predictive packing boundary and negative controls

For an area budget that fits exactly `n` identical serial slices, a hypothetical `n+1` pairwise slices can fit only if

```
(n+1) * A_pairwise * (1+h) <= n * A_serial
h <= [n * A_serial / ((n+1) * A_pairwise)] - 1
```

Here `h` is **candidate-only** unmodeled area overhead relative to the mapped candidate area. This is an exact conditional arithmetic boundary, **not** a physical tile-packing result or a prediction of actual area overhead.

| Serial slices n | Candidate slices n+1 | Max candidate-only overhead h |
| ---: | ---: | ---: |
| 12 | 13 | -1.7564% (impossible at h>=0) |
| 15 | 16 | -0.2214% (impossible at h>=0) |
| 16 | 17 | **+0.1699%** |
| 17 | 18 | **+0.5177%** |
| 20 | 21 | +1.3624% |
| 32 | 33 | +3.2054% |

**Falsification/sensitivity:** At the illustrative 16-to-17 boundary, a mere **0.1700% candidate-only area penalty** erases the extra hypothetical slice. At 15-to-16, even zero penalty cannot fit it. The original relative advantage was larger; the symmetric optimization makes this tile-capacity argument *more fragile*, not less. All thresholds exclude clock trees, shared structures, RF macros, routing, power distribution, and resource granularity.

## Candidate-only physical checkpoint

The SHA-pinned fourth-stage *pre-CTS global-route* candidate log reports repaired cell area **12806.5700 um²**, setup slack **+0.230183 ns**, hold slack **+0.112255 ns**, zero capacitance and zero slew violations. This passes the candidate's frozen early pre-CTS numerical guard (+0.050 ns), **but it is not post-CTS, detailed routing, extracted SPEF, or electrical signoff**. The repaired pre-CTS cell area is **58.2000%** above the unplaced mapped area, illustrating why mapped tile-packing extrapolations are especially unsafe. This is not a candidate-only *relative* penalty against serial, because its matched pre-CTS area is not yet available.

The fourth-stage serial pre-CTS job must complete and be independently checked before a paired pre-CTS decision. Any subsequent full-route trial must use the **strongest fifth-stage optimized serial control**, identical density/clock/RC/constraints, extracted setup >=+0.050 ns, hold >=0, zero cap/slew/DRC, and the frozen area limit. Failure rejects the fixed-word repair, not the old already-rejected decoded implementation.

## Generalizability and next scientific decision

The fixed-word shortcut depends on **two words per bank and two read ports per bank**. With deeper banks, static dedicated word outputs would require more ports or additional muxing, so this is **not evidence for a production SRAM RF**. At identical grants and clock, the refactor has **zero admission-throughput gain by construction**. It has no demonstrated power or bandwidth benefit; speculative switching of both word outputs remains unmeasured.

**Decision: RTL and mapped synthesis pass; candidate pre-CTS numerical gate passes; paired physical evidence incomplete; no GPU win.** Await serial pre-CTS completion, then perform an independently audited matched routed/extracted-RC trial only if all frozen gates survive. Preserve all negative results, holdouts, and Kernellum PR #119. No force-push, merge, or RTX-5090-equivalence claim.
