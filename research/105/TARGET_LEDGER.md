# Vektor-105 target ledger (checked 2026-10-11)

Source: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ (official NVIDIA product specifications).

| Dimension | External RTX 5090 target | Vektor-1A hypothesis | Gate |
|---|---|---|---|
| FP32 | 21,760 CUDA cores, 2.41 GHz boost; arithmetic peak 104.8832 TFLOP/s if one FMA/lane/cycle | 160 x 128 lanes x 2 x 2.56 GHz = 104.8576 TFLOP/s *projection* | INCONCLUSIVE |
| Tensor | Fifth-generation Tensor Cores; vendor 3352 AI TOPS without datatype-specific context in this source | Two matrix engines/tile, unverified datatype/sparsity performance | INCONCLUSIVE |
| VRAM | 32 GB GDDR7, 512-bit interface | 512-bit GDDR7 target; controller/capacity/bandwidth unverified | INCONCLUSIVE |
| Cache | Public official page does not establish detailed hierarchy | 128 MB distributed L2 target | INCONCLUSIVE |
| Graphics | Raster/texture workload performance requires real benchmarks | Distributed raster/texture engines target | INCONCLUSIVE |
| Ray | Fourth-generation RT cores; vendor 318 RT TFLOPS, not FP32-comparable | Trace acceleration target | INCONCLUSIVE |
| Power | 575 W total graphics power | <=575 W target, no physical estimate | INCONCLUSIVE |
| Frequency | 2.41 GHz reference boost | 2.56 GHz target, no timing closure | INCONCLUSIVE |
| Area | Authoritative die area not established here | <=750 mm2 target, no physical area | INCONCLUSIVE |
| Software | CUDA capability 12.0, Vulkan 1.4, OpenGL 4.6 | Original KPX ISA/compiler planned, not equivalent | INCONCLUSIVE |
| Reproducibility | Broad real workloads and PPA required | Component-level synthetic research only | INCONCLUSIVE |

The official page does not provide a verified bandwidth figure or datatype/sparsity tensor breakdown here; do not silently equate marketing metrics. No gate advanced by Vektor-105.
