# Vektor-1A hypothesis and Vektor-105 decision

Baseline design targets, not implemented GPU: 160 active V-Tiles, Wave32, 128 FP32 lanes/tile, 2.56 GHz, two matrix engines/tile, 128 MB distributed L2, 512-bit GDDR7, hierarchical register storage, dynamic cohort scheduling, distributed raster/texture/trace engines, hierarchical NoC, KPX open ISA/compiler.

Vektor-105: synthetic shared-sector gather, same eight issued groups, path-only grouping requires 32 sector incidences/instruction while offline sector-local grouping requires eight. For warp-contiguous accesses, both require 16. In other synthetic cases locality grouping loses cycles despite reducing sectors due to register/cache/migration pressure. Perfect future-address knowledge is not available to a real scheduler.

Do not promote this oracle into RTL. Retain competing masked SIMT, path-only DWF, RF/issue-aware, residency-aware, locality-aware, compiler-assisted and NoC-aware hypotheses. The first implementation gate is a legal compiler trace with same-PC, barrier/atomic/shuffle restrictions and realistic address hints; then independent cycle simulation and equal-resource synthesis.

Prior art: https://github.com/vortexgpgpu/vortex and Fung et al., Dynamic Warp Formation and Scheduling for Efficient GPU Control Flow (MICRO 2007). No novelty claim from standard memory coalescing or information theory.
