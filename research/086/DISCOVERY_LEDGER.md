# Vektor-086 — Discovery Protocol V2 ledger

**Date:** 2026-10-10. **Classification:** CAPABILITY-BUILDING + DISCRIMINATION + SURPRISE. **Cost:** $0. **Branch:** `research/wb-calendar-086`.

## Experiment 086-A: completion-time reservation correctness

**Mechanism:** issue-time bank/latency reservations in a sequential shift calendar prevent future writeback-port oversubscription, assuming fixed known completion latency and no cancellation.

**Preregistered prediction:** 4,096 default and 2,048 alternate cycles exactly match an independent absolute-cycle dictionary oracle for both grant vectors and current-cycle due counts. Reset clears pending writes; invalid latencies are rejected; due per bank never exceeds port capacity.

**Outcome (RTL SIMULATED):** PASS. Default **4,096/4,096**, alternate **2,048/2,048** exact cycles. **Residual:** 0 mismatched cycles in both. Source commit `5cc1b0dfd1b95614d1a2c584e146d04e176bb42a`. [Independent GitHub Actions evidence](https://github.com/sushxnthd/vektor/actions/runs/38055424976).

**Oracle outcomes (PYTHON-MODELED, not hardware throughput):** default offered/accepted: hotspot 500/125, spread 512/512, staggered 512/131, invalid 512/0, random 6182/3483, surprise 1034/458. Alternate: hotspot 372/124, spread 378/378, staggered 384/135, invalid 384/0, random 4586/3039, surprise 747/462. Probes: 512/4096 and 256/2048 = **12.5%**.

**Uncertainty:** two parameterizations, synthetic inputs, no writeback payloads, no variable latency or cancellation, no integrated register hazard semantics. **Competing explanations:** correctness follows from trivial fixed-latency calendar accounting; not a novel GPU performance effect. **Next discriminator:** implement cancellation/late-completion and independently compare event traces with payload identities.

## Experiment 086-B: synthesis feasibility

**Preregistered prediction:** the sequential calendar is synthesizable by free Yosys. **Outcome (SYNTHESIZED, generic):** PASS. Yosys 0.33 `synth -top rf_wb_reservation_086` reports **694 generic cells**, including **16 DFF** for default parameters. **Residual:** qualitative prediction met; no quantitative preregistered cell target. **Uncertainty:** no standard-cell library, timing closure, routing, frequency, power, or area. **Next discriminator:** synthesize multiple parameterizations and compare with an equivalent counter-based baseline under the same constraints.

## Experiment 086-C: starvation counterexample

**Preregistered prediction:** fixed request-index priority can starve lower-index clients. **Outcome (PYTHON-MODELED):** four persistent requests for bank 0, latency 1, one port: grant counts over 1,000 cycles **[1000, 0, 0, 0]**. The same holds for latencies 2 and 4. **Residual:** none; this is a counterexample, not an empirical throughput law. **Assumption falsified:** correctness of capacity scheduling implies acceptable fairness. **Competing explanation:** a real upstream scheduler might rotate request mapping, but no such guarantee exists in this module. **Next discriminator:** fair round-robin vs fixed priority, same reservation capacity, synthetic and compiler-derived traces.

## Evolving world model

- **KNOWN:** 086-A exact oracle agreement for two bounded RTL traces; 086-B generic synthesis success; fixed-priority starvation in the independent model.
- **BELIEVED:** reservations can avoid some modeled future writeback queue stalls in workloads like Vektor-085, conditional on accurate completion timing.
- **CONFLICTING:** Vektor-085 reservation holdout had 47 wins, 17 losses, 32 ties; it is not universally beneficial.
- **FALSIFIED:** 079 large scheduler anomalies survived realistic coherence (no); 082 uncapped collector throughput as execution throughput (no); 083 equal-storage FIFO universal win (no); 084 elastic bypass sustained throughput win (no).
- **ANOMALOUS:** persistent request-index starvation despite correct per-cycle bank capacity; investigate scheduler fairness and mapping sensitivity.
- **UNTESTED:** formal sequential safety proof; age/generation tags; cancellation; variable-latency completions; coherent RAW/WAW integration; matrix/vector arbitration; physical PPA; compiler-driven workloads; GPU-level capabilities.

## Adversarial review

Explorer: future completion slot reservation. Skeptic: fixed latency and unfair arbitration are strong hidden assumptions. Experimentalist: same-bank same-slot collisions, cross-cycle collisions, distinct latency, reset, invalid, alternate port count. Analyst: no GPU performance claim from calendar correctness. Anomaly Hunter: index starvation and admission phase boundaries. Prior-Art Auditor: resource calendars/scoreboards are established; no novelty claim. Replicator: independent absolute-cycle event dictionary rather than RTL shift register. Theorist: if every accepted write finishes at its reserved cycle, accepted completions per bank per cycle cannot exceed P ports.

## Single next decisive action

Implement and verify a **fair, cancellable** reservation controller with identity tags, then integrate with Vektor's coherent pipeline. 5090-class gates: compute, matrix, memory, graphics, ray tracing, software, frequency, area and power **INCONCLUSIVE**.
