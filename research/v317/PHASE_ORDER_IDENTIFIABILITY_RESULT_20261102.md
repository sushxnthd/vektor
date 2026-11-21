# V317 prospective phase-order identifiability: low-cost control falsifies selected oracle advantage (2026-11-02)

## Evidence chronology
The [frozen protocol](FROZEN_PHASE_ORDER_IDENTIFIABILITY_20261102.md) was committed first at 065830f, before the evaluator and results. The positive two-phase pattern was originally selected by searching 1,600 synthetic candidates and is **not an independent workload**. New seeds (137, 271, 809), 500-cycle warmup, 3,000 measured cycles, five regimes and the low-cost degree heuristic were preregistered. Python evaluation and separately implemented independent checker ran locally; hosted workflow is a separate confirmation gate and must not be called successful before completion.

## Result (aggregated over three frozen seeds)

| Regime | Greedy | Reverse | Degree | Exact oldest-preserving | Exact / strongest simple | Frozen decision |
|---|---:|---:|---:|---:|---:|---|
| Selected clean | 24,000 | 24,000 | 28,800 | 28,800 | **1.00000x** | Predicted >=1.05: FAIL |
| 1% phase flips | 23,910 | 23,986 | 28,572 | 28,572 | **1.00000x** | Predicted >=1.02: FAIL |
| Independently shuffled row order | 27,392 | 27,075 | 27,328 | 27,651 | **1.00946x** | Predicted <1.05: PASS |
| Independent random phase | 22,709 | 24,122 | 24,677 | 24,677 | **1.00000x** | Predicted <1.05: PASS |
| Selected clean, cap 2 | 18,000 | 18,000 | 18,000 | 18,000 | **1.00000x** | Predicted <=1.01: PASS |

The selected clean trace still gives exact / original greedy = 1.20000x, but the *stronger* conflict-degree heuristic matches the exact policy's 28,800 completions exactly. The phase-flip and phase-random cases also match exactly. Thus the apparent 20% oracle benefit is not distinctive to exact combinatorial selection on this selected workload. With row-order shuffling, exact beats the strongest simple comparator by only 0.946%, below the frozen 5% relevance gate. All 60 independently implemented full-trace policy replays matched the evaluator. Exhaustive 6,561 four-request three-bank snapshots verified legality, oldest inclusion and oracle dominance of simple policies for caps 2 and 4.

## Mechanism and interpretation
The cheap heuristic serves the oldest request, then sorts the other three by increasing *static pairwise bank-overlap degree* and grants feasible requests. It does not enumerate all feasible subsets. It is a combinational scheduling rule with equal abstract read-port and output resources; its actual gate count, critical path, routed wire, power, and electrical legality remain unmeasured. It is not necessarily a superior physical design.

The two pre-outcome descriptive features in the frozen protocol, lag-1 phase persistence and canonical row-order fraction, are not validated positive boundary laws. In particular, the degree heuristic eliminates exact's benefit on the clean and 1%-flip traces despite their different phase persistence. The correct claim is a **synthetic negative control**, not a new GPU mechanism.


## Generalization caveat from exhaustive snapshots
The degree heuristic is **not** universally cardinality-optimal. In the independent exhaustive 3-bank, four-request space (6,561 operand assignments), degree matches exact on all cap-2 snapshots but loses one grant in **264/6,561 = 4.024%** of cap-4 snapshots. This prevents mistaking its equality on selected temporal streams for a theorem or a physically proven replacement. The check is combinational and does not predict sustained throughput.

## Physicality decision
**Kill the selected periodic trace as evidence that a costly exact scheduler has a material advantage over strong simple controls.** Retain the prior physical V317 falsification, where compact greedy physically dominated pairwise and all RF-proxy routes were electrically illegal. Do not restart V287 or promote a second active architecture mechanism. No same-resource routed clock, SRAM macro, real GPU IPC, calibrated power or RTX 5090 equivalence is established.

## Reproduction
Run: python3 research/v317/rtl/phase_order_identifiability.py > /tmp/v317-phase-order.json
Then: python3 research/v317/rtl/audit_phase_order_identifiability.py /tmp/v317-phase-order.json
The independent checker does not import the evaluator. Hosted GitHub Actions workflow: .github/workflows/v317-phase-order-identifiability.yml.

## Next high-value kill test
Do not spend another run searching for synthetic patterns. Require a workload-derived bank-conflict trace, finite source/backpressure, a pre-outcome predictor and a competent physically matched degree/greedy RTL baseline. If physical timing/area or bandwidth ceiling erases the prospective gain, terminate the architecture claim.
