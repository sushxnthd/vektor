# V309: source-conditional full-corpus memory-sector bounds (2026-10-30)

**Evidence tier: historical-tracer-source-conditional workload analysis. NOT measured V100 memory transactions, stalls, bandwidth, throughput or GPU hardware performance.**

## Decisive result

[Hosted CI #40990436508](https://github.com/sushxnthd/vektor/actions/runs/40990436508) **PASSED** on commit `59297f1c`; [raw JSON artifact #12948184008](https://github.com/sushxnthd/vektor/actions/runs/40990436508/artifacts/12948184008). It authenticated the original Purdue V100 Rodinia archive (SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`), read 210 trace files, and checked 240,465 global-memory-proxy rows. This result extends the earlier source-conditional address-recovery work without changing its archive or pretending that the 2020 tracer commit has been established as the actual producer.

| Conditional sector-count classification | Rows |
|---|---:|
| Format-0, previously uniquely mapped | 84,224 |
| Format-0, hidden predicates, **newly identified 32B sector count** | **16,835** |
| Format-0, hidden predicates, still non-point-identified | 5,669 |
| Format-1, point-identified 32B sector count | 133,366 |
| Format-1, non-point-identified 32B sector count | 371 |
| **Total point-identified sector count** | **234,425 / 240,465 (97.4882%)** |
| **Remaining interval-only rows** | **6,040 / 240,465 (2.5118%)** |

**74.8089% of the 22,504 previously ambiguous format-0 rows now have source-conditionally identifiable 32B sector counts.** The remaining 5,669 rows are explicitly retained as uncertain. Format-0 exact recovery does **not** necessarily mean absolute lane addresses or archive-producer identity are known.

The aggregate **full-corpus** source-conditional 32B sector-count interval is **1,580,660–1,595,620** sectors, with a 14,960-sector width (0.9464% of the lower bound). This is a sum of per-warp instruction sector sets, not measured cache transactions. It is a conservative interval: the per-row 4,096-choice and global 2,000,000-choice enumeration caps leave 4,478 format-0 rows with safe but potentially non-sharp bounds. The full-corpus result therefore cannot be presented as a sharp physical interval.

| Family | Format-0 hidden rows | Newly identified | Source-conditional total sectors (lower–upper) |
|---|---:|---:|---:|
| Backprop | 2,048 | 2,048 | 93,717–93,717 |
| BFS | 9,698 | 4,029 | 78,474–93,131 |
| Heartwall | 204 | 204 | 51,509–51,509 |
| Hotspot | 2,766 | 2,766 | 28,506–28,506 |
| KMeans | 0 | 0 | 16,100–16,100 |
| LUD | 0 | 0 | 3,828–4,068 |
| Nearest Neighbor | 0 | 0 | 487,500–487,500 |
| Needleman-Wunsch | 64 | 64 | 7,168–7,168 |
| Pathfinder | 8 | 8 | 4,263–4,326 |
| SRAD v2 | 0 | 0 | 67,072–67,072 |
| Streamcluster | 7,716 | 7,716 | 742,523–742,523 |

## Mechanism and verification

The [frozen protocol](FORMAT0_SECTOR_ENVELOPE_PROTOCOL_20261030.md) and [executable oracle](format0_sector_envelope.py) use the historical source hypothesis `M=A&P`, where `M` is the printed mask, `A` is the original active mask, and format-0 address tokens are ordered by lanes in `A`. If `n=32`, then `A` must be all 32 lanes even if the printed mask contains only a subset. More generally, all source-compatible active masks are enumerated when bounded; otherwise, per-visible-lane possible-token ranks yield rigorous conservative sector-set union/intersection bounds.

The hosted run passed **747 independent exhaustive small-mask cases**, **100 forced-conservative oracle cases**, one adversarial hidden-lane counterexample and malformed-record tests. It checked prior format-0 and format-1 row conservation and the previously verified format-1 envelope 1,194,830–1,195,201. It enumerated **1,999,999** source-compatible masks within the frozen 2,000,000 budget. A separate independent full-corpus redecoder is still outstanding.

The first full-corpus attempt failed closed on a width-extended uint64 overflow token, which may be a predicated-off lane's garbage address. A compatibility addendum was committed before successful outcomes. The implementation now flags possibly visible overflow tokens as unresolved and assigns conservative bounds, rather than silently inventing wraparound semantics. The second failed run was an adversarial fixture assertion error, and the third a bookkeeping assertion that mistakenly charged closed-form unique masks against the enumeration budget. All are preserved in hosted CI history.

## Architectural interpretation and next gate

This is a **trace-identifiability improvement**, not a GPU hardware mechanism. It neither reopens the retired V287/V296/V297–V308 candidates nor promotes a V309 architecture. An ideal fixed-address coalescer remains the strongest no-cost control for unchanged memory addresses, and no sector-count improvement beyond that control is established.

The next decisive experiment is an independent historical producer redecoder and a hardware-counter/cycle-calibrated bottleneck model with genuinely unseen workloads. Only then should a single new hardware mechanism be selected, preregistered, and advanced through equal-resource RTL, synthesis, electrical/timing, workload, and wire/load gates. Kernellum PR #119 remains untouched. No RTX 5090 equivalence claim is supported.
