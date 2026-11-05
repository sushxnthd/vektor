# V309: authenticated V100 memory-sector topology, conservative negative hardware screen (2026-10-30)

**Decision:** No memory-coalescer hardware mechanism qualifies. The strongest equal-resource control, an ideal fixed-address within-warp sector coalescer, already attains the exact 32-byte-sector lower bound. This is a **trace-address topology study**, not measured memory transactions, stalls, bandwidth, GPU IPC, power or an RTX 5090 claim.

## Preregistration and verification
- [Frozen protocol and timestamped, pre-outcome parser amendments](MEMORY_SECTOR_PROTOCOL_20261030.md). Legacy format-0 address cardinality was unidentifiable from active masks (one active lane had 16 address tokens in Needleman-Wunsch, while another had two in BFS). A noncontiguous format-1 mask also lacked version-verified stride semantics. All such rows were excluded before any address-sector metric was computed. Earlier failed CI runs remain visible.
- Authentic Purdue Tesla V100 Rodinia 2.0-ft SASS archive, 210 trace files, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. [Source](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz).
- [Passing hosted CI #40980975691](https://github.com/sushxnthd/vektor/actions/runs/40980975691), [raw primary + independent JSON artifact #12945075581](https://github.com/sushxnthd/vektor/actions/runs/40980975691/artifacts/12945075581). The independent redecoder imports none of the primary accounting functions and reproduced every global/per-application counter. Selftests passed 90 byte-enumeration oracle cases, six malformed primary records, and **21 independent adversarial report mutants**.
- This is **exploratory**: all eleven Rodinia families had been examined for prior V309 questions. None can serve as a prospective architecture holdout.

## Exact observed workload descriptors

| Descriptor | Count |
|---|---:|
| All active memory-operation rows | 484,259 |
| LDG/STG/ATOM/RED global-proxy rows | 240,465 |
| Unambiguously decoded global-proxy rows | **129,883 (54.0133%)** |
| Excluded ambiguous format-0 global rows | **106,728** |
| Excluded noncontiguous format-1 global rows | **3,854** |
| Decoded format-2 global rows | **0** |
| Decoded active lane references | 3,558,791 |
| Distinct requested bytes across decoded rows | 11,570,346 |
| Distinct 32-byte sectors touched (summed per instruction) | **1,096,117** |
| Distinct 64-byte regions touched | 700,019 |
| Distinct 128-byte regions touched | 384,331 |
| Perfect-packed 32-byte-sector floor (sum per instruction) | 384,265 |
| **Layout-only** excess sectors above that floor | **711,852** |
| Decoded rows with any layout packing slack | 46,644 (35.9123%) |
| 32-byte sector byte utilization on decoded subset | **32.9867%** |

**Coverage limitation:** 110,582 of 240,465 global-proxy rows (45.9867%) were excluded, and two workload families (Hotspot and SRAD-v2) had no unambiguously decoded global-proxy rows. Do not generalize 32.99% utilization to the full corpus, to all V100 memory transactions, or to Blackwell.

Exploratory per-family 32-byte sector utilization in the **decoded subset**: Nearest Neighbor 4.615%, KMeans 26.087%, Streamcluster 55.455%, Needleman-Wunsch 61.261%, Heartwall 65.557%, Backprop 66.667%, Pathfinder 80.033%, BFS 88.502%, LUD 100%. These differences are descriptive, potentially confounded by selection/coverage and opcode mix, and cannot be used as post-hoc win/no-win holdouts.

## Exact predictive negative law, with scope

For fixed lane byte addresses `a_l`, width `w`, and hypothetical sector granularity `g`, let

`S_g = | union_l { floor(b/g) : b in [a_l, a_l+w) } |`.

Any within-warp mechanism that must fetch whole aligned `g`-byte sectors and preserve **those exact addresses** must touch at least `S_g` distinct sectors. A free ideal coalescer reaches `S_g` exactly. Thus the opportunity for another **fixed-address, same-sector-granularity coalescer** to reduce distinct touched sectors relative to this baseline is **zero**, regardless of the observed byte utilization.

Let `U = |union_l [a_l,a_l+w)|` be the distinct requested byte count. The floor `ceil(U/g)` is achievable only if layout or access addresses can be rearranged into perfectly packed aligned sectors; `S_g - ceil(U/g)` is **layout-only slack**, not a GPU speedup, not an actual DRAM transaction saving, and not a hardware mechanism. Timing, memory ordering, cache reuse, occupancy and cross-warp reuse can invalidate any naive translation to throughput.

This exact negative boundary is classical set coverage, **not a novel GPU architecture law**. A genuine positive law would require a different physical mechanism with matched resources, measured counters or validated cycle simulation, and unseen workload predictions.

## Decision and next gate
- **Kill** a pure within-warp coalescer idea based solely on these fixed-address sector counts.
- Preserve the excluded-format evidence and independent checks. Do not silently fill missing addresses or infer sector counts for excluded rows.
- Acquire a separately versioned, unambiguous SASS+counter dataset or validated cycle simulation with trace semantics and matched memory-system statistics. Freeze win/no-win regimes before evaluation, and test the strongest equal-resource physical alternative. Only then select a new RTL mechanism.
- V287/V296/V297-V308 remain retired; V309 stays the sole qualification workstream in draft PR #26. Kernellum PR #119 unchanged. No RTL timing/area, electrical signoff or GPU-level improvement demonstrated.
