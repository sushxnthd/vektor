# V309: authentic V100 dynamic SASS acquisition (2026-10-30)

**Evidence tier:** original NVBit/Accel-Sim `.traceg` files collected on Tesla V100, not RTX 5090. No measured stall cycles, GPU IPC, matched hardware counters, physical bank mapping, or power results.

## Provenance and first decisive result

Source: [Purdue Accel-Sim Tesla V100 Rodinia archive](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/rodinia_2.0-ft.tgz), listed at approximately 20 MiB in the [public index](https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/2020.03.18/).

Archive SHA-256: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.

| Authenticated acquisition metric | Observed |
|---|---:|
| Compressed bytes | 21,011,152 |
| Tar members | 309 |
| Actual `.traceg` members | **210** |
| Declared uncompressed trace bytes | 279,797,334 |
| Link entries safely skipped | 11 |
| Bounded trace prefixes sampled | 24 |
| Old NVBit-format row prefixes recognized | **11,353** |
| Total complete lines in those prefixes | 11,794 |

The 11,353 count is a **sample**, not a whole-workload dynamic instruction count. Initial CI #40947646950 downloaded the archive but stopped on historical tar link entries. The metadata-only parser was repaired to skip links without dereferencing them. The subsequent hosted run [#40947792640](https://github.com/sushxnthd/vektor/actions/runs/40947792640) passed, as did the digest-pinned [#40947830494](https://github.com/sushxnthd/vektor/actions/runs/40947830494) and instruction-example [#40947952782](https://github.com/sushxnthd/vektor/actions/runs/40947952782) runs.

The sample contains genuine NVBit trace rows with CTA, warp, PC, mask, destination/source register tokens and SASS opcode, including IMAD, MOV and SHFL instructions. Zero-mask pseudo-rows occur and must not be treated as active executed instructions. A separate full-corpus decoder handles this explicitly.

## Scientific consequence

The previous 512 MiB acquisition barrier for *modern H200 complete configurations* does **not** prevent obtaining a small authentic older-generation SASS dataset. V309 now has a reproducible 21 MB source with 210 trace files, enabling dynamic operand-demand analysis without inventing synthetic traces.

This is an **evidence acquisition success**, not an architecture win. The V100 archive is historical and lacks confirmed paired hardware performance counters. Neither its register numbers nor modulo bank mapping certify physical RF bank conflicts. An equal-resource free-broadcast baseline is still required, and no speculative mechanism is promoted.

## Next gate

Full-corpus profiling is implemented in `v100_sass_profile.py`, with an independent conservation/mutation checker in `audit_v100_sass_profile.py`, under the separately frozen `V100_DYNAMIC_PROFILE_PROTOCOL_20261030.md`. The hosted full-corpus result must be inspected before making any dynamic workload claim. A prospective separate-workload holdout, matched hardware counters and physically credible controls remain mandatory before any RTL investment.
