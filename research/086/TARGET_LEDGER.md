# Vektor-086 target and 5090-class gate ledger

Rechecked 2026-10-10 against [NVIDIA official GeForce RTX 5090 specifications](https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/). This is an **external target**, not a Vektor capability statement.

| Dimension | External RTX 5090 published target | Vektor-1A hypothesis | Evidence / gate |
|---|---|---|---|
| FP32 | 21,760 CUDA cores; 2.41 GHz boost; 104.88 TFLOPS arithmetic peak if one FMA/lane/cycle | 160 tiles x 128 FP32 lanes x 2 x 2.56 GHz = 104.8576 TFLOPS **projection** | INCONCLUSIVE; no validated FP32 execution at target frequency |
| Matrix/tensor | NVIDIA advertises 3,352 AI TOPS, fifth-generation tensor cores; datatype, sparsity and test method must be resolved before comparisons | Two matrix engines/tile | INCONCLUSIVE for FP4/FP8/FP16/BF16/TF32, sparse/dense |
| Memory | 32 GB GDDR7, 512-bit bus (official); effective bandwidth requires independently verified GDDR7 data rate | 512-bit GDDR7; capacity and controllers unspecified | INCONCLUSIVE |
| Cache | Public product page does not specify detailed L1/L2 capacity or cache behavior | 128 MB distributed L2 target | INCONCLUSIVE |
| Texture/raster | No official comparable workload-throughput figure in product spec table | Distributed raster/texture engines proposed | INCONCLUSIVE |
| Ray | NVIDIA advertises 318 RT TFLOPS (vendor-defined), fourth-gen RT cores | Distributed trace engines proposed | INCONCLUSIVE; require open RT workloads |
| Frequency | 2.41 GHz boost (official, not a sustained guarantee) | 2.56 GHz target | INCONCLUSIVE; no P&R/timing closure |
| Power | 575 W total graphics power (official) | <=575 W target | INCONCLUSIVE; no power analysis |
| Area | Die area not specified on official product page | <=750 mm^2 target | INCONCLUSIVE; no mapped PPA |
| Software | CUDA, Vulkan 1.4, OpenGL 4.6, DX12 Ultimate supported (official) | Original KPX ISA/compiler planned | INCONCLUSIVE; no production runtime compatibility |

**Vektor-086 progress:** narrow synthesizable writeback-calendar controller (694 generic Yosys cells; 16 DFF default; 6,144 independently checked RTL cycles). This advances a component-level implementation gate, **not** any RTX 5090-class equivalence gate. Generic cell counts cannot be converted to ASIC area or power without library mapping and physical design.

**Prior art:** [Vortex open GPU](https://vortexgpgpu.github.io/index.html) demonstrates an open synthesizable GPU plus compiler/runtime; compare software-stack coverage before any Vektor originality or competitiveness claims.
