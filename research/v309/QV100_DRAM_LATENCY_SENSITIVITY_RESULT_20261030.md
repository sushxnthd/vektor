# V309: source-pinned QV100 DRAM-latency sensitivity (2026-10-30)

## Status and evidence identity

**PASS: independent simulator sensitivity audit, not hardware validation.** The preregistered [protocol](QV100_DRAM_LATENCY_SENSITIVITY_PROTOCOL_20261030.md) and [executable experiment](qv100_dram_latency_sweep.py) were committed before outcome inspection. [Hosted GitHub Actions run #41094525853](https://github.com/sushxnthd/vektor/actions/runs/41094525853), triggered by [workflow commit eda7a0b](https://github.com/sushxnthd/vektor/commit/eda7a0bb220d8ec9a875c5d8a7e5736660db01ae), **passed** on 2026-10-30 at approximately 17:01 UTC. [Raw evidence artifact #12995227726](https://github.com/sushxnthd/vektor/actions/runs/41094525853/artifacts/12995227726) contains the six complete raw logs (two per configuration), all generated config files, SHA-256 manifest, selection manifest, independent audit and build provenance. Artifact retention is 30 days; regenerate from the pinned workflow.

The original authenticated Rodinia 2.0-ft Pathfinder `1000_20_5` trace selection remains unchanged: four kernel launches, two original HtoD copies. The same pinned Accel-Sim/GPGPU-Sim QV100-SASS binary and trace config are used. Exactly one `gpgpusim.config` setting changes: active `-dram_latency` from **100** to **200** and **400** simulator units. The script refuses other config changes, digest drift, missing/duplicated options, changed launch count or instruction count, missing simulator completion, inconsistent repeated per-kernel counter vectors, and malformed counters.

## Prospective sensitivity result

| `-dram_latency` | Total simulated cycles | Cycle change vs baseline | L1D miss counter | L2 miss counter |
|---:|---:|---:|---:|---:|
| 100 (unchanged baseline) | 28,717 | 0.000% | 3,534 | 129 |
| 200 | 28,950 | +0.8114% | 3,534 | 129 |
| 400 | 29,316 | +2.0859% | 3,534 | 129 |

All three configurations execute **1,059,640 simulated instructions** over the same four launches. Two repeats per configuration completed, and the independent per-kernel counter auditor passed. The preregistered directional and monotonicity predictions both **survived**. The miss counts were identical across the variants, so this test changes simulated service latency without changing the reported demand counters. The baseline repeats need not have identical *log bytes* because wall-clock rate fields vary; the independent semantic counter vectors match.

Across the tested interval, the secant response is **599 / 300 = 1.9967 total simulated cycles per added unit of configured DRAM latency**. This is an empirical response slope for one fixed simulator workload, **not** a portable architectural law. The effective log-elasticity from 100 to 400 is **0.01489**. The 100→200 and 200→400 secant slopes differ (2.33 vs 1.83), so a globally linear relationship is not established.

## Decision

This experiment provides **a negative constraint on exaggerated memory-latency optimization claims**: a fourfold modeled DRAM-latency setting increases the workload's total simulated cycles by only **2.09%**. The observation is consistent with considerable latency hiding or non-DRAM work, but does **not** identify which resource dominates. The experiment does not vary actual DRAM bandwidth, port pressure, occupancy or hardware timing, and it does not show that eliminating memory latency would yield a particular speedup. Do not extrapolate the local secant to zero latency or to a different workload.

**No new V309 hardware mechanism is promoted.** Before physical qualification, obtain a matched second workload and an equal-resource candidate/control comparison with repeated cycle counters, followed by RTL/synthesis/timing/electrical evidence and hardware calibration. Do not revive historical V287/V296, claim a physical speedup, or assert RTX 5090 equivalence. Kernellum PR #119 remains separate.
