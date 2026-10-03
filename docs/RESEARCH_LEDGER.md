# Vektor Research Ledger

This ledger records hypotheses, decisive experiments, failures, evidence status, and the next action. Results are never upgraded from simulated/synthesized/projected to measured silicon evidence without a corresponding artifact.

## 2026-10-03 — Bootstrap

### Target
Build an independently designed contemporary GPU architecture and test whether a feasible implementation can approach the broad capability envelope of an RTX 5090-class device.

### Initial architecture hypothesis: Vektor-1A
- 160 active V-Tiles in 10 fabric islands
- Wave32 execution
- 4 wave schedulers/tile
- 128 FP32 lanes/tile
- 2 matrix engines/tile
- 2.56 GHz architectural frequency target
- 128 MB distributed L2
- 512-bit, 28 Gb/s-pin GDDR7 target
- hierarchical RF + operand cache
- dynamic cohort scheduler
- asynchronous trace engine

### What is established
The topology's arithmetic peak targets are machine-readable and executable. Given the configuration, the analytic model derives:
- 104.8576 TFLOPS FP32 target
- 1677.7216 TOPS dense FP4 target
- 3355.4432 TOPS sparse FP4 target
- 1792 GB/s external memory bandwidth target
- 1638.4 Gtexel/s texture-rate target
- 450.56 Gpixel/s ROP-rate target

These are **targets implied by configuration**, not achieved performance.

### What is not established
- ability to sustain 2.56 GHz
- die area or transistor count
- <=575 W board/device power
- sustained utilization on real workloads
- L1/L2/NoC latency and bandwidth feasibility
- register-file timing/energy
- matrix-engine physical feasibility
- texture/raster/RT workload performance
- compiler/runtime maturity
- GDDR7 PHY/controller implementation
- equivalence to any commercial GPU

### Experiment 001 — resource-accounting simulator
A deterministic single-tile resource simulator was introduced to prevent peak-throughput assumptions from being silently treated as utilization. It currently models FP32, FP4 matrix, and provisional local-memory resource ceilings.

**Status:** infrastructure only. No architecture result yet.

## 2026-10-03 — Experiment 002: Wave issue, dependencies, RF banking, operand cache

Branch: `research/vtile-sim-002`

Frozen evidence source: commit `3cc4f527cf0a4bd4ba0a1673424acad738fa69c2`

GitHub Actions run: `37107996482`

Artifact digest: `sha256:791cf869c52fc30ad505fe084496421f54393392d30279071160caf5afb6c2e7`

### Model change
Replaced the pure throughput counter with an auditable issue model containing four shared wave issue slots, separate execution-resource ceilings, in-order wave state, dependency readiness, 16-bank RF reads, an LRU operand cache, fixed load latency, and a bounded outstanding-load queue.

### Evidence quality
- 7 deterministic tests passed in GitHub Actions.
- Benchmark execution passed in the same run.
- Raw JSON benchmark artifact uploaded successfully.
- A failed earlier evidence-capture run (`37107966716`) is preserved; tests passed but benchmark execution failed because direct script invocation did not put the repository root on `sys.path`. The invocation was corrected to module mode. No benchmark numbers from the failed run were used.

### Result A — high-reuse FP32 synthetic kernel
No operand cache: 1024 cycles, 50.0% issue utilization, 4096 RF reads, 30480 bank stalls.

64-entry operand cache: 513 cycles, 99.805% issue utilization, 64 RF reads, 142 bank stalls.

Within this simulator, the operand cache reduces modeled RF reads by 98.4% and removes the dominant RF-bank bottleneck for this workload.

### Result B — dependent FP32 synthetic kernel
With a 64-entry operand cache: 521 cycles, 98.27% issue utilization, 2322 RF reads, 112 dependency stalls.

This indicates that 32 resident waves can mostly hide the modeled four-cycle arithmetic dependency once RF contention is reduced. This is a simulator behavior, not a silicon result.

### Result C — dependent load/use negative control
With 120-cycle fixed load latency and a 64-entry operand cache: 983 cycles, 13.02% issue utilization, 29092 dependency stalls, 240 resource stalls, and 832 fully idle cycles.

Changing operand-cache capacity does not improve this kernel. The modeled bottleneck is memory latency, providing a negative control against treating the RF optimization as universal.

### Supported claim
In the current deterministic V-Tile simulator, RF-bank pressure can halve issue throughput on a high-reuse synthetic FP32 workload, while a small operand cache largely removes that modeled bottleneck; the same cache does not rescue a dependent long-latency memory workload.

