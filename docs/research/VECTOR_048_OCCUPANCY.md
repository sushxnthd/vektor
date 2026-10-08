# Vektor-048 — phase-dither occupancy falsification (2026-10-09)

Evidence: deterministic C++ cycle simulation, independent Python event-calendar replication. NOT RTL-simulated, synthesized, measured silicon, or RTX 5090-class evidence.

## Preregistered mechanism
Vektor-047 found +50% modeled IPC from phase-dither-9 over round-robin on a four-wave, single-bank, 5-cycle RF-latency synthetic trace. Vektor-048 held policy and synthetic generator fixed, increased resident waves to 8/16/32, and repeated 360 paired cases per W (4 banksets x 5 latencies x 2 stall regimes x 9 seed/pattern variants). Two read ports/bank, three operands/instruction, 1400 cycles, first 200 warmup. 11.1% structured rotating-pattern probes. No tuning on scaling holdout.

| W | RR IPC | Dither IPC | Relative change | wins/losses/ties | 95% 40-regime cluster-bootstrap CI |
|---:|---:|---:|---:|---:|---:|
| 4 (recomputed control) | 0.887076 | 0.902148 | +1.699% | 185/68/107 | +0.260% to +3.772% |
| 8 | 1.404137 | 1.413685 | +0.680% | 217/98/45 | +0.258% to +1.211% |
| 16 | 2.017037 | 2.018257 | +0.060% | 190/140/30 | -0.009% to +0.138% |
| 32 | 2.672271 | 2.673481 | +0.045% | 180/155/25 | -0.025% to +0.114% |

The 32-wave CI includes zero. Bootstrap (20,000 samples) clusters nine seeds together per bank/latency/stall regime, describing only the chosen synthetic distribution. No tag mismatch or bank-port overflow across 2,880 policy runs. Independent Python reimplementation reproduced 270 selected scaling runs, max mean-IPC residual <1e-6.

## Mechanism boundary
In a single bank with two reads/cycle and three mandatory reads/instruction, long-run issue capacity <=2/3 IPC (assuming no bypass/reuse/multicast). All-hot, L=5, 12,000-cycle measured window: W4 RR=0.444333 and dither=0.666667; W8 RR=0.636250 and dither=0.638667; W10 RR=0.666583 and dither=0.666667. By W10, the baseline saturates bank capacity and the 4-wave headline no longer transfers. Finite-window rates can slightly exceed 2/3 due to pre-window operand reads.

## Adversarial 048B follow-up
W8, 16 banks, L1, rotating descriptors, periodic 12.5% downstream rejection: RR 6.0000 IPC versus dither 7.0000 (+1.0). Same approximate rejection fraction with deterministic hash-based stalls: RR 6.5175 versus dither 6.588333 (+0.070833). Across 108 paired hash-stall cases/W, mean relative changes: W8 +0.518%, W16 -0.006%, W32 -0.038%. Independent Python replication of 24 selected hash-stall runs: <1e-8 IPC residual, zero safety errors. The extreme periodic result is an aliasing artifact, not robust general improvement.

## Discovery Protocol V2
- KNOWN (analytic): long-run single-bank all-hot issue <=2/3 IPC under stated port/read assumptions.
- KNOWN (model): low-occupancy priority/response resonance can idle RF ports; phase perturbation sometimes helps.
- BELIEVED: increasing independent resident waves can saturate RF read capacity and hide phase effects.
- CONFLICTING: dither is better for 32-wave GPU scheduling (155/360 losses, 95% regime-bootstrap CI includes zero).
- FALSIFIED: selected four-wave +50% throughput result generalizes to a 32-wave tile.
- FALSIFIED: +1.0 IPC eight-wave periodic-stall anomaly survives equal-rate hash-stall control.
- ANOMALOUS: deterministic rotating descriptors and periodic downstream stalls phase-lock.
- UNTESTED: scoreboard replay, real RF data, multi-instruction wave pipelines, actual KPX traces, RTL/PPA, graphics/tensor/ray/memory systems.

Explorer: condition dither on measured occupancy; Skeptic: artificial periodicity; Experimentalist: fixed policy scaling and decorrelated stalls; Analyst: retain all regressions; Anomaly Hunter: inspect W8 +1 IPC outlier; Prior-Art Auditor: register banking/operand collection/scheduling already known; Replicator: independent Python event-calendar; Theorist: capacity bound 2/3 IPC. No novelty claim.

## 5090-class gates
All INCONCLUSIVE: FP32 sustained, datatype/sparsity-resolved tensor, 32GB-class capacity and bandwidth, cache hierarchy, texture/raster, ray workloads, frequency, area, power, KPX compiler/runtime, reproducibility. Vektor-1A 104.8576 TFLOPS FP32 is a target calculation only. NVIDIA official product specs (rechecked 2026-10-09): 21,760 CUDA cores, 2.41 GHz boost, 3352 AI TOPS (not datatype-resolved), 318 RT TFLOPS (not a ray workload), 32GB GDDR7, 512-bit, 575W. https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

## Single next decisive action
Implement a 32-wave scoreboard-aware tagged operand collector with real data, finite return bandwidth and replay; compare RR, phase-dither and age-aware arbitration on KPX-generated held-out traces, and synthesize equal-budget RTL. Do not promote dither as a general scheduler without a reproducible occupancy trigger and PPA evidence.

Prior art: https://gpgpu-sim.org/manual/index.php/Main_Page ; https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/

Complete preregistrations, C++/Python source, raw CSV, analysis and SHA256 manifest: Vektor-048 reproducibility package generated in the ChatGPT working environment; source-file GitHub integration remains pending.
