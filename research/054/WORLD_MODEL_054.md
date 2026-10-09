# Vektor-054 — Discovery Protocol V2 world model

**Date:** 2026-10-09. **Classification:** CAPABILITY-BUILDING / DISCRIMINATION / EXPLOITATION.
**Evidence type:** deterministic Python transaction simulation and an independently coded packed-state interpreter. RTL candidate and testbench exist; **RTL simulation and synthesis are pending**.

## Evolving claims

| State | Claim and scope |
|---|---|
| KNOWN (model) | 24 independent trace comparisons, 60,000 cycles, zero reference/replica mismatches; zero-alias controls exactly equal for three seeds. |
| KNOWN (model) | Tagged returns preserve correct source data in the tested two-slot model with out-of-order returns and variable backpressure. One intentionally invalid response per trace is detected by a sticky error bit. |
| BELIEVED | Tagged source dedup/fanout can reduce read demand when same-instruction physical register aliases occur, subject to implementation cost and compiler statistics. |
| CONFLICTING | The 053 idealized 100%-alias read reduction was 66.7%, but this 054 model's *total* reads fall only 51% because more instructions complete. Normalize per instruction before interpreting traffic. |
| FALSIFIED | Reducing per-instruction read count by 3x necessarily triples throughput: 100%-alias case improves modeled completions only 47.22% because two collector slots, response latency and backpressure become limiting. |
| ANOMALOUS | Across seeds the 25% alias regime improves modeled completions only 5.77% while physical read demand per completed instruction decreases approximately 16.7%; suggests occupancy/latency bottleneck migration. |
| UNTESTED | RTL compile, differential simulation, generic synthesis, critical path, area, power, physical bank mapping, real compiler alias rates, shader/ML traces, tensor/graphics/ray performance. |

## Experiment 054A: tagged two-slot fanout (CAPABILITY-BUILDING / DISCRIMINATION)

**Mechanism.** Issue instruction (tag, 3 physical source IDs); collect each distinct ID once when DEDUP=1, or all three logical operands when DEDUP=0. Every return carries tag, operand index, source ID, and value. Return fanout is restricted to matching source IDs **within the same live instruction**. A completion may retire only after all three operands are received.

**Predictions:** exact 0% alias control; fewer read requests under aliases; no instruction-identity mixing; invalid/stale return rejected. See PREREGISTERED_054.md for timing caveat.

**Outcome:** 24 x 2500-cycle traces, three seeds and four alias levels, each with DEDUP on/off. A separate packed-state Python model matched all 60,000 expected cycle outputs. Three 0%-alias pairs have exactly equal accepted instructions, reads and completions. At 25%, 50%, 100% alias, modeled completion gains are +5.77%, +16.35%, +47.22%. One deliberately invalid response per trace sets the sticky error. The 100%-alias regime is not an empirical workload estimate.

**Residual:** zero mismatches against independent software interpreter, zero difference in 0%-alias controls. No RTL residual is available because HDL tools could not run locally. **Uncertainty:** synthetic offered instruction stream, deterministic pseudo-random return/backpressure, only two collector slots, one request port, no banks, no scoreboard or execution pipeline. The independent replica shares the architectural specification, so common-mode specification errors remain possible.

**Assumptions weakened/falsified:** per-instruction RF traffic alone does not determine completion rate. Two-slot occupancy and response latency can dominate. **Competing explanations:** head-of-line blocking, completion backpressure, outstanding return distribution, and synthetic alias rates. The current design cannot distinguish all of them.

**Cheapest discriminating experiment:** run Icarus differential RTL vectors, then equal-budget Yosys generic synthesis with DEDUP 0/1; separately add 4/8/16 collector slots to the software model to isolate occupancy from read-port pressure. Extract compiler-derived source-register traces before any claim of real GPU benefit.

## Adversarial roles

Explorer: source-ID dedup and tag-qualified return fanout as testable mechanism.
Skeptic: questions synthetic alias rates, two-slot representativeness, area/frequency overhead and absence of bank contention.
Experimentalist: equal instruction streams and zero-alias controls; malformed response injection; 24 deterministic traces.
Analyst: reports both total reads and completions, not only selected speedups.
Anomaly Hunter: identifies 100%-alias non-triple throughput and 25%-alias weak throughput gains as bottleneck migration.
Prior-Art Auditor: GPGPU-Sim and existing operand collectors predate Vektor; no novelty claim.
Replicator: separately coded packed-state model; 60,000 cycle-level comparisons.
Theorist: the read-port ceiling is bounded by distinct source count, but achievable instruction rate also depends on collector occupancy, return latency and completion backpressure.

## Bottleneck cluster and branches

Vektor-047 to -054 repeatedly expose coupled RF credit, partial operand collection, wave occupancy, and return bandwidth. First-grant RR and phase-dither scheduling are retained as conditional/negative branches, not forgotten. The priority is tagged collector correctness and PPA, not another scheduler-only sweep.

## Foothold assessment

**Capability-building foothold (software only):** deterministic tagged-return and source-alias reference harness with an independently checked 60,000-cycle suite. No hardware-performance foothold or 5090-class gate advancement until RTL verification and synthesis succeed.

**Single next decisive action:** differential RTL simulation and equal-budget generic synthesis of tagged DEDUP=0 and DEDUP=1.
