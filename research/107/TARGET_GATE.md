# Vektor-107 external target gate (2026-10-11)

NVIDIA official RTX 5090: 21,760 CUDA cores, 32 GB GDDR7, 512-bit, 1,792 GB/s, 2.41 GHz boost, 680 5th-gen tensor cores, 170 4th-gen RT cores. Published AI TOPS is not FP32 throughput. L2 96 MiB as documented in 106 whitepaper ledger.

Sources:
https://www.nvidia.com/en-sg/geforce/graphics-cards/50-series/
https://www.nvidia.com/ja-jp/geforce/news/rtx-50-series-graphics-cards-gpu-laptop-announcements/

Vektor-1A 160x128 lanes x 2 FP32 operations/FMA x 2.56GHz = 104.8576 TFLOP/s arithmetic PROJECTION only. 128 MiB L2, 512-bit GDDR7, 2.56 GHz, <=575W and <=750 mm2 remain unvalidated hypotheses.

5090-class gate status:
- FP32 sustained: INCONCLUSIVE
- Tensor datatype/sparsity: INCONCLUSIVE
- Memory capacity/bandwidth/cache: INCONCLUSIVE
- Texture/raster: INCONCLUSIVE
- Ray tracing: INCONCLUSIVE
- Area/frequency/power: INCONCLUSIVE
- KPX software: INCONCLUSIVE
- Reproducible end-to-end comparison: INCONCLUSIVE

V107 corrects a host-side cache-stage accounting proxy, not a 5090-class performance gate.
