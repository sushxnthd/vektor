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
