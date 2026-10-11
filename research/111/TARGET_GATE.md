# Vektor-111 target ledger

RTX 5090 official reference: 21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit bus, 575 W, 5th-gen tensor and 4th-gen RT cores (NVIDIA product specifications). 1792 GB/s nominal bandwidth follows from 28 Gb/s x 512 / 8, corroborated by PNY specifications. Prior whitepaper review indicates 96 MiB L2; revisit exact source revision before use.

Vektor-1A 160 tiles x 128 FP32 lanes x 2 FLOP/FMA x 2.56 GHz = 104.8576 TFLOPS projected peak, not measured. 128 MB L2, 512-bit GDDR7, 2 matrix engines/tile, graphics/RT units and KPX remain hypotheses.

5090-class gates: FP32 INCONCLUSIVE; tensor by datatype/sparsity INCONCLUSIVE; bandwidth/capacity INCONCLUSIVE; L1/L2 INCONCLUSIVE; raster/texture INCONCLUSIVE; ray tracing INCONCLUSIVE; area/frequency/power INCONCLUSIVE; software stack INCONCLUSIVE; reproducibility PARTIAL, not a full-gate PASS.

V111 validates an abstract memory-hazard model only.
