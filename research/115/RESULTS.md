# Vektor-115 results — 2026-10-12

**Evidence type:** deterministic synthetic host model, source anchor audit and independent C++ enumeration. No GPU runtime, cycle, synthesis, PPA or silicon evidence.

| Group | Configurations | Reordered | Incorrect naive FIFO VA→PA attributions | Paired-model incorrect attributions |
|---|---:|---:|---:|---:|
| Discovery seed 115001 | 256 | 221 | 972 | 0 |
| Holdout seed 115002 | 128 | 115 | 476 | 0 |
| Surprise seed 115003 | 48 | 44 | 215 | 0 |

Independent C++ exhaustively enumerated 36 three-request mapping/order permutations: 30 configurations ambiguous, 72 wrong naive attributions. Six Python regression tests passed. The paired model's zero error is a consistency check against its own explicit mapping, **not independent Vortex runtime validation**.

**Residual:** predicted naive FIFO misattribution >0; observed 1663 over 432 cases. Predicted translation-point paired-model misattribution 0; observed 0, tautological until a simulator run independently checks translations. Predicted lane-vs-request discrepancy for eight lanes sharing one line: 8 vs 1 in a simplified 32B grouping model.

**Competing explanations:** a real trace may provide a unique request ID that avoids FIFO matching; real scheduling may not reorder particular same-key requests; MMU may not see the same grouping for all address classes. **Uncertainty:** no frequency estimate for real workloads.

**Prior art:** neither request tagging nor paired translation logging is novel; Vortex's existing MemReq and MMU provide the mechanism. This is instrumentation/correctness infrastructure, not a new GPU architecture or breakthrough.

**Foothold status:** useful capability-building diagnostic, not a GPU speedup. **5090-class gates:** compute/tensor/graphics/ray/memory performance, frequency, area, power and software stack all INCONCLUSIVE.
