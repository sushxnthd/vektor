# V291 retirement — equal-resource control erases distinct benefit (2026-10-23)

**Decision: RETIRE V291 as an architecture-science breakthrough kernel.** This is a *strongest-baseline functional/equal-resource falsification*, not a measured electrical failure.

## Smallest falsifier
The frozen strong control is an ordinary operand-collector broadcast network with one RF read port, the same four collector destinations, the same full physical tag equality checks, and the same data fanout. It selects the first valid request and broadcasts to all identical full tags. The V291 candidate implements exactly this transfer relation. No distinct scheduling, buffering, banking, or traffic advantage remains under equal hardware resources.

An independently coded Python oracle compared 4,096 exhaustive low-tag/valid patterns and 100,000 deterministic 16-bit physical-tag patterns, including full-tag collisions and warp/version aliases: **zero behavioral mismatches**. Of the randomized tests, 27,125 had more than one granted consumer; all those gains over the deliberately weak serial-only reference were reproduced by the matched control. See `independent_results.json`.

A separate RTL-to-RTL checker and generic synthesis comparison were committed and launched in public CI. **They were still installing tools when this retirement was recorded**. Do not call the Python result an RTL or electrical measurement. Later CI outcome is evidence only; it cannot restore distinct architectural advantage if the same-budget control passes.

## Boundary law and realistic traffic caveat
For N valid iid uniformly distributed full physical tags over A possible tags, a one-port selected-tag broadcast serves E[S]=1+(N-1)/A consumers per beat (conditional on N>=1). With N=4 and A=65536, E[S]=1.000045776. Correlated aliases can make E[S] higher, but the same-budget broadcast baseline gets exactly the same gain. This relation is not an end-to-end throughput claim.

The toy RTL has a 32-bit scalar `rf_data`, whereas Vektor Wave32 FP32 register operands are 32 lanes x 32 bits = 1024 bits. Synchronous RF read latency, per-lane identity, real crossbar capacitance, writeback/collector ports, electrical max-cap/slew, area and timing were not validated. Do not extrapolate the toy block to a tile-level result.

## Prior-art risk
- BOW, MICRO 2020, DOI 10.1109/MICRO50266.2020.00084: GPU operand windows and register bypass.
- Memento, ISCA 2024, DOI 10.1109/ISCA59077.2024.00075: adaptive register file caching and reuse.
- CORF, 2019: coalesced operand register reads.
- Conventional GPU operand collectors already distribute full warp-register operands to collectors.

No V-Tile RTL is changed, no physical improvement is established, and no RTX 5090 comparison is justified. Archive the V291 branch; do not reactivate it without a distinct equal-budget mechanism and a new physical discriminator.
