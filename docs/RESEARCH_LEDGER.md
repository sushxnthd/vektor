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

### Highest-value next experiment
Replace the provisional memory-pipeline assumption with a parameterized latency/bandwidth hierarchy and add wave issue/dependency state. Then run compute-bound, matrix-bound, bandwidth-bound, and mixed synthetic kernels to quantify the utilization required for the full-chip peak projections.

### Subsequent gate
Implement a first synthesizable execution slice (Wave32 scheduler + FP32 lane group + register banking) and compare RTL behavior against the simulator before making timing/area claims.
