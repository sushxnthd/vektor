# Vektor-052 target and evidence ledger (2026-10-09)

External reference: NVIDIA GeForce RTX 5090 Founders Edition, https://www.nvidia.com/en-gb/geforce/graphics-cards/50-series/rtx-5090/

| Capability | RTX 5090 external reference | Vektor-1A hypothesis | Evidence gate |
| --- | --- | --- | --- |
| FP32 peak | 21,760 CUDA cores x 2 FLOP/FMA x 2.41 GHz = 104.8832 TFLOP/s theoretical | 160 tiles x 128 FP32 lanes x 2 x 2.56 GHz = 104.8576 TFLOP/s projected | INCONCLUSIVE |
| Tensor/matrix | 5th-generation Tensor; NVIDIA lists 3,352 AI TOPS without comparable datatype/sparsity context on product page | Two matrix engines per tile; datatype-specific rates not validated | INCONCLUSIVE |
| VRAM | 32 GB GDDR7 | 512-bit GDDR7 interface target; capacity to specify | INCONCLUSIVE |
| Memory bandwidth | Must verify GDDR7 effective rate against primary technical source | No PHY/controller RTL, bandwidth unverified | INCONCLUSIVE |
| Cache | Vendor public product page does not give L2/L1 topology | 128 MB distributed L2 target | INCONCLUSIVE |
| Raster/texture | Must benchmark real workloads and graphics API | Distributed raster/texture targets only | INCONCLUSIVE |
| Ray tracing | NVIDIA lists 4th-gen RT and 318 RT TFLOPS (vendor metric, not equivalent to FP32) | Distributed trace engines target only | INCONCLUSIVE |
| Clock | 2.41 GHz boost (Founders Edition) | 2.56 GHz aspirational | INCONCLUSIVE |
| Power | 575 W total graphics power | <=575 W aspirational | INCONCLUSIVE |
| Area | Public product specification lacks die area | <=750 mm^2 aspirational | INCONCLUSIVE |
| Software | CUDA capability 12.0, Vulkan 1.4, OpenGL 4.6, DX12 Ultimate | KPX ISA/compiler plan, no parity | INCONCLUSIVE |

Do not interpret arithmetic peak similarity as performance equivalence. Generic Yosys logic-cell counts cannot establish power, physical area, or 2.56 GHz. This ledger records explicit gaps and does not grant any 5090-class PASS.
