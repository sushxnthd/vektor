# V309: stronger equal-resource generic synthesis control (2026-10-31)

**Evidence tier: independently hosted RTL oracle and generic Yosys synthesis.** [Successful PR-attached run #41157729254](https://github.com/sushxnthd/vektor/actions/runs/41157729254), source commit `273ecc8aa851bef1363e90c416598b115b1df341`. The stronger baseline protocol was committed **before** its synthesis outcome at `83e9a28df31040beb32ed70d2adfd1aae8118cdf`. No routed timing, electrical signoff, power or GPU speedup is claimed.

## Independently accepted functional and synthesis result

Icarus compared the new compact-greedy baseline with the original greedy **grant mask**, and both exact-max implementations with the independent per-bank counting oracle. **All 109,076 cases passed**: 104,976 exhaustive reduced-bank combinations, four frozen directed controls, and 4,096 deterministic full-bank cases. The win motif remains 2 versus 3 admitted requests, the no-win motif 4 versus 4.

Same-interface Yosys generic `synth; stat; ltp -noff` on the same hosted toolchain:

| Controller | Policy | Generic mapped cells | Longest generic logic path edges |
|---|---|---:|---:|
| Original serial greedy | Fixed-priority greedy | 1,321 | 49 |
| **Compact greedy (strongest incumbent control)** | **Exactly same fixed-priority greedy** | **260** | **16** |
| Factored exact maximum | Maximum-cardinality subset | 331 | 18 |
| Rejected brute-force exact maximum | Maximum-cardinality subset | 3,802 | 54 |

**Important correction:** the factored exact-max controller is not smaller than a competent implementation of the incumbent. Against compact greedy it costs **331/260 = 1.2730769x generic cells** and has **18/16 = 1.125x generic path edges**. It still passes the preregistered 2.0x generic cell ceiling. The original-greedy comparison (331/1321=0.25057x) was an implementation-quality confound, not a policy area advantage.

## Prospective issue-gain versus timing cost

Previously frozen synthetic holdouts yielded 1.000994x admission ratio on uniform16 and 1.042661x on hot3. A separate exact IID equality-partition predictor has prospectively frozen unseen uniform8 (1.007648758x) and hot2 (1.097348334x) predictions, pending hosted evaluation.

If the candidate's frequency retention is `r_f`, even the optimistic unbottlenecked throughput condition is `r_f * R_issue > 1`. For hot2 this requires `r_f > 0.91129`; for uniform8 `r_f > 0.99241`. **The generic logic-depth ratio is not a frequency measurement.** It raises a serious timing risk but does not itself prove the mechanism fails.

## Decision and next gate

**Continue only conditionally.** A frozen [Nangate45 matched standard-cell mapping protocol](NANGATE45_MATCHED_STDCELL_PREREG_20261031.md) now compares original greedy, compact greedy and factored exact-max using a source-verified Liberty. The mapped-area hard stop is 2.0x the compact greedy. Then require matched input slew, output load, wire parasitics and electrical timing checks. If measured timing, control overhead, occupancy or downstream acceptance erases issue gains, kill the factored mechanism. Neither synthetic admission nor generic depth may be reported as GPU throughput.

Preserve the brute-force rejection, V296 physical no-go and V287 retirement. No new active mechanism, no merge, no force push.
