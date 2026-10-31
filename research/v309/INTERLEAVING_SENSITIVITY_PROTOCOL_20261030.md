# V309: per-warp order-preserving memory-replay sensitivity (preregistered 2026-10-30)

## Question and status
The previous 64-line LRU replay implicitly treated the historical .traceg row order as GPU memory-service order. Can legal alternative interleavings that preserve **each CTA/warp's local instruction order** materially change predicted line fills? This is a **falsification/sensitivity** study of a trace-order assumption, not a GPU architecture, a cycle simulator, or a claim that either ordering is physically realizable under V100 scheduling.

Keep the existing V309 qualification branch and draft PR #26. V287/V296 are retired and must not be revived. No hardware mechanism is promoted.

## Frozen input and protocol
Use the SHA-256-authenticated 2020-03-18 Tesla V100 Rodinia 2.0-ft archive, digest `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`. Preserve the existing `address_tail`, `certified_addresses`, and `instruction_lines` semantics without changing the decoder. Only LDG rows enter this replay; each instruction is an atomic bundle of sorted distinct hypothetical 128-byte line IDs. For unknown LDG addresses, retain an explicit unknown event. Never fabricate an address. A stream key is the exact first four numeric row tokens (CTA x/y/z, warp ID); the archive's producer interpretation remains unverified.

Per .traceg file, replay the *same* multiset of events under three schedules:
1. RECORDED: original row order (existing model's assumption).
2. SERIAL: all events from each stream in first-seen stream order, preserving within-stream order.
3. ROUND_ROBIN: one event per stream in first-seen stream order, repeating until exhausted, preserving within-stream order.

At capacities C=4,16,64,256 hypothetical fully associative LRU lines, replay both SKIP (unknown rows do not modify cache) and FLUSH (unknown rows invalidate cache). All caches start cold per trace file. Intra-instruction line order remains ascending. Neither SKIP nor FLUSH brackets actual GPU misses. All three schedules must have identical event count, certified line-reference count, unknown count, unique-line count, and each stream's local sequence.

## Preregistered predictions and kill criteria
- **High-interleaving synthetic regime**: two disjoint streams, each cycles over two unique lines for three rounds, C=2. SERIAL has 4 misses and ROUND_ROBIN has 12. The interleaving sensitivity factor is exactly 3. For W disjoint streams, K distinct lines per stream, R repetitions, and K <= C < W*K, SERIAL has WK misses while strict round-robin (one line event per stream) has WKR misses, provided the round-robin reuse distance is at least C.
- **No-interleaving-sensitivity regime**: same streams, C >= WK, both schedules have WK compulsory misses.
- **Shared-line countercontrol**: streams may share addresses, so no universal inequality SERIAL <= ROUND_ROBIN may be asserted.
- **Real traces**: report per-app and corpus absolute misses and the max/min ratio across the three schedules; **do not preregister a sign**. If materially different, retire recorded-order replay as a stand-alone physical cache-traffic estimator. If identical, this still does not validate GPU timing, cache hierarchy, occupancy, memory-level parallelism, or tracer provenance.

## Independent checks and hard refusals
Implement a separate simple list-based LRU oracle, exhaustive interleavings on small two-stream cases, deterministic random cases, per-stream order checks, and malformed stream/line/capacity refusals. Validate against the existing RECORDED SKIP/FLUSH implementation for every file and capacity; for 64 lines reproduce the previously hosted 175042/202939 global misses. Require exactly 210 files, 197197 LDG rows, 190219 certified rows, 530930 line references and 159345 summed per-file unique lines. Fail closed on any mismatch, archive digest failure, or unsupported row parse.

## Interpretation
The boundary W*K > C is a mathematical fully-associative LRU scheduling-sensitivity law for the frozen synthetic family, **not a new GPU mechanism or an empirical speedup law**. No measured V100 cache misses, DRAM bytes, cycle counts, RTL advantage, area/power or RTX 5090 equivalence is inferred. Stop speculative cache replay after this falsification and prioritize matched trace/counter/cycle evidence and an actual physically evaluable candidate.
