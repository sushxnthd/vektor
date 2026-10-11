# Vektor-101B: return-producer scaling law and saturation boundary

Date: 2026-10-11. Classification: **DISCRIMINATION + EXPLOITATION**.
This experiment extends V098/V100 return-fabric models. It is a
software cycle-model study, not GPU throughput, RTL or silicon measurement.

## Frozen predictions, discovery and holdout

Controlled sweep: 81 configurations = sources {1,2,4} x copies {1,3,7}
x sink-hold {0,0.4,0.8} x 3 deterministic seeds. Ten additional
minimally guided probes (10/91 = 10.99%) varied source count, depth,
tag count, copies, age guard, hold and burst.

Pre-registered discovery predictions and outcomes:

| Prediction | Threshold | Observed | Residual / status |
|---|---|---:|---|
| P1: four vs one producer, 1 beat, no sink hold | ratio >=1.30 | 1.763585 | +0.463585 / PASS |
| P2a: four vs one, 3 beats, 80% hold | ratio <=1.10 | 1.076555 | -0.023445 / PASS |
| P2b: four vs one, 7 beats, 80% hold | ratio <=1.10 | 1.005128 | -0.094872 / PASS |
| P3: increasing hold reduces completions, 4 producers | strictly monotone | 3 and 7 beats | PASS |

For 4 producers and 3 beats, mean completions were 2139 (0% hold),
1309 (40% hold), 450 (80% hold). With 7 beats they were 920, 564, 196.

**Unseen holdout**: depth=8, tags=16, guard=32, burst=113,
cycles=10000, seeds 8801/8802; sources {1,4}, copies {1,3,7},
hold {0.1,0.75}. All 24 configurations independently replicated
against the V100 C++ implementation. Frozen predictions:

| Condition | Prediction | Observed ratio | Status |
|---|---|---:|---|
| 1 beat, 10% hold | 4/1 >1.40 | 1.762107 | PASS |
| 7 beats, 75% hold | 4/1 <1.08 | 1.020000 | PASS |
| 3 beats, 75% hold | 4/1 <1.15 | 1.025111 | PASS |

All 91 discovery/exploratory configurations and 24 holdouts matched
independent C++ aggregate outputs exactly (115/115). The models share
the same high-level architectural assumptions; replication is not
independent RTL or physical validation.

## Mechanism, competing explanations and uncertainty

One producer has a packetizer turnaround bubble after each request.
Independent producers can hide that bubble. Once a shared one-beat
return port is saturated, adding producers cannot increase its
service rate; periodic sink blocking makes the shared service bottleneck
more severe. This is a conditional bottleneck law, not novel hardware.

Alternative explanations: tag capacity, finite launch queue, deterministic
offer pattern, and arbitration priority can also limit completions.
A direct no-stall one-versus-four RTL test with matched total buffering
is required before attributing all improvement to bubble hiding.

## World model

- KNOWN (model): the pre-registered saturation/turnaround predictions
  passed discovery and unseen holdout with exact C++ replication.
- BELIEVED: source parallelism should be allocated where producer
  turnaround dominates, not when return bandwidth is already saturated.
- CONFLICTING: source count also changes storage and area, so completion
  counts alone cannot establish an equal-resource advantage.
- FALSIFIED: unconditional assumption that four producers always give
  large gains over one; 7-beat/75%-hold holdout showed only 2% gain.
- ANOMALOUS: in directed V101 RTL, 2/4/8 producers all admitted 562
  transactions under the same heavy-hold 3-beat scenario.
- UNTESTED: equal-area tradeoff, realistic GPU writeback mix,
  formal quiescence, physical timing and broad 5090 capability.

## Reproducibility and evidence hashes

The complete executable V100 model, independent C++ source, V101B
Python sweeps, frozen preregistration and raw JSON are in the
Vektor-101 reproducibility archive associated with this run.

Discovery JSON SHA256:
ebf57394cab437a8b99dab3b963a2ae0151b99f4d6b18dfcd557502d5276318a

Holdout JSON SHA256:
76c8db5461968a56fde588ae2eafe8202ae291c4d326800cf6daf25d562916eb

**Single next decisive experiment:** build a one-producer RTL variant,
compare 1/2/4 sources under matched buffering and synthetic plus
realistic writeback workloads, then measure generic synthesis and
timing on a pinned open-cell technology. No GPU-class gate advanced.
