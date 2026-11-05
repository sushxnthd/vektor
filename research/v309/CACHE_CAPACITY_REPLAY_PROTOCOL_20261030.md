# V309 certified-subsequence cache-capacity sensitivity protocol (frozen 2026-10-30)

## Research question and scope
Does the high *address-identity* reuse reported in the historical Tesla V100 Rodinia LDG trace subset survive a finite-capacity, demand-only, fully associative LRU replay, or is it an artifact of assuming infinite cache capacity? This is a workload-model **falsification/sensitivity** experiment, not a hardware proposal, actual GPU cache simulation, measured DRAM traffic, or unseen validation. No V287/V296 revival; keep PR #26 and the single V309 branch.

## Frozen input and controls
Use the SHA-256 authenticated 2020-03-18 Rodinia 2.0-ft trace archive (aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1), 210 trace files and 240465 global-proxy rows. Only LDG records with source-conditionally identifiable visible-lane addresses enter the replay, using the unchanged trace_line_reuse.py decoder and hypothetical 128-byte lines. Unknown rows must never be fabricated as misses or hits.

Each trace file is an independent address domain and cache is cold at its start. Within an instruction, line IDs are visited in ascending order (an arbitrary, declared deterministic tie-breaker). The trace's inter-instruction order is used **only as a replay sensitivity assumption**, not authenticated GPU memory scheduling. Compare two policies for uncertified LDG rows: SKIP (retain cache contents, optimistic replay) and FLUSH (clear cache before the next certified instruction, pessimistic replay). Neither brackets actual DRAM behavior because omitted instructions could prefetch lines or evict them differently. STG/ATOM/RED and shared/local accesses are omitted, not assumed cost-free.

Capacity sweep (lines): 1, 4, 16, 64, 256, 1024, plus infinite-capacity cold cache (unique line identities U). Equal-resource control is the same LRU cache and same certified address stream without speculative changes. A fixed-address coalescer cannot beat the infinite-capacity unique-line floor in this model.

## Frozen predicted synthetic regimes (before full-corpus run)
- HOT: 64 instructions each referencing one identical line: R=64, U=1, all finite capacities miss exactly once; high reuse survives.
- COLD: 64 instructions each referencing a different line: R=64, U=64, all capacities miss 64; no benefit from cache capacity.
- THRASH: eight distinct lines cyclically repeated eight times (R=64,U=8): at C=4, 64 misses; at C=16, 8 misses. Predicted capacity win at C=16 and no-win at C=4.
- ORDER: two sequences with identical line-frequency histogram and R=4,U=2: ABAB has 4 misses at C=1, AABB has 2. Therefore unordered frequency/reuse counts cannot identify finite-cache miss counts.
- Monotonicity for the same sequence: LRU misses cannot increase with cache capacity; FLUSH misses cannot be lower than SKIP misses at the same capacity. (If a counterexample to either assertion arises, retain the failure and investigate the model.)

## Independent verification and conservation
Use a separate simple list-based LRU oracle on deterministic adversarial and pseudo-random short sequences, and malformed capacity refusals. Replay per trace file and report per-app and global R, U, misses by capacity and policy, all summing across file domains. Exact conservation must reproduce LDG=197197, certified=190219, R=530930, U=159345 from the prior hosted audit. If any mismatch or digest failure, fail closed. No benchmark speedup, power, cache hit-rate or GPU throughput inferred.

## Stop criterion
If finite-cache sensitivity erases most apparent address reuse, reject the infinite-cache reuse opportunity as a GPU traffic proxy. Even if reuse survives, do **not** promote hardware until matched counters/cycle-model validation and equal-resource physical evaluation. The historical tracer-producer identity remains unverified. Rodinia is already inspected, so all application results are retrospective.
