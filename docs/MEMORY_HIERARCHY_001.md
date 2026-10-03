# Memory Hierarchy 001 — Non-blocking L1/L2/DRAM Gate

## Status

**SIMULATED / PASS as infrastructure; architecture conclusions remain provisional.**

This milestone replaces the V-Tile's single fixed load-latency constant with an explicit non-blocking L1 -> L2 -> DRAM timing hierarchy integrated into wave issue. It is not a claim of silicon performance, physical cache feasibility, or RTX 5090 equivalence.

## Frozen evidence

GitHub Actions evidence run: `37108593818`

Source commit: `8372db0df829f6d24c51328d664017984490c8c6`

Uploaded artifact: `memory-hierarchy-results`

Artifact digest: `sha256:b64cd944cbd7b9bed8a92202580648a4df6148583bb2ecfdf1f38c282664a945`

CI result: 13 deterministic tests passed; the existing V-Tile benchmark passed; memory-hierarchy benchmark execution passed; both evidence artifacts uploaded.

## Model added

The timing model now contains:

- 128 KiB provisional L1, 128-byte lines, 4-way set associativity;
- 4-cycle provisional L1 hit latency and four L1 accesses/cycle;
- 8 MiB provisional per-tile/slice L2 model, 16-way set associativity;
- 40-cycle provisional L2 hit latency and four L2 accesses/cycle;
- 300-cycle provisional DRAM latency;
- two DRAM requests/cycle;
- configurable MSHR capacity;
- same-line outstanding-miss merging;
- finite L1, L2, and DRAM request bandwidth;
- cache fill timing and L1/L2 replacement state;
- backpressure from the hierarchy into Wave32 issue.

The sizes and latencies above are **architecture parameters**, not measured values from Vektor silicon or inferred measurements of a commercial GPU.

## Deterministic benchmark

The benchmark uses 32 resident waves, four dependent 128-byte load/use iterations per wave, and the same four-slot V-Tile issue model used in Experiment 002.

### 1. Cold unique lines — MSHR sweep

Every logical load accesses a unique cache line, so the 128 loads become 128 DRAM misses with no merging or cache hits.

| MSHRs | Cycles | Issue utilization | DRAM misses | MSHR stall observations |
|---:|---:|---:|---:|---:|
| 8 | 4,804 | 1.33% | 128 | 99,456 |
| 16 | 2,408 | 2.66% | 128 | 32,704 |
| 32 | 1,219 | 5.25% | 128 | 0 |
| 64 | 1,219 | 5.25% | 128 | 0 |
| 128 | 1,219 | 5.25% | 128 | 0 |

**Modeled result:** useful miss-level parallelism saturates at 32 MSHRs for this trace. The trace has 32 resident waves and at most one dependency-blocking load per wave, so increasing MSHRs above 32 cannot expose additional independent misses. This is a workload/model result, not a universal GPU sizing rule.

### 2. Coalescing without post-fill reuse

The same 128 logical loads are mapped onto eight cache lines. Requests to an already outstanding line merge, but each phase advances to a different line before returning to a filled line.

For every tested MSHR capacity >=8:

- cycles: **1,219**;
- issue utilization: **5.25%**;
- DRAM misses: **8**;
- merged misses: **120**;
- L1 hits: **0**.

Coalescing reduces external DRAM transactions from 128 to 8 (93.75%) but does **not** reduce runtime versus the 32+-MSHR cold-unique case. This trace is dominated by dependent miss latency rather than external transaction count once enough MSHRs are available.

That is a deliberate negative result: lower memory traffic is not automatically lower execution time.

### 3. True post-fill L1 reuse

All four iterations reuse one line. The first wave group creates one DRAM miss plus outstanding-line merges; later iterations access the filled line.

For every tested MSHR capacity:

- cycles: **360**;
- issue utilization: **17.78%**;
- DRAM misses: **1**;
- merged misses: **31**;
- L1 hits: **96**.

Relative to the 1,219-cycle latency-bound cases, actual post-fill L1 reuse reduces modeled runtime by about **70.5%**. This confirms that the integrated hierarchy distinguishes request coalescing from a true cache hit rather than counting both as the same mechanism.

## Supported claims

The current simulator supports the following narrow conclusions:

1. On the 32-wave dependent cold-load trace, increasing MSHRs from 8 to 32 reduces runtime from 4,804 to 1,219 cycles; more than 32 MSHRs provides no additional benefit because the trace exposes no more than 32 independent blocking misses at once.
2. Outstanding-line coalescing can dramatically reduce modeled DRAM traffic without reducing latency-bound runtime.
3. Post-fill L1 reuse is behaviorally distinct from coalescing and materially reduces runtime in the same timing model.

## Explicit boundary

This milestone does **not** establish:

- that 32 MSHRs is optimal for real Vektor workloads;
- physically achievable L1/L2 latency or bandwidth;
- cache area, energy, leakage, or timing closure;
- GDDR7 controller/PHY behavior;
- NoC contention or multi-tile coherence behavior;
- real application performance;
- an advantage over NVIDIA, AMD, Vortex, or another GPU;
- RTX 5090-class capability.

## Next decisive gate

Memory timing is now rich enough to stop using the fixed-latency shortcut. The next experiment should add execution masks and a conventional SIMT divergence/reconvergence baseline, then compare it against a separately implemented cohort-compaction scheduler on identical branch traces.

Only if a cohort effect survives balanced/adversarial traces should that mechanism move to RTL. In parallel, the first synthesizable Wave32 scheduler + banked-RF slice can begin once its behavioral interface is frozen against the reference simulator.
