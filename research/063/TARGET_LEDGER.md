# Vektor external target ledger — checked 2026-10-09

Authoritative source: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

NVIDIA GeForce RTX 5090: 21,760 CUDA cores; 2.41 GHz boost clock; 32 GB GDDR7; 512-bit interface; 575 W total graphics power; fifth-generation tensor cores (3,352 marketing AI TOPS); fourth-generation RT cores (318 marketing RT TFLOPS). Marketing TOPS and RT figures are not comparable without datatype, sparsity, and workload definitions.

Vektor-1A hypothesis: 160 tiles x 128 FP32 lanes x 2 FMA FLOPs x 2.56 GHz = 104.8576 TFLOPS **arithmetic projection only**. 128 MB L2, 512-bit GDDR7, <=575 W, <=750 mm2, KPX software stack remain targets.

5090-class gates: FP32 INCONCLUSIVE; tensor by datatype and sparsity INCONCLUSIVE; memory capacity/bandwidth INCONCLUSIVE; cache INCONCLUSIVE; texture/raster INCONCLUSIVE; ray INCONCLUSIVE; area INCONCLUSIVE; clock INCONCLUSIVE; power INCONCLUSIVE; software stack INCONCLUSIVE; full-chip reproducibility INCONCLUSIVE. Component software-model validation does not pass the chip-level gate.
