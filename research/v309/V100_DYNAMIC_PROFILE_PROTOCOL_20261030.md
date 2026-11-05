# V309: frozen full V100 dynamic SASS profiling protocol (2026-10-30)

**Exploratory external workload characterization; not a prospective architecture holdout.** This protocol was committed after inspecting bounded prefixes of the first 24 trace files, but before decoding the full 210-trace archive. No hardware mechanism is being promoted.

## Immutable source
- Purdue Tesla V100 Rodinia 2.0-ft archive (2020), `rodinia_2.0-ft.tgz`.
- First successful independent hosted acquisition: 21,011,152 compressed bytes; SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
- Inventory: 309 tar entries, 210 `.traceg` files, 279,797,334 declared uncompressed trace bytes, 11 links skipped without dereference. Sampled 11,353 matching row prefixes in 24 trace members; this **does not** establish total dynamic instructions.
- Archive contains tracer `stats.csv` files, not independently matched Nsight Compute GPU performance counters.

## Precommitted analysis
1. Stream each trace member without filesystem extraction, bounded to the known SHA and 64 MiB compressed size; reject devices/unsafe paths.
2. Parse trace rows with CTA, warp, PC, active mask, destinations, opcode, source registers and memory width. Count malformed/unsupported rows explicitly. Report zero-mask rows separately.
3. For active rows, count source-register occurrences, within-instruction unique sources, duplicate-source occurrences removable by an **equal-resource free-broadcast baseline**, memory-op mix, and application-family breakdown.
4. Compute conditional collision incidence for modulo bank maps `R % B`, `B=2,4,8`, both with and without `R255`. Treat `R255` as a sensitivity variable, not an established physical zero register.
5. These are **trace-demand descriptors**, not real bank conflict stalls, instruction latency, IPC, occupancy, power, or throughput. The true register-file bank mapping, bypass, collectors and ports are not identified from SASS alone.
6. Independent audit must reconcile global and per-family totals, source conservation, collision monotonicity for nested modulo bank counts, and malformed-input mutations. Archive SHA and decoder version must be retained.

## Decision gate
Use the data to choose a future bottleneck measurement, not a hardware winner. No hardware candidate until a calibrated resource bottleneck and strongest equal-resource control are established; freeze separate predicted-win/no-win workloads before their evaluation. If parsing is materially unsupported, fail closed and preserve the negative result. Do not claim transfer to RTX 5090 or Blackwell.
