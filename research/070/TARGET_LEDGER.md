# Vektor-070 external target/spec ledger — 2026-10-10

Source: NVIDIA official GeForce RTX 5090 specification page, https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/ . No proprietary implementation or confidential sources.

| Dimension | RTX 5090 external reference | Vektor-1A hypothesis | Gate |
|---|---|---|---|
| FP32 | 21,760 CUDA cores, 2.41 GHz boost. Derived FMA arithmetic 104.8832 TFLOPS, **not measured sustained throughput** | 160 tiles x 128 lanes x 2 FLOP/FMA x 2.56 GHz = 104.8576 TFLOPS **projected only** | INCONCLUSIVE |
| Matrix/tensor | 5th-gen Tensor; 3,352 marketed AI TOPS, datatype/sparsity not directly comparable | 2 matrix engines/tile; no verified per-datatype rates | INCONCLUSIVE |
| Memory capacity | 32 GB GDDR7 | capacity unvalidated | INCONCLUSIVE |
| Memory bandwidth | 512-bit GDDR7; 1,792 GB/s commonly advertised, requires independent target-source verification for sustained BW | 512-bit at 28 Gb/s/pin => 1.792 TB/s arithmetic; PHY absent | INCONCLUSIVE |
| L2/cache | exact hierarchy not established from cited official product spec | 128 MB distributed L2 hypothesis | INCONCLUSIVE |
| Raster/texture | workload-dependent; no universal rate from official page | distributed raster/texture engines unbenchmarked | INCONCLUSIVE |
| Ray tracing | 4th-gen RT, 318 marketed RT TFLOPS, not an equal-workload benchmark | distributed trace engines unbenchmarked | INCONCLUSIVE |
| Clock | 2.41 GHz marketed boost | 2.56 GHz target, no mapped timing | INCONCLUSIVE |
| Power | 575 W TGP | <=575 W target; no dynamic power analysis | INCONCLUSIVE |
| Area | no directly comparable published die area established here | <=750 mm2 target; no physical synthesis | INCONCLUSIVE |
| Software | NVIDIA driver/CUDA/graphics stack | KPX compiler/ISA path incomplete | INCONCLUSIVE |

At the projected Vektor peak and projected memory BW, the first-order compute/memory balance is **58.51 FP32 FLOP/byte**. This is a *roofline threshold*, not a performance prediction. At 575 W, the projected peak implies **182.36 GFLOP/s/W**; no evidence currently supports that efficiency.

Vektor-070 validates only a small protocol component, not any 5090-class gate. Next performance-oriented discriminator after end-to-end protocol correctness: multi-tile synthetic memory/NoC utilization under realistic latency and contention.
