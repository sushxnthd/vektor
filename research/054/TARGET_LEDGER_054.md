# Vektor-054 target and evidence ledger (2026-10-09)

Reference: NVIDIA GeForce RTX 5090 official specifications, https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ . Partner 28 Gbps GDDR7 specification: https://www.gigabyte.com/in/Graphics-Card/GV-N5090WF3-32GD/sp . Treat the RTX 5090 as an external engineering target, not a design template.

| Dimension | External target | Vektor-1A hypothesis | Evidence gate |
|---|---|---|---|
| FP32 arithmetic | ~104.88 TFLOPS theoretical at 21,760 lanes, 2 FMA ops, 2.41 GHz boost (derived) | 104.8576 TFLOPS arithmetic at 160*128 lanes*2*2.56 GHz | INCONCLUSIVE: no sustained workload |
| Tensor/matrix | NVIDIA markets 3,352 AI TOPS; datatype/sparsity conditions not verified here | 2 matrix engines/tile | INCONCLUSIVE |
| Memory | 32 GB GDDR7, 512-bit, 28 Gbps/pin partner; derived 1,792 GB/s theoretical | 512-bit GDDR7, capacity TBD | INCONCLUSIVE |
| Cache hierarchy | official product page does not state L2; verify from primary architecture documentation | 128 MB distributed L2 | INCONCLUSIVE |
| Texture/raster | workload-specific targets not established | distributed engines proposed | INCONCLUSIVE |
| Ray tracing | NVIDIA markets 318 RT TFLOPS, non-interchangeable with FP32 | distributed trace engines proposed | INCONCLUSIVE |
| Frequency | NVIDIA 2.41 GHz boost | 2.56 GHz design target | INCONCLUSIVE |
| Power | NVIDIA 575 W TGP | <=575 W target | INCONCLUSIVE |
| Area | official product page does not specify die area | <=750 mm2 hypothesis | INCONCLUSIVE |
| Software | CUDA compute capability 12.0, Vulkan 1.4, DX12 Ultimate on NVIDIA | KPX open ISA/compiler proposal | INCONCLUSIVE |
| RF collector | NVIDIA internal design not inferred | experimental tagged fanout, two slots | 24/24 RTL differential tests pass; Yosys generic synthesis 2323 vs 2139 cells (+8.60%); physical PPA pending |
| Overall | broad comparable capability across all workloads | not achieved | INCONCLUSIVE |

Do not compare 3,352 AI TOPS to an unqualified Vektor tensor FLOPS estimate. No graphics/ray/physical feasibility equivalence is supported.
