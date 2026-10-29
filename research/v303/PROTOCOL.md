# V303 prospective RF operand-cache coherence audit (2026-10-29)

## Motivation and scope
The main V-Tile simulator's operand cache is keyed by (wave_id, architectural register). It touches entries on source reads but never explicitly updates or invalidates them on destination writes. Consequently, a cache hit after a register overwrite implicitly assumes a coherent, zero-cost cache update. This audit tests that assumption before using the simulator to motivate new GPU hardware.

**Candidate mechanism:** version-coherent operand-cache maintenance at destination writes. The conservative implementation invalidates a resident entry; the zero-cost write-update variant is an optimistic upper bound, not a physical implementation. The candidate is *not* promoted as a new speedup claim without a port-limited, area/timing-matched update implementation.

## Frozen hypotheses and falsification
1. H1, read-mostly repeated operands (existing reuse_fma kernel): write invalidation should preserve most of the ideal-update operand-cache benefit because frequently read source registers are not overwritten.
2. H2, alternating dependent-register updates (existing dependency_fma kernel): write invalidation should increase RF reads relative to ideal zero-cost updates. Whether cycles increase is measured, not assumed.
3. H3, dependent load/use (existing load_use kernel): memory dependency should remain the dominant bottleneck, irrespective of cache maintenance.
4. Adversarial unit trace: read R, write R, read R must incur an RF reread under invalidate; the old implicit-preserve behavior is **not coherent** unless a physical write-update is provided.
5. No physical benefit claim is allowed without an explicit cache write-port model, matched read/write bank accounting, RTL, timing and power proxies.

## Evaluation design
Run the exact same three kernels under cache capacities 0, 8, 64 and policies invalidate / ideal_update, with no seed tuning. Report cycles, RF reads, bank stalls, and relative differences. Independently enumerate short register read/write sequences and check cache-data coherence with a value-carrying oracle.

**No-win prediction:** in the read-mostly kernel, invalidate and ideal_update should tie or nearly tie.
**Potentially material correction:** in the dependent update kernel, invalidate should show additional RF traffic.
**Stop rule:** if no distinct implementable mechanism beats a simple coherent baseline with an equal-resource physical path, retire V303 and preserve the simulator correction. Never use ideal_update numbers as silicon evidence.

All workloads are synthetic. No RTX 5090, tile throughput, power, routed timing or novelty claim follows from this protocol.
