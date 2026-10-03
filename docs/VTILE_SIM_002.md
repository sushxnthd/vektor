# V-Tile Simulator 002 — Dependency, RF Banking, and Operand Cache Gate

## Status

**SIMULATED / PASS as infrastructure; architecture effect is provisional.**

This milestone replaces the bootstrap resource-counter with an auditable Wave32 issue model. It is not a claim of silicon performance, physical feasibility, real-workload speedup, or RTX 5090 equivalence.

## Frozen implementation

GitHub Actions evidence run: `37107996482`

Source commit: `3cc4f527cf0a4bd4ba0a1673424acad738fa69c2`

Uploaded artifact: `vtile-issue-results`

Artifact digest: `sha256:791cf869c52fc30ad505fe084496421f54393392d30279071160caf5afb6c2e7`

CI result: 7 tests passed; benchmark execution passed; artifact upload passed.

## Model added

The V-Tile model now includes:

- four shared wave issue slots;
- separate FP32, matrix, and memory issue ceilings;
- in-order per-wave instruction issue;
- register dependency readiness;
- 16-bank register-file model with configurable read ports;
- per-wave-keyed LRU operand cache;
- fixed load latency;
- bounded outstanding-load queue;
- explicit accounting for dependency, resource, bank, and idle stalls.

It still does **not** model L1/L2 caches, DRAM timing, NoC contention, execution-pipeline timing, instruction fetch, branch divergence, cohort scheduling, physical wire delay, area, energy, or clock closure.

## Deterministic microbenchmarks

All results below are produced by `benchmarks/vtile_issue_bench.py` inside GitHub Actions.

### 1. Operand-reuse FP32 kernel

32 waves × 64 Wave32 FP32 FMA instructions. Each wave repeatedly reads the same two source registers.

| Operand-cache entries | Cycles | Issue utilization | RF reads | Bank stalls |
|---:|---:|---:|---:|---:|
| 0 | 1024 | 50.00% | 4096 | 30480 |
| 8 | 513 | 99.81% | 2048 | 7086 |
| 16 | 517 | 99.03% | 1400 | 4182 |
| 32 | 513 | 99.81% | 832 | 1678 |
| 64 | 513 | 99.81% | 64 | 142 |
| 128 | 513 | 99.81% | 64 | 142 |

**Observed in this simulator only:** RF read pressure is a binding bottleneck without operand reuse storage. A 64-entry cache reaches the same cycle count as 128 entries and reduces modeled RF reads by 98.4% versus no cache.

This does not establish an energy reduction because the cache itself has no area/energy/timing model yet.

### 2. Dependent FP32 chain

32 waves × 64 FP32 instructions, with a four-cycle data dependency inside each wave.

| Operand-cache entries | Cycles | Issue utilization | RF reads | Dependency stalls |
|---:|---:|---:|---:|---:|
| 0 | 1024 | 50.00% | 4096 | 6048 |
| 32 | 575 | 89.04% | 2946 | 1406 |
| 64 | 521 | 98.27% | 2322 | 112 |
| 128 | 523 | 97.90% | 96 | 116 |

The model shows that enough resident waves can hide a four-cycle arithmetic dependency once RF contention is reduced. The non-monotonic 64→128 cycle count demonstrates that the current round-robin/LRU interaction itself must be treated as part of the provisional model, not a physical prediction.

### 3. Load/use memory stress

32 waves × 8 dependent 128-byte load/use pairs with a fixed 120-cycle load latency and 64 outstanding-load limit.

| Operand-cache entries | Cycles | Issue utilization | Dependency stalls | Resource stalls | Idle cycles |
|---:|---:|---:|---:|---:|---:|
| 0 | 983 | 13.02% | 29092 | 240 | 832 |
| 64 | 983 | 13.02% | 29092 | 240 | 832 |
| 128 | 983 | 13.02% | 29092 | 240 | 832 |

The operand cache does not improve this workload because the modeled bottleneck is memory latency. This is a useful negative control.

## Claim boundary

Supported claim:

> In the current deterministic V-Tile simulator, RF-bank pressure can halve issue throughput on a high-reuse synthetic FP32 workload, while a small operand cache largely removes that modeled bottleneck; the same cache does not rescue a dependent long-latency memory workload.

Not supported:

- physical register-file energy savings;
- physical frequency improvement;
- area or power advantage;
- superiority over NVIDIA, AMD, or another open GPU;
- real application performance;
- RTX 5090-class performance.

## Next decisive gate

The next milestone must attack the largest modeling weakness rather than extending the same synthetic result:

1. implement explicit L1/shared-memory and L2 request queues, hit/miss latency, MSHRs, and bandwidth;
2. replace fixed memory latency with a parameterized hierarchy;
3. add branch masks/divergence and a baseline reconvergence scheduler;
4. add a separately testable cohort-compaction scheduler;
5. run identical traces through both schedulers;
6. only if the simulator effect survives, implement the first synthesizable Wave32 scheduler + banked RF slice and verify RTL against the reference model.
