# Vektor-097 discovery ledger (2026-10-11)

Class: DISCRIMINATION / CAPABILITY-BUILDING.

Mechanism: V096 dynamically reprioritizes FINAL/debt arbitration even when downstream is stalled. A newly offered FINAL can replace a nonfinal beat already presented without handshake. Locking the source on first stall preserves beat identity, conditional on upstream hold-until-ready.

Preregistered P1: old design fails on a legal two-source trace. **Observed:** 9,088 output-stability violations across 32,768 bounded five-cycle traces; example offers (0,0,0,2,1), with bit2 indicating ready. P2: sticky design has zero violations. **Observed:** zero in the same bounded traces and 16,384 held-valid random cycles. P3: always-ready arbitration matches. **Observed:** 20,000 matching cycles. C++17 independently matched 16,384 generated cycle outputs. Residual against predictions: zero observed; these are software results.

Competing explanations: issue admission was not changed; the violation is output reprioritization during a stalled transfer. No silicon, GPU throughput or timing inference. The sticky repair can defer a later FINAL. Alternative: register payload in a skid buffer; adds storage and potentially latency.

World model:
- KNOWN: V096 ready/valid stability is false under legal backpressure.
- BELIEVED: source-lock RTL implements the reference if producers hold their payload.
- CONFLICTING: V096 simulated fairness improvement coexists with protocol invalidity.
- FALSIFIED: V096 RTL is safe for direct ready/valid composition.
- ANOMALOUS: equal aggregate short-trace acceptances despite correctness difference.
- UNTESTED: unbounded formal properties, composition, PPA, 5090-class.

Roles: Explorer source-lock; Skeptic reset and producer assumptions; Experimentalist exhaustive legal traces; Analyst avoid GPU claims; Anomaly Hunter threshold crossings; Prior-Art Auditor notes standard elastic buffering; Replicator C++ model; Theorist hold payload until handshake.

**Next decisive action:** run RTL equivalence and generic synthesis, then compose with V095 elastic FIFO.
