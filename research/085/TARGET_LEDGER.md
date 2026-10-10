# Vektor-085 external target and 5090-class evidence ledger

Verified 2026-10-10 against NVIDIA's official [RTX 5090 specifications](https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/). External comparison targets, **not Vektor achievements**:

| Dimension | External RTX 5090 reference | Vektor-1A status |
|---|---|---|
| FP32 | 21,760 CUDA cores, 2.41 GHz advertised boost; ~104.9 TFLOPS theoretical peak from 2 FLOP/FMA | 160 ×128 FP32 lanes ×2 ×2.56 GHz = **104.8576 TFLOPS arithmetic TARGET**; sustained compute untested |
| Tensor | NVIDIA lists 3,352 AI TOPS (precision/sparsity must be matched before comparison) | Two matrix engines/tile TARGET; no datatype-specific measured rates |
| VRAM | 32 GB GDDR7, 512-bit | 512-bit GDDR7 TARGET; memory capacity/controller not validated |
| Bandwidth | ~1,792 GB/s commonly cited; pin rate not stated on the official product spec page used here | Target only; no controller/NoC bandwidth proof |
| Cache hierarchy | Official product page does not enumerate all cache sizes | 128 MB distributed L2 TARGET; no synthesized cache |
| Texture/raster | No matched workload measurements in this ledger | Distributed texture/raster/ROP TARGET; no workload evidence |
| Ray tracing | 318 RT TFLOPS advertised vendor metric; not interchangeable with general FP32 | Distributed trace engines TARGET; no matched scene benchmark |
| Clock | 2.41 GHz advertised boost | 2.56 GHz TARGET, no post-route evidence |
| Power | 575 W board power | <=575 W TARGET, no power estimate |
| Area | Not independently verified here | <=750 mm² TARGET, no process-qualified physical estimate |
| Software | CUDA 12.0 capability and graphics API support listed by NVIDIA | KPX ISA/compiler path UNTESTED on representative kernels |

**5090-class gate:** FP32, tensor (FP4/FP8/FP16/BF16, sparse/dense), memory, cache, raster/texture, ray tracing, area, frequency, power, software and full-system reproducibility: all **INCONCLUSIVE**. Vektor-085 adds only bounded software-model RF resource/correctness evidence.

Do not infer RTX 5090-class performance from the 104.8576 TFLOPS arithmetic target. No silicon or process-specific synthesis evidence exists for this architecture.
