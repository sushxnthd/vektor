# V149 exact prior-art correction and architecture pivot (2026-10-13)

## Directly relevant public prior art

1. Shuqing Zhao, "Formally Verified Synthesizable Floating-Point Data Types in ARCH HDL", arXiv:2607.23715 (2026-07-26), https://arxiv.org/abs/2607.23715. This preprint reports an end-to-end IEEE-754 binary32 FMA with a bounded **98-bit** guard/round/sticky datapath, machine-checked equivalence to an exact-wide reference, and an open Nangate45 Yosys/OpenSTA pipeline study. The reported seven-stage 268 MHz point is technology/flow-specific, not comparable to Vektor's target frequency without common mapping. Independent reproduction is pending.
2. Tachyum-Open-Source/fma-rtl, https://github.com/Tachyum-Open-Source/fma-rtl, an Apache-2.0 public SIMD fused multiply-add implementation with binary32 lanes and IEEE flags. Source review, license audit and independent test reproduction are pending.
3. vortexgpgpu/vortex, https://github.com/vortexgpgpu/vortex, a public GPU stack with FP32 FMA unit and workload/compiler context. Must be used as a GPU architecture/software baseline rather than only a toy microbenchmark.
4. dawsonjon/fpu, https://github.com/dawsonjon/fpu, public IEEE-754 arithmetic primitives and extensive differential tests. It is not by itself a complete fused FMA baseline.

## What this corrects

V149's 49-bit cancellation-only packer is a valid bounded subsystem experiment but **not a novel full-FMA mechanism** and **not a competitive general FP32 execution solution**. Existing public work already addresses bounded full-FMA arithmetic and pipelining with stronger correctness arguments. The frozen workload probe found CLOSE eligibility 0% in same-sign vector FMA and 12.72% in synthetic GEMM fragments.

## Required next equal-budget test

Replicate one open full-FMA implementation in a controlled Wave32 adapter, preserve its license and rounding contract, and compare with Vektor's eventual general FMA using the same lane count, RF ports, elastic latency and mapped library. Keep V149 CLOSE only as an optional fast path if its additional area/timing/energy cost is justified by real workload coverage.

Do not use the paper's Nangate45 frequency as a Vektor frequency measurement, and do not call a separate CLOSE datapath a scientific breakthrough.
