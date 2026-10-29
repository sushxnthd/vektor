# V303 frozen cache-coherence audit: independent local replay

Date: 2026-10-29. Protocol committed first at `8523706980f35eda62563fdc812aeac622d83cc2`. Results below are from an independently written local event-loop replica, subsequently committed as `research/v303/independent_replay.py`; the hosted main-model cross-check is pending at the time of this report.

## Scientific correction

The previous V-Tile operand-cache model preserved entries across destination-register writes. That is valid **only if** hardware updates resident cached data coherently. No such update port, energy, timing or write arbitration had been priced. V303 makes the conservative `invalidate` policy the simulator default and preserves `ideal_update` as an explicitly unpriced optimistic bound.

The independent value-carrying oracle exhaustively checks 1,364 read/write sequences of lengths 1..5 over two registers. Invalidation and explicitly coherent update have zero stale reads; implicit preservation produces counterexamples.

## Frozen kernel sensitivity

Independent replay, same 32 waves, issue width four, 16 RF banks, two reads per bank, deterministic LRU and dependency timing. Values are **synthetic**.

| Kernel | Cache entries | Invalidate cycles | Ideal-update cycles | Invalidate RF reads | Ideal-update RF reads |
|---|---:|---:|---:|---:|---:|
| H1 read-mostly | 0 | 1024 | 1024 | 4096 | 4096 |
| H1 read-mostly | 8 | 513 | 513 | 2048 | 2048 |
| H1 read-mostly | 64 | 513 | 513 | 64 | 64 |
| H2 alternating dependent overwrites | 0 | 1024 | 1024 | 4096 | 4096 |
| H2 alternating dependent overwrites | 8 | 1024 | 1024 | 4096 | 4096 |
| H2 alternating dependent overwrites | 64 | **516** | 521 | **2080** | 2322 |
| H3 dependent load/use | 0 | 983 | 983 | 512 | 512 |
| H3 dependent load/use | 8 | 983 | 983 | 512 | 512 |
| H3 dependent load/use | 64 | 983 | 983 | 288 | 288 |

H1's predicted no-win regime holds exactly. H3 remains memory-latency dominated. **H2 falsifies the simple prediction that invalidation must increase aggregate RF traffic.** With finite LRU and round-robin issue, changing the policy changes the interleaving and eviction pattern; in this frozen trace the conservative policy improves both cycles and RF reads. Therefore a naive monotonic `RF_reads(invalidate) >= RF_reads(ideal_update)` law is false for the scheduler-coupled system. This does not imply invalidation is universally faster.

## Mechanistic bound and next hard gate

Let `D_t` be the number of issued writes in cycle `t` whose destinations are resident in the operand cache. An always-update implementation with `P` cache-write ports must either defer/serialize at least `max(0,D_t-P)` writes in that cycle or invalidate some entries. The original ideal-update model does neither. The actual performance consequence depends on subsequent reuse, eviction, RF-bank contention, occupancy and issue order.

This result **does not establish a novel GPU speedup mechanism**. Before promotion, measure `D_t`, implement a port-limited coherent update baseline, and compare area/timing against simple invalidation. If no prospective advantage survives, close this draft PR unmerged and retire V303.

## Limitations

No data values are propagated by the main V-Tile issue model; the separate value-carrying oracle checks coherence semantics. No physical cache data array, write ports, routing, timing, power, or real application workload is modeled. The local independent replay is not yet a substitute for hosted regression. No RTX-5090-equivalence claim.
