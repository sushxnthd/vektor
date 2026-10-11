# Vektor-106 world-model delta and external targets

KNOWN: 112/112 bounded aligned SGEMM sector-law predictions; 16 surprise
probes with 14 deviations; host-side replay only.
BELIEVED: long-lived cohorts might amortize migration in some regimes.
CONFLICTING: sector saving versus 1,110/1,890 non-overlap proxy regressions.
FALSIFIED: fewer sectors always means lower execution cost; law holds at
arbitrary pitch/sector size.
ANOMALOUS: surprise residual down to -102 sector requests.
UNTESTED: real Vortex/KPX traces, legal cross-warp scheduling, cycle timing,
RTL, formal proof, synthesis, frequency, power, graphics and ray workloads.
NEXT: independent Vortex simx per-PC/per-lane trace instrumentation.

RTX 5090 authoritative NVIDIA whitepaper:
https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf
Published external targets: 104.8 FP32 TFLOPS; 32GB GDDR7; 1,792GB/s;
96MiB L2; 170 SMs; 176 ROPs; 680 texture units; 575W; 750mm2;
2.407GHz boost. Matrix dense/sparse targets:
FP4 1,676/3,352; FP8 FP16 accum 838/1,676;
FP8 FP32 accum 419/838; FP16 FP32 accum 209.5/419;
TF32 104.8/209.5; INT8 838/1,676 (TOPS where applicable).
Vektor-1A 128MiB L2 and 2.56GHz are design targets, not 5090 specs.
All full-GPU capability gates remain INCONCLUSIVE.
