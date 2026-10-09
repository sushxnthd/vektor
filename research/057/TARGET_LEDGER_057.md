# RTX 5090 external envelope (checked 2026-10-09)

Source: NVIDIA official GeForce RTX 5090 specifications at https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ and NVIDIA regional comparison at https://www.nvidia.com/en-me/geforce/graphics-cards/50-series/rtx-5090/. NVIDIA board-partner memory spec: https://www.pny.com/geforce-rtx-5090-models?isCommercial=true&sku=VCG509032TFXPB1.

| Capability | External reference | Vektor-1A evidence / gate |
|---|---|---|
| FP32 | 21,760 cores, 2.41 GHz boost; arithmetic 104.88 TFLOPS assuming one FMA/cycle/lane | 160 x 128 x 2 x 2.56 GHz = 104.8576 TFLOPS **projection only** / INCONCLUSIVE |
| Tensor | 5th-gen cores, NVIDIA 3,352 AI TOPS marketing number; datatype/sparsity not established here | 2 engines/tile hypothesis; per-datatype throughput UNTESTED |
| Memory | 32 GB GDDR7, 512-bit, 1,792 GB/s board-spec | 512-bit GDDR7 target; no controller/PHY / INCONCLUSIVE |
| Cache | Full hierarchy not specified on cited consumer page | 128 MB distributed L2 hypothesis / INCONCLUSIVE |
| Texture/raster | No workload-throughput comparison | distributed engines hypothesis / INCONCLUSIVE |
| Ray tracing | 4th-gen RT, 318 RT TFLOPS marketing metric | no validated ray workloads / INCONCLUSIVE |
| Frequency/area/power | 2.41 GHz boost, 575 W graphics power; comparable die area not verified | 2.56 GHz, <=750 mm2, <=575 W aspirations / INCONCLUSIVE |
| Software | CUDA capability 12.0, DX12 Ultimate, Vulkan 1.4, OpenGL 4.6 | KPX/compiler incomplete / INCONCLUSIVE |

Peak arithmetic matching is not an equivalence gate. 057 only concerns bounded RF return arbitration.
