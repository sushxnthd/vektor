# V309: finite-capacity LRU replay of certified historical V100 LDG traces (2026-10-30)

**Hosted PASS:** [GitHub Actions #41048898951](https://github.com/sushxnthd/vektor/actions/runs/41048898951) at commit `08c837a931bf091737e3dc98397370698ed1d551`. [Raw evidence artifact #12973063459](https://github.com/sushxnthd/vektor/actions/runs/41048898951/artifacts/12973063459). The [frozen protocol](CACHE_CAPACITY_REPLAY_PROTOCOL_20261030.md) was committed first (`767fa06`), followed by [executable replay and independent oracle](cache_capacity_replay.py) (`9575d83`) and CI (`08c837a`). These results are **not measured GPU cache misses, DRAM reads or performance**.

## Authenticated source and exact conservation

Historical 2020-03-18 Tesla V100 Rodinia 2.0-ft archive SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`; 210 trace files, 11 workload families, 240,465 global-proxy rows, 197,197 active LDG rows, 190,219 source-conditionally certified LDG rows, **R=530,930** 128-byte line references and **U=159,345** per-file unique line identities. The 6,978 ambiguous LDG rows are excluded; other memory operations are not modeled. Exact per-file and per-app conservation passed. The historical tracer-producer hypothesis remains **unverified**.

## Full-corpus conditional replay sensitivity

Each file starts cold; certified line IDs are replayed in trace order with ascending line-ID order within each instruction. Two explicit missing-row treatments: SKIP (retain cache state) and FLUSH (clear cache at each uncertified LDG). Fully associative LRU, hypothetical 128-byte lines. The infinite-capacity certified-only baseline is U=159,345 fills.

| Capacity (128-byte lines) | SKIP replay misses | FLUSH replay misses | SKIP misses above U | SKIP reduction vs no-reuse R |
|---:|---:|---:|---:|---:|
| 1 | 525,907 | 525,924 | 230.04% | 0.95% |
| 4 | 500,441 | 500,726 | 214.06% | 5.74% |
| 16 | 228,308 | 236,897 | 43.28% | 57.00% |
| 64 | **175,042** | **202,939** | **9.85%** | **67.03%** |
| 256 | 161,832 | 192,212 | 1.56% | 69.52% |
| 1024 | 160,110 | 191,482 | 0.48% | 69.84% |
| infinite | 159,345 | 159,345 (no unknown-row resets) | 0% | 69.99% |

The infinite-capacity FLUSH entry is **not** a finite-cache limit of the FLUSH policy; the tabulated U is the separate ideal no-reset baseline. The finite-capacity FLUSH sequence can remain above U even for very large caches because unknown rows reset the model cache. Thus the previously reported 69.99% duplicate-address fraction is **not a finite-cache hit rate**. At four lines, the ordered SKIP replay eliminates only 5.74% of certified line requests; at 64 lines it eliminates 67.03%. Neither number is a measured V100 cache result.

### Workload and missing-address sensitivity at 64 lines

| Family | R | U | SKIP misses | FLUSH misses |
|---|---:|---:|---:|---:|
| Backprop | 27,013 | 6,790 | 6,790 | 6,790 |
| BFS | 44,090 | 4,029 | **4,281** | **31,122** |
| Heartwall | 19,282 | 2,974 | 6,421 | 6,421 |
| Hotspot | 12,604 | 406 | 406 | 406 |
| KMeans | 13,600 | 425 | 425 | 425 |
| LUD | 880 | 376 | 436 | 492 |
| Nearest Neighbor | 202,512 | 22,972 | 22,972 | 22,972 |
| Needleman-Wunsch | 2,624 | 2,575 | 2,575 | 2,624 |
| Pathfinder | 1,315 | 717 | 717 | 743 |
| SRAD-v2 | 24,704 | 7,184 | 14,956 | 14,956 |
| Streamcluster | 182,306 | 110,897 | 115,063 | 115,988 |

**Important falsification:** BFS changes from 4,281 to 31,122 modeled misses at the same 64-line capacity solely by changing the declared handling of ambiguous LDG rows. This shows that an apparently precise cache-traffic estimate is not identifiable without the missing address events and a validated memory-order model. These two replay policies **do not bound physical GPU cache misses**; excluded events can also bring useful lines, alter scheduling or cause additional evictions.

## Independent checks and frozen predictions

The independent list-based LRU reference matched the optimized OrderedDict replay in **8,192** deterministic adversarial/pseudorandom oracle comparisons. Six invalid-capacity and three invalid-line refusals passed. Frozen synthetic controls passed: HOT (64 references, one miss), COLD (64 references, 64 misses), THRASH (64 misses at C=4 versus eight at C=16), and ORDER (same address histogram with two versus four misses at C=1). The hosted independent audit reproduced all corpus counts and cache-miss conservation, LRU stack monotonicity, and FLUSH >= SKIP for each capacity.

## Decision and next experiment

**No architecture mechanism promoted.** The data refute using R-U or a single infinite-cache reuse percentage as a finite-cache GPU throughput/traffic prediction. The experiment is retrospective, source-conditional and order-assumption-dependent; its capacity sweep is a model sensitivity, not an actual cache characterization or a novel architectural positive law.

Do **not** invest further in standalone address-reuse proxies. The next decisive gate remains **matched same-run trace/counter/cycle evidence** on a version-matched workload, followed by equal-resource RTL synthesis, timing, electrical checks, occupancy and bandwidth sensitivity, and a prospective unseen-workload boundary prediction for exactly one implementable mechanism. V287/V296 remain retired, no RTX-5090-equivalence claim. Kernellum PR #119 was not changed.
