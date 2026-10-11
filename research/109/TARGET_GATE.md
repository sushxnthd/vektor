# Vektor-109 external target ledger

NVIDIA RTX 5090 external targets (official GeForce specifications, rechecked 2026-10-11): 21,760 CUDA cores, 32 GB GDDR7, 512-bit memory bus, 2.41 GHz boost, 575 W TGP, fifth-generation tensor, fourth-generation RT. 28 Gbps x 512/8 = 1,792 GB/s theoretical interface bandwidth. Prior architecture whitepaper identifies 96 MiB L2; Vektor-1A's 128 MiB L2 remains a tradeoff to evaluate.

Vektor-1A projections: 160 tiles x 128 FP32 lanes x 2 operations/FMA x 2.56 GHz = 104.86 TFLOPS *theoretical*; no measured hardware throughput.

Gates: FP32 INCONCLUSIVE; matrix datatype/sparsity INCONCLUSIVE; memory capacity/bandwidth INCONCLUSIVE; cache INCONCLUSIVE; texture/raster INCONCLUSIVE; ray INCONCLUSIVE; frequency INCONCLUSIVE; area INCONCLUSIVE; power INCONCLUSIVE; compiler/ISA INCONCLUSIVE. V109 is a component-level validation correction, not a GPU capability advance.
