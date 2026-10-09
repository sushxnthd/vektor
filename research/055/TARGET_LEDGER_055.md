# Vektor-055 RTX 5090 external target ledger — 2026-10-09

Official NVIDIA RTX 5090 page: https://www.nvidia.com/en-gb/geforce/graphics-cards/50-series/rtx-5090/

**External reference:** 21,760 CUDA cores; 2.41 GHz advertised boost; 32 GB GDDR7; 512-bit memory bus; 1,792 GB/s advertised bandwidth; 575 W total graphics power; advertised 3,352 AI TOPS and 318 RT TFLOPS. AI TOPS and RT TFLOPS are not interchangeable with datatype-resolved tensor FLOPS or ray workload performance.

| Gate | Vektor-1A hypothesis | Evidence status |
|---|---|---|
| FP32 | 160 tiles × 128 lanes × 2.56 GHz × 2 ops/clock = 104.8576 TFLOPS **arithmetic projection** | INCONCLUSIVE |
| Tensor by datatype and sparsity | Two matrix engines/tile, unvalidated | INCONCLUSIVE |
| Memory bandwidth and capacity | 512-bit GDDR7 target, capacity unverified | INCONCLUSIVE |
| Cache hierarchy | 128 MB distributed L2 target, L1 unverified | INCONCLUSIVE |
| Texture/raster | Distributed engines proposed | INCONCLUSIVE |
| Ray workloads | Distributed trace engines proposed | INCONCLUSIVE |
| Area, frequency, power | <=750 mm², 2.56 GHz, <=575 W **targets only** | INCONCLUSIVE |
| KPX ISA/compiler and software | Proposed open stack, no broad executable conformance | INCONCLUSIVE |

Official NVIDIA cache capacities, detailed datatype/sparsity tensor rates, and die-area comparators remain to be verified from suitable sources. This experiment changes no 5090-class gate. A peak-FP32 arithmetic match is insufficient.
