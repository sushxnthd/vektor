# Vektor-065 RTX 5090 external target ledger (2026-10-09)

Official sources: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ and https://www.nvidia.com/en-us/geforce/graphics-cards/compare/?section=compare-16

| Gate | External published target | Vektor-1A status |
|---|---|---|
| FP32 | 21,760 CUDA cores; 2.41 GHz boost; benchmark-specific FP32 pending | 160 tiles x 128 lanes x 2 FLOP/FMA x 2.56 GHz = **104.8576 TFLOPS theoretical only**; INCONCLUSIVE |
| Matrix | 3,352 AI TOPS aggregate, not datatype-specific | Two matrix engines/tile; FP4/FP8/BF16/FP16/TF32/INT8, dense/sparse: INCONCLUSIVE |
| Memory | 32 GB GDDR7, 512-bit, 1,792 GB/s | 512-bit GDDR7 hypothesis; capacity/bandwidth unverified: INCONCLUSIVE |
| Cache | L1/L2 hierarchy needs authoritative characterization | 128 MB distributed L2 target: INCONCLUSIVE |
| Texture/raster | Equal-resolution API benchmark required | Distributed engines proposed: INCONCLUSIVE |
| Ray tracing | 318 RT TFLOPS aggregate, not equal to ray workload FPS | Distributed trace engines proposed: INCONCLUSIVE |
| Frequency | 2.41 GHz published boost | 2.56 GHz target: INCONCLUSIVE |
| Power | 575 W total graphics power | <=575 W target: INCONCLUSIVE |
| Area | Physical die area source and mapped comparison needed | <=750 mm^2 target: INCONCLUSIVE |
| Software | CUDA and supported graphics API stack | KPX ISA/compiler/runtime execution: INCONCLUSIVE |
| Reproducibility | Independent workload benchmarks required | Component-level software models only: INCONCLUSIVE |

The RTX 5090 AI TOPS and RT TFLOPS aggregate figures are **not** directly comparable with FP32 FLOP/s. No Vektor silicon, GPU benchmark, physical area, timing, or power measurements are established. Every RTX 5090-class gate remains INCONCLUSIVE.
