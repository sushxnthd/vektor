# Vektor-105 — Coalescing / divergence interaction (2026-10-11)

**Evidence:** deterministic synthetic cycle simulation; no physical hardware, no calibrated GPU timing, no RTL synthesis, no GPU performance claim.

## Mechanism and controlled outcome

Eight Wave32 warps, balanced two-path divergence, 16 instructions, 128-byte memory sectors, one memory-sector request serviced per model cycle. Three policies: masked warp/path groups, path-only cross-warp DWF, and **offline sector-local** grouping (perfect future-address knowledge). Equal useful lane work and RF/issue/memory resources.

| Layout | Policy | Sectors per instruction | Model cycles |
|---|---|---:|---:|
| Shared sectors across warps | Masked | 64 | 1026 |
| Shared sectors across warps | DWF | 32 | 518 |
| Shared sectors across warps | Sector-local | **8** | **138** |
| Warp-contiguous | Masked | 16 | **258** |
| Warp-contiguous | DWF | 16 | 262 |
| Warp-contiguous | Sector-local | 16 | 262 |

The sector-local policy improves the **synthetic** memory-bound shared-sector case, but is not hardware deployable as specified. A separate dependency-free `sector_incidence.py` reproduces structural counts, not cycle timing.

## Search, holdout and independent checks

| Partition | Cases | LOCAL faster than DWF | LOCAL slower than DWF | LOCAL saves sectors | Saves sectors yet slower |
|---|---:|---:|---:|---:|---:|
| Discovery | 96 | 22 | 23 | 42 | 18 |
| Surprise | 12 | 3 | 1 | 5 | 1 |
| Holdout | 48 | 8 | 7 | 11 | 2 |
| Supplement | 6 | 1 | 1 | 1 | 0 |

The six supplementary probes were added after initial results to correct the exploratory-budget denominator: 18/162 = 11.11%. This is explicitly not retrospective preregistration. An independent C++ implementation reproduced **1368/1368** group, sector and migration counts, not timing cycles. Eight directed Python tests passed locally.

## Anomaly and negative controls

Discovery case 19: sector requests 385 -> 110, cycles **103 -> 112**, cache hits 728 -> 248 and migration 9 -> 94. Holdout case 17: sector requests 240 -> 120, cycles **178 -> 188**. Thus, memory-sector savings do not imply speedups when RF, cache, residency and migration costs intervene. On warp-contiguous loads the locality policy gives no coalescing gain.

The incidence bound `T >= sum_{path,sector} ceil(active_lanes(path,sector)/32)` is elementary counting and is not claimed as novel. DWF and coalescing are established prior art.

## Provenance and limitations

The full evidence package contains unchanged Vektor-103 synthetic cycle model, Vektor-105 harness, preregistration and amendment, 162 JSON cases, C++ independent sector reference, tests, and SHA256 manifest. The GitHub branch includes the compact structural reproducer and summary, **not** the full timing suite. Offline packing uses future addresses and assumes legal cross-warp regrouping. Barriers, atomics, shuffles, PC equality, lane remapping, MSHRs, real workloads, physical PPA are unverified.

**Single next decisive action:** implement a compiler trace legality contract and an independently timed memory scheduler on real Vortex kernels, with no perfect future-address oracle. No RTX 5090-class evidence gate advanced.
