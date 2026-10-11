# Vektor-101 prior-art and baseline audit (2026-10-11)

**Not a novelty claim.** Elastic FIFOs, credit accounting, held ready/valid,
round-robin arbitration, exactly-once completion, cancellation precedence and
tag-generation semantics are longstanding hardware protocol mechanisms.

The strongest publicly accessible integrated GPU baseline identified for the
next GPU-level gate is the open-source **Vortex GPGPU** project:
https://github.com/vortexgpgpu/vortex (Apache-2.0).
Its current public documentation describes a configurable SIMT GPU with RTL,
software simulation, compiler/runtime, OpenCL/Vulkan/HIP support, raster,
texture, ray traversal, tensor and cache-hierarchy blocks. Those documented
capabilities are not independently remeasured here. Vektor should compare
kernel correctness, compiler coverage, simulated utilization, and RTL
resource/timing cost against pinned Vortex configurations rather than treat
an isolated return controller as evidence of an end-to-end GPU.

Follow-up reproducible baseline: pin a Vortex commit, build its simulator on
a free CI runner, run deterministic vector-add, reduction, SGEMM and
divergent-control microbenchmarks, and report instruction and cycle counts
with exact configuration and source hash. Compare *capability and mechanism*,
not high-end silicon performance, until a technology-matched PPA flow exists.

Vektor KPX remains an unvalidated compiler/ISA hypothesis. NVIDIA
proprietary RTL, leaks and confidential artifacts are excluded.
