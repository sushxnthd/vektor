# Vektor-106 prior-art and architecture decision

Dynamic warp formation, warp regrouping, memory coalescing and compiler-guided
scheduling are established research areas. Vortex is a full-stack open
RISC-V GPU baseline: https://github.com/vortexgpgpu/vortex

The current effect is a bounded source-derived accounting law, NOT a new
general scheduling theorem, independently demonstrated GPU performance, or
novel hardware. Source expressions are from pinned Vortex revision
7fe19369587c087f902c3e2bc2add612aa910a95.

Vektor-1A remains a design hypothesis: 160 active V-Tiles, Wave32,
128 FP32 lanes/tile, 2.56GHz target, 2 matrix engines/tile,
128MiB distributed L2, 512-bit GDDR7, hierarchical RF,
dynamic cohort scheduling, distributed raster/texture/trace, hierarchical
NoC and original KPX ISA/compiler path.

Do NOT promote persistent row grouping to RTL until actual Vortex/KPX
execution traces, memory-model legality, migration/RF/NoC timing and equal
hardware-resource comparison support it. Masked SIMT remains baseline.
