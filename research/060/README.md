# Vektor-060 — cancellation-drain versus epoch-only response reuse

Date: 2026-10-09. Parent: Vektor-059. Status: software-model DISCRIMINATION; RTL proposed, not verified.

## Preregistered hypotheses
H60-A: A 2-bit generation counter alone cannot prevent a stale canceled operand response from being credited after four slot reuses. Expected: explicit ABA counterexample.
H60-B: Holding a canceled instruction slot until all previously issued responses are acknowledged prevents incorrect crediting under **exactly-once delivery**, arbitrary reordering and eventual return. Expected: zero false credits in bounded exhaustive and randomized tests.
H60-C: Drain/quarantine reduces slot allocation opportunities under delayed responses. Expected: fewer successful allocations than eager reuse for the tested offered-load generator.

## Measured software-model outcomes
- Explicit epoch-wrap counterexample: old generation-0 response was falsely credited to a later generation-0 instruction; its legitimate response was subsequently rejected as a duplicate.
- Exhaustive 20-event search, one slot, two operands, two epoch bits: eager reuse 113,592 reachable states, 610,570 explored transitions, 27,092 false-credit edges; drain/quarantine 47 states, 76 transitions, **zero** false-credit edges.
- 384 deterministic random traces × 2,000 events = 768,000 events. Eager reuse: 5,311 false credits and 59,377 allocations. Drain/quarantine: **zero false credits** and 47,517 allocations. These allocations are not equal-workload performance measurements; traffic diverges after scheduling decisions.
- Independent transaction-ownership oracle matched the tag/seen-bit implementation in all randomized traces.

## Scope and limitations
A fixed-width epoch is not sufficient if arbitrarily late duplicates may arrive after acknowledgments and wrap. Drain/quarantine is safe only under the stated exactly-once transport/acknowledgment contract; lost responses can block a slot indefinitely. RTL simulation, formal verification, synthesis, performance, area and frequency are unverified. The effect is a standard ABA/protocol-safety issue, not a novelty claim.

## Discovery Protocol V2
KNOWN: epoch wrap causes ABA under eager reuse with unbounded stale returns.
BELIEVED: drain-on-cancel is a viable bounded resource reclamation protocol under exactly-once delivery.
CONFLICTING: low-overhead eager cancellation versus guaranteed response identity.
FALSIFIED: a 2-bit epoch alone prevents all stale response misrouting.
ANOMALOUS: false credit causes subsequent correct response rejection.
UNTESTED: duplicated packets, lost packets, distributed NoC reorder, physical timing, integrated tagged collector, and long-lived GPU workload traces.

Mechanism: canceled in-flight operand remains valid after its instruction slot is reused and its epoch wraps.
Prediction: eager false credit, drain zero false credit; observed as above, residual zero for qualitative predictions.
Competing explanation: network duplicate/replay or malformed return tag; neither is needed for the counterexample.
Uncertainty: transport contracts and traffic realism; zero false credits do not establish liveness.
Cheapest next discrimination: run directed RTL test and model-check slot release/credit under exactly-once and explicit drop/duplicate adversaries.

Adversarial roles: Explorer proposes draining tombstones; Skeptic attacks loss/duplication assumptions; Experimentalist enumerates arbitrary response orders; Analyst retains allocation-cost caveat; Anomaly Hunter identifies ABA after epoch wrap; Prior-Art Auditor notes standard tagged transaction techniques; Replicator independently tracks physical packet ownership; Theorist states the invariant: a slot cannot be reallocated while any old response may still arrive.

RTX 5090-class gate: INCONCLUSIVE across compute, tensor, graphics, ray, memory, software and PPA. Vektor-1A remains hypothetical.
