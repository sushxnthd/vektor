# External RTX 5090 targets (2026-10-10)

Source: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

Official reference: 21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit bus, 575 W. NVIDIA launch article reports 1,792 GB/s bandwidth and markets 3,352 AI TOPS; exact tensor datatype/sparsity comparison is not established here.

Derived FP32 peak arithmetic: 21,760 x 2 x 2.41 GHz = 104.88 TFLOPS. Vektor-1A projected: 160 x 128 x 2 x 2.56 GHz = 104.8576 TFLOPS. Neither demonstrates Vektor performance.

Vektor's 128 MB L2, matrix engines, 512-bit GDDR7, 2.56 GHz, graphics/ray engines, power/area targets and KPX software remain unvalidated. All RTX 5090-class gates: INCONCLUSIVE.
