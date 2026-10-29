# V303: write-coherent operand-cache audit (frozen before code and results)

## Mechanism under test
The main-branch `DependencyTileSimulator` caches source registers under `(wave_id, architectural_reg)` and calls `cache.touch` on a source read. It updates `ready_at[dst]` on writes but never invalidates or versions the cached destination. Consequently a write followed by a dependent read can be counted as an operand-cache hit even though a physically correct cache must supply the new value. This is an **identified modeling correctness defect**, not a GPU performance breakthrough.

V303's **single active mechanism** is a conservative write-invalidate operand-cache policy: invalidate `(wave_id,dst)` at instruction issue when the instruction has a destination. The register write becomes visible after its modeled latency; dependency gating prevents dependent reads before that time. An eventual implementation must also check physical writeback and forwarding behavior.

## Frozen predictions
1. Predicted correctness-win (W1): 32 waves each execute 64 alternating dependent FP32 updates to architectural registers 2/3. A cache keyed only by architectural register will incorrectly reuse stale operand entries; write invalidation must count at least one new RF read for each updated-register source. No performance gain is predicted; more bank stalls or cycles may result.
2. Predicted no-change (N1): 32 waves each execute 64 FP32 instructions reading two immutable registers 0 and 1 and writing rotating distinct destinations 2..31. Write invalidation must not change source cache hit/miss counts or cycles versus the legacy simulator.
3. Cross-wave isolation: invalidating wave A's register must not invalidate the same architectural register in wave B.
4. Oracle: a standalone version-tag reference model increments each register version on writes and requires cache hits to match the current version. Every hit from the corrected simulator must correspond to an equal-version oracle hit. Independent minimal counterexample: two read-modify-write instructions of one register must generate two RF reads, not one.

## Hard gates
- Run all existing unit tests and benchmark scripts, plus targeted version-tag tests.
- Preserve the legacy output and quantify deltas. Do not silently upgrade previously published operand-cache speedups.
- If source reads can be served from a same-cycle write-forwarding path, model that explicitly before claiming physical timing.
- Treat this as a correctness repair only. Do **not** call it a novel architectural performance mechanism or a world-class completion.
- After validating, move to independently reproduced bottleneck attribution before proposing another performance mechanism.

## Prior art and limits
Register-file operand collectors and bank-aware warp scheduling are established. HPCA 2023 *Mitigating GPU Core Partitioning Performance* discusses bank-aware scheduling; GPGPU-Sim models register bank arbitration and operand collection. V303 does not claim either idea as novel.
Sources: https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf ; https://github.com/gpgpu-sim/gpgpu-sim_distribution

## Evidence tier
This protocol is source-inspection-based. No numerical results, RTL equivalence, synthesis, routing, electrical checks, GPU throughput, or RTX 5090 equivalence are claimed before execution.
