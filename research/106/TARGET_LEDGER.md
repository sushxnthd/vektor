# RTX 5090 external target ledger (NVIDIA, reverified 2026-10-11)

Source: https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf
Appendix A Table 3, pages 46-48. These are NVIDIA reference metrics,
not Vektor measurements. Slash = dense / sparsity-enhanced.

- FP32 non-tensor: 104.8 TFLOPS; 21,760 CUDA cores; 2.407 GHz boost.
- FP4 tensor FP32 accum: 1,676 / 3,352 AI TOPS.
- FP8 tensor FP16 accum: 838 / 1,676 TFLOPS.
- FP8 tensor FP32 accum: 419 / 838 TFLOPS.
- FP16 tensor FP16 accum: 419 / 838 TFLOPS.
- FP16/BF16 tensor FP32 accum: 209.5 / 419 TFLOPS.
- TF32 tensor: 104.8 / 209.5 TFLOPS.
- INT8 tensor: 838 / 1,676 TOPS.
- Memory: 32GB GDDR7, 512-bit, 28Gbps, 1,792GB/s peak.
- Cache: 96MiB L2, 21,760KiB aggregate L1/shared,
  43,520KiB aggregate RF.
- Raster: 176 ROPs, 423.6 Gpixel/s published.
- Texture: 680 units, 1,636.8 Gtexel/s published.
- Ray: 170 RT cores, 317.5 vendor RT TFLOPS.
- Physical: 750mm2 die, 575W TGP.
- Software: CUDA capability 12.0; Vulkan 1.4; OpenGL 4.6; DX12 Ultimate.

Vektor-1A projected FP32 arithmetic 160*128*2*2.56 = 104.8576 TFLOPS,
not measured. Its 128MiB L2 target exceeds the 5090 96MiB published
capacity; no area/power tradeoff established. Its 2.56GHz target is not
clock closure. ALL RTX 5090-class gates INCONCLUSIVE.
