# Vektor external 5090 target ledger (checked 2026-10-11)
Official NVIDIA: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/
Official AIB bandwidth: https://www.pny.com/geforce-rtx-5090-models?isCommercial=true&sku=VCG509032TFXPB1

| Metric | External target | Vektor-1A status |
|---|---|---|
| FP32 | 21,760 CUDA cores, 2.41 GHz boost; 104.88 TFLOPS arithmetic if 2 FLOP/FMA/core/cycle | 160 tiles x 128 lanes x 2 x 2.56 GHz = 104.8576 TFLOPS arithmetic only |
| Matrix/tensor | NVIDIA 3,352 AI TOPS marketing, datatype/sparsity qualification needed | two engines/tile hypothesis, no measured datatype rates |
| Memory | 32 GB GDDR7, 512-bit, 1,792 GB/s nominal from 28 Gb/s pins | 512-bit GDDR7 target; no PHY/controller/real bandwidth |
| Cache | official spec page does not provide L2 size | 128 MB distributed L2 hypothesis |
| Texture/raster | no comparable Vektor benchmark | INCONCLUSIVE |
| Ray | NVIDIA advertises 318 RT TFLOPS; no comparable workloads | INCONCLUSIVE |
| Power | 575 W total graphics power | <=575 W budget, unvalidated |
| Frequency | 2.41 GHz boost | 2.56 GHz target, no timing closure |
| Area | not independently verified here | <=750 mm² target, no physical estimate |
| Software | NVIDIA commercial CUDA/graphics stack | KPX compiler/ISA path unvalidated |

All RTX 5090-class gates remain INCONCLUSIVE. Arithmetic FLOPS projections are not demonstrated GPU performance. No gate advances from Vektor-094.
