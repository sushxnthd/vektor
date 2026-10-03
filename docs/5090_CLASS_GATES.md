# RTX 5090-Class Evidence Gates

Vektor may not claim RTX 5090-class capability until the relevant gates below are supported by reproducible evidence. Peak arithmetic alone is insufficient.

| Gate | Requirement | Current status |
|---|---|---|
| FP32 compute | Sustained workload performance consistent with ~104.8 TFLOPS-class peak and demonstrated utilization | INCONCLUSIVE |
| Matrix/AI | FP4/FP8/FP16/BF16 matrix execution with validated throughput, accumulation semantics, sparsity behavior, and workload tests | INCONCLUSIVE |
| Memory | Feasible controller/cache/NoC design sustaining a competitive fraction of 1.792 TB/s under representative traffic | INCONCLUSIVE |
| Graphics | Working geometry/raster/texture/ROP path with representative rendering workloads | INCONCLUSIVE |
| Ray tracing | Working acceleration structure traversal/intersection path with measured scene workloads | INCONCLUSIVE |
| Frequency | Post-synthesis/place-route evidence supporting the target clock in an appropriate process model | INCONCLUSIVE |
| Area | Credible physical-design evidence compatible with the chosen die/package envelope | INCONCLUSIVE |
| Power | Credible power model/estimation compatible with the board/device envelope | INCONCLUSIVE |
| Software | Compiler/runtime/driver path capable of executing nontrivial workloads reproducibly | INCONCLUSIVE |
| Verification | Reference-model equivalence, randomized testing, and formal checks for critical blocks | INCONCLUSIVE |
| Reproducibility | Clean reruns from frozen commits/configs with preserved raw artifacts | INCONCLUSIVE |
| Independent check | Major headline results reproduced by a second implementation/checker where practical | INCONCLUSIVE |

## Evidence labels

- **MEASURED** — physical hardware measurement
- **SYNTHESIZED** — synthesis/place-route derived
- **SIMULATED** — executable simulator or RTL simulation
- **MODELED** — analytical/statistical/physical model
- **PROJECTED** — scaled/extrapolated from lower-level evidence
- **TARGET** — desired value only

Every result table must label its evidence class.