### Explicit boundary
Experiment 002 does not establish register-file energy savings, physical frequency, area, power, real-workload performance, superiority over another GPU, or RTX 5090 equivalence.

### Highest-value next experiment
Implement a parameterized L1/shared-memory + L2 hierarchy with finite queues, hit/miss latency, MSHRs and bandwidth, then add divergence masks and a conventional reconvergence baseline. Only after that baseline exists should Vektor's proposed dynamic cohort scheduler be tested on identical traces.

### Subsequent gate
If a scheduler/RF effect survives the richer simulator and adversarial traces, implement a synthesizable Wave32 scheduler + banked register-file slice and prove RTL/reference-model equivalence before making timing, area, or power claims.

## 2026-10-03 — Experiment 003: Explicit non-blocking memory hierarchy

Branch: `research/memory-hierarchy-001`

Frozen evidence source: commit `8372db0df829f6d24c51328d664017984490c8c6`

GitHub Actions run: `37108593818`

Artifact digest: `sha256:b64cd944cbd7b9bed8a92202580648a4df6148583bb2ecfdf1f38c282664a945`

### Model change
The fixed load-latency shortcut can now be replaced by a parameterized L1 -> L2 -> DRAM timing hierarchy. The reference model includes set-associative L1/L2 state, cache-fill timing, finite request bandwidth, same-line miss merging, configurable MSHRs, DRAM request bandwidth, and direct backpressure into wave issue.

Provisional parameters used in the frozen benchmark are 128 KiB L1 / 128-byte line / 4-way / 4-cycle hit, 8 MiB L2 / 16-way / 40-cycle hit, 300-cycle DRAM latency, two DRAM requests/cycle, and an MSHR sweep. These values are model parameters rather than silicon measurements.

### Evidence quality
- 13 deterministic tests passed in GitHub Actions.
- Existing Experiment 002 benchmark still passed.
- Memory-hierarchy benchmark passed and its raw JSON artifact was uploaded in the same clean run.
- Tests directly exercise DRAM fill to L1 hit, same-line miss merging, MSHR rejection/backpressure, L1 eviction exposing an L2 hit, cold pipeline loads, and integrated same-line coalescing.

### Result A — MSHR threshold on a cold dependent trace
For 32 resident waves with four dependent unique-line load/use iterations each:

- 8 MSHRs: 4804 cycles, 1.33% issue utilization;
- 16 MSHRs: 2408 cycles, 2.66% issue utilization;
- 32 MSHRs: 1219 cycles, 5.25% issue utilization;
- 64 MSHRs: 1219 cycles;
- 128 MSHRs: 1219 cycles.

All cases perform 128 modeled DRAM misses. The no-benefit region above 32 MSHRs follows from this trace exposing no more than one blocking miss per each of 32 waves at once. It is not a general recommendation that a V-Tile needs exactly 32 MSHRs.

### Result B — coalescing is not latency reduction
Mapping the same 128 logical loads onto eight outstanding cache lines yields 8 DRAM misses plus 120 merged requests, a 93.75% reduction in DRAM transactions, yet runtime remains 1219 cycles once MSHR capacity is non-binding.

This is a useful negative result: reducing external transactions does not improve this dependency-limited trace because the critical path still waits on miss completion.

### Result C — true L1 reuse is distinct
Mapping all four iterations to a single line produces 1 DRAM miss, 31 merged misses, and 96 L1 hits. Runtime falls to 360 cycles and issue utilization rises to 17.78%.

Relative to the 1219-cycle latency-bound cases, actual post-fill L1 reuse reduces modeled runtime by about 70.5%.

### Supported claims
The simulator now distinguishes miss-level parallelism, outstanding-line coalescing, and post-fill cache reuse as separate mechanisms. On the frozen 32-wave trace, useful MSHR capacity saturates at 32, coalescing cuts traffic without cutting latency-bound runtime, and true L1 reuse materially shortens the critical path.

### Explicit boundary
Experiment 003 does not establish physically achievable cache latency/bandwidth, optimal MSHR count on real applications, cache area/energy, NoC behavior, GDDR7 controller/PHY feasibility, commercial-GPU superiority, or RTX 5090 equivalence.

### Highest-value next experiment
Add per-lane execution masks, branch divergence, and a conventional SIMT reconvergence baseline. Freeze balanced traces with matched active-lane work, then implement Vektor cohort compaction as a separate scheduler and compare both under identical RF/memory conditions. Include adversarial cases where compaction overhead should lose.

### Parallel implementation gate
Begin the first synthesizable Wave32 scheduler + banked-RF slice only against a frozen behavioral interface, then prove RTL/reference-model agreement before any timing/area/power extrapolation.
