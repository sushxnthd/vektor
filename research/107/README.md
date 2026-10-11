# Vektor-107: cache-stage coalescing discrimination

Evidence: deterministic host-side simulation, not GPU timing or real Vortex traces (2026-10-11).

The Vektor-106 128-byte grouping proxy must not be labeled an NVIDIA 32-byte sector count. In a controlled two-warp SGEMM expression replay, regrouping reduces 128-byte groups from 88 to 52 (40.91%), but 32-byte sector requests only from 88 to 72 (18.18%). A cold fully associative 256-sector read cache yields 20 misses for both policies despite 80 versus 64 read-sector requests. No DRAM-read speedup is established.

In a 96-case paired post-discovery confirmation, 0 cache-miss regressions occurred under step-major issue order versus 5 under group-major. The primary 128 discovery, 64 holdout, and 24 minimally guided cases are preserved in the reproducibility package.

World model: KNOWN 32-byte correction and compulsory-miss equality; BELIEVED cache-aware gating could help; CONFLICTING sector savings with no miss savings; FALSIFIED guaranteed off-chip savings; ANOMALOUS finite-cache regressions; UNTESTED GPU timing, migration, PPA.

Next: instrument Vortex SimX LSU traces and test legal regrouping under equal resources.

References:
https://developer.nvidia.com/blog/unlock-gpu-performance-global-memory-access-in-cuda/
https://github.com/vortexgpgpu/vortex
