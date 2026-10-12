# Vektor-125 external RTX 5090 target envelope (2026-10-12)

Official reference: https://www.nvidia.com/en-us/geforce/graphics-cards/compare/ and https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ . NVIDIA lists 21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit bus, 3,352 AI TOPS (unspecified matching datatype/sparsity in headline), and 318 RT TFLOPS (marketing unit, not ray workload benchmark). 575 W total graphics power is listed on the official RTX 5090 product page. The 104.88 TFLOPS FP32 number is an arithmetic peak projection (21,760 x 2 x 2.41 GHz), not a sustained benchmark.

| Gate | External target | Vektor evidence / status |
|---|---|---|
| FP32 throughput | ~104.88 TFLOPS projected peak | 104.8576 TFLOPS Vektor-1A **target**, no sustained benchmark: INCONCLUSIVE |
| Matrix/tensor | 3,352 AI TOPS headline; datatype and sparsity normalization pending | two matrix engines/tile **hypothesis**, no implementation: INCONCLUSIVE |
| Memory capacity | 32 GB GDDR7 | no implemented capacity: INCONCLUSIVE |
| Memory bandwidth | 512-bit GDDR7, ~1.792 TB/s theoretical with 28 Gb/s pins | 512-bit GDDR7 **hypothesis**, no PHY/controller: INCONCLUSIVE |
| Cache hierarchy | independently verify L1/L2 sizes and latencies | 128 MB distributed L2 **hypothesis**, no physical cache: INCONCLUSIVE |
| Texture/raster | workload comparison not established | distributed engines **hypothesis**: INCONCLUSIVE |
| Ray tracing | 318 RT TFLOPS headline, must use actual workload benchmarks | no RT execution: INCONCLUSIVE |
| Frequency | 2.41 GHz advertised boost | 2.56 GHz **target**, no STA: INCONCLUSIVE |
| Power | 575 W TGP | <=575 W **target**, no power analysis: INCONCLUSIVE |
| Area | verified comparable area target pending | <=750 mm² **target**, no PPA: INCONCLUSIVE |
| Software | CUDA/graphics stack support | KPX-0 integer interpreter, V125 candidate RTL subset, no runtime: INCONCLUSIVE |
| Reproducibility | independent model and hardware verification | 224 software agreement cases; RTL simulator and synthesis pending: INCONCLUSIVE |
| Overall 5090-class | broad evidence across all gates | **INCONCLUSIVE** |

No V125 result is a GPU throughput, physical area, timing, power, or RTX 5090 equivalence measurement. Do not conflate AI TOPS, RT TFLOPS, FP32 TFLOPS, or workload throughput.
