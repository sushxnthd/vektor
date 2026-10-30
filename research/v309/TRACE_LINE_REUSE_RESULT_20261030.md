# V309: source-conditional global-load line-reuse result (2026-10-30)

**Hosted result: PASS.** [GitHub Actions #41036327864](https://github.com/sushxnthd/vektor/actions/runs/41036327864); [raw artifact #12968641262](https://github.com/sushxnthd/vektor/actions/runs/41036327864/artifacts/12968641262). [Protocol](TRACE_LINE_REUSE_PROTOCOL_20261030.md) was committed **before** implementation, at `7563219`. Analyzer `trace_line_reuse.py` committed at `1511017`; hosted workflow at `de90b5b`. All source-conditional claims remain subject to the **unverified historical tracer-producer hypothesis**.

## Authenticated full-corpus result

Source: original 2020-03-18 Tesla V100 Rodinia 2.0-ft archive, SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Exactly 210 trace files, 11 workload families, 240,465 active LDG/STG/ATOM/RED global-proxy instructions. Only LDG load-proxy rows enter the line-identity calculation.

| Measure | Source-conditional result |
|---|---:|
| Active LDG rows | 197,197 |
| Certified visible-lane address rows | **190,219 (96.4614%)** |
| Excluded format-0 hidden-lane rows | 5,881 |
| Excluded format-1 shifted-start rows | 1,097 |
| Certified format-0 rows | 67,313 |
| Certified format-1 rows | 122,906 |
| Sum of distinct 128-byte lines touched **per certified instruction** R | 530,930 |
| Sum of unique line identities **within each trace file** U | 159,345 |
| Duplicate line references in certified subset D=R-U | **371,585 (69.9876% of R)** |

The denominator for 69.9876% is **only the certified load-instruction line references**, not full workload memory requests, L1/L2 misses or DRAM transactions. Unique addresses are counted separately per trace file, never merged across kernels.

### Application variation (retrospective, not unseen)

| Workload | LDG rows | Certified | R | U | Duplicate fraction |
|---|---:|---:|---:|---:|---:|
| Backprop | 18,437 | 18,437 | 27,013 | 6,790 | 74.87% |
| BFS | 21,917 | 15,955 | 44,090 | 4,029 | 90.86% |
| Heartwall | 12,648 | 12,648 | 19,282 | 2,974 | 84.58% |
| Hotspot | 5,474 | 5,474 | 12,604 | 406 | 96.78% |
| KMeans | 442 | 442 | 13,600 | 425 | 96.88% |
| LUD | 688 | 544 | 880 | 376 | 57.27% |
| Nearest Neighbor | 30,016 | 30,016 | 202,512 | 22,972 | 88.66% |
| Needleman-Wunsch | 1,216 | 1,152 | 2,624 | 2,575 | **1.87%** |
| Pathfinder | 759 | 664 | 1,315 | 717 | 45.48% |
| SRAD-v2 | 14,080 | 14,080 | 24,704 | 7,184 | 70.92% |
| Streamcluster | 91,520 | 90,807 | 182,306 | 110,897 | 39.17% |

**Interpretation:** A no-reuse line-fill proxy is severely misleading on some certified load subsequences. The strong variation between Needleman-Wunsch and Hotspot illustrates why sector-only or read-counter-only throughput inference must be killed. But neither high duplicate fraction nor low unique-line count establishes any GPU cache hit rate or hardware optimization opportunity: the line identities are only addresses, without actual cache scheduling, coherence, prefetch, physical mapping or measured traffic.

## Frozen controls and independent checks

Hosted audit passed 36 independent byte-level line-footprint comparisons, two preregistered synthetic extremes (hot reuse: R=256,U=4; cold stream: R=256,U=256), five malformed/overflow refusal tests, source-mask ambiguity refusals, file-domain separation and independent per-file/per-application conservation checks. The source hypothesis is not independently authenticated by these tests.

**Positive law scope:** D=R-U and rho=D/R are exact elementary set identities for the certified subset. They are **not a novel architectural boundary law** and must not be presented as throughput gain. The equal-resource ideal infinite-capacity, cold, demand-only cache already has U compulsory line fills; a fixed-address coalescer cannot improve its unique-line floor.

## New matched-evidence acquisition lead

The upstream [Accel-Sim hardware-data acquisition script at commit `7ba54ded`](https://github.com/accel-sim/accel-sim-framework/blob/7ba54ded60c4ba0083410c37d22d719166acd6dc/util/hw_stats/get_hw_data.sh) explicitly references a downloadable **`volta-tesla-v100.tgz`** hardware-profiler archive, alongside `quadro.v100.cycle.tgz`. This is a concrete candidate for matched benchmark-family and GPU-generation counters, but **the archive has not yet been downloaded or inspected**, and no same-run pairing to the 2020-03-18 SASS trace corpus is established. Next: bounded metadata acquisition, compare exact workload/configuration/kernel identities, verify counter semantics, and only then attempt calibrated cycle simulation. If the archive does not match, report that negative result and do not infer traffic.

## Research decision

**No hardware mechanism promoted.** The V309 draft remains a qualification gate; retired V287/V296 mechanisms stay retired. A world-class physical architecture result still requires same-run or independently validated matched trace/counter/cycle evidence, one implementable mechanism, matched-resource RTL synthesis and timing, electrical checks, power/area sensitivity, prospective workloads, prior-art audit and a defensible predictive boundary law. Kernellum PR #119 unchanged. No RTX-5090-equivalence claim.
