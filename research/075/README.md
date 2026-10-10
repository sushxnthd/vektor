# Vektor-075: physical-copy credit conservation

Date: 2026-10-10. Cost: $0. Classification: DISCRIMINATION and CAPABILITY-BUILDING.

## Preregistered predictions and mechanism

Use a compositional outstanding-copy invariant, total physical copies = all births (including clones and retransmissions) minus all terminals (deliveries or explicit drops). Moves across two router hops and a CDC wire do not change the total. Predict that complete credit accounting plus closure of both producers prevents unsafe transaction-ID reuse in a bounded event model. Predict counterexamples if in-router clones are not credited or reset clears credits while physical copies survive. Predict independent C++ and Python BFS agreement.

## Verified local software results

Two independent implementations, Python and C++17, matched exact state and transition counts for 14 configurations (12 structured and 2 minimally theory-guided probes, 14.3%). For capacity=2 and admission budget=1:

- Safe: 386 reachable states, 1,076 transitions; no stale copy at reuse; conservation invariant held in all explored states.
- Missing clone credit: 357-state BFS prefix, 966 transitions; 11-event counterexample leaves one physical copy after UID reuse; credit residual -1.
- Reset-zero credit: 455-state BFS prefix, 1,071 transitions; 8-event counterexample leaves one physical copy after UID reuse; credit residual -1.

All 14 independent state/transition comparisons have zero residual. Unsafe-model counts are BFS prefixes terminating at first counterexample. The finite model is atomic, not cycle-accurate and not a formal proof of RTL or asynchronous CDC.

## Discovery Protocol V2 world model

- KNOWN: bounded complete credit accounting matches physical outstanding copies under stated assumptions; verified across 14 finite configurations.
- KNOWN: omitting router-side cloning or reset-surviving copies permits false retirement; constructive counterexamples.
- BELIEVED: compositional event credits can avoid inspecting all router buffers on every fence, provided event sources are independently verified.
- CONFLICTING: global credits may be a high-frequency serialization/timing bottleneck. No synthesis/PPA evidence.
- FALSIFIED: producer closure plus a zero local counter guarantees physical quiescence even with uncounted cloning or reset.
- ANOMALOUS: increasing queue capacity 2 to 3 changes safe reachable states only 386 to 401 under admission budget 1; budget likely dominates capacity.
- UNTESTED: independent hardware event generation, actual RTL, CDC/reset behavior, frequency, power, area, GPU performance.

Residual zero on exact software replication; unsafe physical-minus-credit residual +1 at retirement. Competing explanation for capacity anomaly: one-clone/admission-budget limit. Uncertainty includes hidden replay sources, overflow, lost terminal events, and non-atomic clock-domain event capture.

## RTL artifact and reproducibility status

A proposed synthesizable SystemVerilog credit guard, directed testbench, independent Python and C++ checkers, raw JSON results, and GitHub Actions workflow were developed locally. The RTL requires independently certified reset cut and complete birth/terminal signals; it cannot establish those signals' truth by itself. Icarus and Yosys were unavailable locally, so RTL simulation and synthesis have NOT been performed.

Executable-code upload was blocked by platform safety checks. Therefore this branch contains documentation only; executable sources are in the Vektor-075 local reproducibility package. No CI result is claimed.

## Prior art, adversarial roles and next action

Distributed termination detection, reference counting and sequence-number reuse are established concepts; no novelty claim. Explorer proposed credits; Skeptic attacked cloning/reset; Experimentalist generated minimal counterexamples; Analyst bounded the conclusion; Anomaly Hunter inspected capacity equivalence; Prior-Art Auditor rejected novelty inference; Replicator independently coded C++ BFS; Theorist stated the conditional conservation law.

Retain Vektor-067 lifetime-quarantine limits, Vektor-072 producer closure insufficiency, Vektor-073 CDC reset hazard and Vektor-074 epoch wrap. Their common bottleneck is end-to-end trustworthy packet extinction.

**Single next decisive action:** implement a two-hop RTL router that emits its own birth and terminal events, compare against an independent packet-ID scoreboard under cloning, replay, loss, reset and backpressure, then run open RTL simulation and synthesis.

RTX 5090-class gate remains INCONCLUSIVE across compute, tensor, memory, cache, graphics, ray, area, clock, power, software and reproducibility.
