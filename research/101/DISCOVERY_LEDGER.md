# Vektor-101: composed RTL discrimination and evidence gate

Date: 2026-10-11. Classification: **DISCRIMINATION / CAPABILITY-BUILDING**.
Parent: Vektor-100 software model, Vektor-099 cancellation precedence, Vektor-098 composed return network.

## Preregistered mechanism and predictions

Hypothesis H101-A: Under a trusted cold-reset flush, one FINAL per accepted
request, producer-held ready/valid, and eventual sink service, replacing
FINAL-wins retirement with cancellation-wins retirement should change
**only completion classification** on a same-cycle live FINAL/cancel event.

Predictions frozen before RTL CI:
1. All 5 directed source/depth/copy configurations drain with grants == FINALs,
   FINALs == completions + stale drops, and beats == COPIES * FINALs.
2. With the same external traffic, the old and new fabrics have identical
   grants, tag ownership, dispatch and return handshakes.
3. The exact difference in live completions equals the number of live FINALs
   coinciding with cancellation. A mutation using FINAL-wins violates this
   rule but remains a valid implementation under a different API contract.
4. Held ready/valid output is stable through stalls.
5. Generic Yosys cell counts are recorded as logic-complexity indicators
   only; no area, frequency, power or performance equivalence is claimed.

## Independent comparison and assumptions

The same source stimulus drives both RTL compositions; the only intentional
difference is consumer precedence. This is a *differential policy check*,
not an independent implementation of the fabric. The earlier V100 Python/C++
models are separate evidence and may share architectural assumptions.

A counterexample or mismatch will be preserved, not silently suppressed.
Negative controls: the V098 FINAL-wins consumer and configurations with
no cancel/FINAL collisions. The former must differ only on the specified
race; the latter must match exactly.

Known limitations: the RTL does not prove quiescence, exactly-once FINAL,
cross-clock correctness, reset-safe replay, or unbounded liveness.
Parameter restrictions: SOURCES>=2, power-of-two DEPTH>=2, COPIES in [1,15].

## World model

- **KNOWN:** Software V100 demonstrated incarnation-order sensitivity;
  RTL and physical evidence were absent before this run.
- **BELIEVED:** The composed V100 design conserves transactions under
  the stated source/return protocol assumptions.
- **CONFLICTING:** FINAL-wins and cancel-wins are both coherent APIs;
  choosing one requires an externally specified cancellation contract.
- **FALSIFIED:** Cancellation after same-cycle reuse is safe without
  generation semantics (V100 counterexample).
- **ANOMALOUS:** High rates of same-cycle tag reuse in synthetic stress
  make the boundary easy to exercise; field frequency is unknown.
- **UNTESTED:** Unbounded proof, external flush correctness, physical PPA,
  full GPU integration and all RTX 5090-class gates.

## Adversarial roles

Explorer: compose independent existing blocks. Skeptic: question flush
assumptions and testbench independence. Experimentalist: sweep producers,
depth and copies with controlled backpressure. Analyst: separate simulated
and synthesized results from GPU throughput. Anomaly Hunter: investigate
unexpected queue occupancy, grant/FINAL mismatch and stalled output drift.
Prior-Art Auditor: ready/valid, FIFO elasticity and cancellation priority
are established protocol concepts, not novelty claims. Replicator: rerun
Python/C++ models and CI independently. Theorist: tag ownership must be
linearized against the pre-edge transaction incarnation.

## Target ledger (rechecked 2026-10-11)

NVIDIA's official GeForce RTX 5090 specification:
https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit interface,
3,352 AI TOPS (precision/sparsity conditions not established here),
318 RT TFLOPS (not interchangeable with raster throughput), and 575 W
total graphics power. The published top-level page does not establish
comparable measured Vektor FP32, per-datatype tensor, memory bandwidth,
L2/cache, texture/raster, ray workload, area, frequency or software
execution capability. Vektor's 104.8576 TFLOPS FP32 arithmetic projection
assumes 160*128*2*2.56 GHz FMA counting and full utilization.

All RTX 5090-class gates: **INCONCLUSIVE**.

## Single next decisive action

Execute CI RTL simulation and generic synthesis; if a counterexample
appears, minimize it and revise the composed contract. If green, add a
formal/bounded property harness with adversarial source quiescence and
cancel/reuse, then compare area-normalized throughput on realistic GPU
writeback traffic. No personal expenditure.
