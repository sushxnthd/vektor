# Vektor-066 external target ledger — 2026-10-09

NVIDIA official: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ and https://www.nvidia.com/pt-br/geforce/news/rtx-50-series-graphics-cards-gpu-laptop-announcements/ (2025-01-06).

| Capability | RTX 5090 external target | Vektor-1A hypothesis | Gate |
|---|---|---|---|
| FP32 | 21,760 CUDA cores, 2.41 GHz boost; ~104.88 TFLOPS arithmetic projection (2 FLOPs/FMA) | 160 tiles × 128 lanes × 2 FLOPs × 2.56 GHz = **104.8576 TFLOPS projected** | INCONCLUSIVE |
| Tensor | 680 fifth-gen Tensor cores, 3,352 vendor AI TOPS aggregate; FP4 supported | two matrix engines/tile; no datatype/sparsity measured rates | INCONCLUSIVE |
| VRAM | 32 GB GDDR7 | capacity unspecified in physical implementation | INCONCLUSIVE |
| Bandwidth | 1,792 GB/s external | 512-bit GDDR7 target, no PHY verification | INCONCLUSIVE |
| L1/L2/RF | comparable cache hierarchy not established | 128 MB distributed L2, hierarchical RF | INCONCLUSIVE |
| Texture/raster | workload comparison required | distributed engines proposed | INCONCLUSIVE |
| Ray tracing | 170 fourth-gen RT cores; 318 vendor RT TFLOPS aggregate | distributed trace engines proposed | INCONCLUSIVE |
| Frequency | 2.41 GHz boost | 2.56 GHz target | INCONCLUSIVE |
| Power | 575 W board power | <=575 W target | INCONCLUSIVE |
| Area | authoritative comparable die area not established | <=750 mm² target | INCONCLUSIVE |
| Software | CUDA and graphics APIs | original KPX path incomplete | INCONCLUSIVE |

Vendor AI TOPS and RT TFLOPS are not per-datatype independent measurements. Arithmetic peak matching is not RTX 5090-class equivalence.
