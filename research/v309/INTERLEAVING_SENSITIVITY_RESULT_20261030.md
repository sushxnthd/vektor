# V309: order-preserving warp-interleaving sensitivity, hosted result (2026-10-30)

**HOSTED PASS:** [GitHub Actions #41053006272](https://github.com/sushxnthd/vektor/actions/runs/41053006272), source commit `94702526ae1215f14a722829e1f3935c720a04b7`, [raw JSON artifact #12975536471](https://github.com/sushxnthd/vektor/actions/runs/41053006272/artifacts/12975536471). Frozen protocol `25765b3` preceded experiment code `8897879`. This is a **retrospective, source-conditional workload-model falsification**, not a measured GPU result.

## Decisive finding
The recorded historical .traceg LDG row order is equivalent to concatenating each CTA/warp stream in first-seen order for **all 210 trace files**, under all four replay capacities and both unknown-address policies. Thus the previous "recorded-order" finite-LRU experiment is, for this decoded subset, effectively a **warp-serial replay**. It is not independently authenticated memory-service order.

Reordering the exact same certified LDG instruction bundles in round-robin order across CTA/warp streams, **without changing any per-stream instruction order, addresses, unknown-row events, or cache capacity**, changes the hypothetical LRU miss count dramatically:

| Hypothetical capacity | SKIP recorded/serial | SKIP round-robin | RR/recorded | FLUSH recorded/serial | FLUSH round-robin |
|---|---:|---:|---:|---:|---:|
| 4 lines | 500,441 | 468,252 | 0.9357x | 500,726 | 468,306 |
| 16 lines | 228,308 | 436,227 | 1.9107x | 236,897 | 437,618 |
| 64 lines | **175,042** | **421,962** | **2.4106x** | 202,939 | 428,723 |
| 256 lines | 161,832 | 357,518 | 2.2092x | 192,212 | 388,754 |

The **sign reverses** with cache capacity: at 4 lines, round-robin predicts **6.43% fewer** misses than recorded; at 64 lines, **141.06% more**. This is an exact output of the declared fully associative LRU model, not an observed hardware cache effect. The two missing-row policies are assumptions, not physical bounds.

### Per-family 64-line SKIP sensitivity
| Retrospective Rodinia family | Recorded/serial misses | Round-robin misses | Ratio |
|---|---:|---:|---:|
| Backprop | 6,790 | 9,100 | 1.34x |
| BFS | 4,281 | 22,168 | 5.18x |
| Heartwall | 6,421 | 7,237 | 1.13x |
| Hotspot | 406 | 406 | 1.00x |
| KMeans | 425 | 13,600 | **32.00x** |
| LUD | 436 | 392 | 0.90x |
| Nearest Neighbor | 22,972 | 183,776 | **8.00x** |
| Needleman-Wunsch | 2,575 | 2,584 | 1.00x |
| Pathfinder | 717 | 717 | 1.00x |
| SRAD-v2 | 14,956 | 12,188 | **0.81x** |
| Streamcluster | 115,063 | 169,794 | 1.48x |

Across 210 files, recorded and serial are identical for **210/210** under every tested capacity/policy; round-robin differs from recorded in **178/210** files under at least one configuration, and in **153/210** for C=64 SKIP. Sixteen files have no eligible LDG events. This variation shows why a single warp-serial cache replay cannot qualify DRAM traffic or a throughput boundary.

## Exact synthetic boundary and controls
Frozen before corpus evaluation: two disjoint streams with K=2 lines per stream and R=3 repetitions, capacity C=2, produce SERIAL=4 misses versus ROUND_ROBIN=12. At C=4 both produce 4 compulsory misses. The general sufficient thrash regime is K <= C < WK for W disjoint streams of K lines, with strict round-robin reuse distance >= C: serial misses WK, round-robin WKR, giving factor R. This is a classical scheduling/cache-capacity fact, **not an original GPU architecture mechanism**. A shared-line countercontrol reverses the ordering (SERIAL=4, ROUND_ROBIN=2 at C=1), preventing a false universal sign law.

## Validation and limitations
- SHA-256-authenticated Tesla V100 Rodinia 2.0-ft archive; 210 files, 11 families, 240,465 global-proxy rows, 197,197 LDG rows, 190,219 certified LDG rows, 530,930 line references and 159,345 per-file unique line identities.
- Full-corpus prior recorded-order reproduction: C=64 SKIP=175,042 and FLUSH=202,939.
- **9,408** independent list-based LRU oracle checks plus synthetic high/no-win and shared-line controls; file/application conservation and LRU monotonicity passed in hosted CI.
- Preserves per-stream order, but **neither round-robin nor recorded/serial is proven to be a feasible V100 scheduler order**. The trace format's CTA/warp interpretation and producer identity remain conditional. Different stream scheduling can also change real occupancy, dependencies and cache coherence. The modeled cache is fully associative LRU, with 128-byte lines, not calibrated L1/L2. Missing LDG and all other accesses are omitted.

## Scientific decision
**Retire the previously published recorded-order 64-line LRU miss numbers as stand-alone physical cache-traffic estimates.** Retain them as explicitly conditional schedule sensitivities only. A valid positive GPU mechanism must first obtain matched, version-identical trace/counter/cycle evidence or a validated trace-driven scheduler/cache hierarchy, then demonstrate matched-resource RTL/timing/area and unseen workload predictions. Further replay-only optimizations are not a substitute.

No V287/V296 revival, new mechanism, hardware speedup, power result, routed timing signoff or RTX-5090-equivalence claim. Kernellum PR #119 remains unchanged.
