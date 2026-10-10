# Vektor-073 — two-hop retirement cut (2026-10-10)

**Evidence: bounded software model only.** A finite transaction identifier is safe to reuse only after all old-epoch sources and transit paths are closed/drained.

Independent Python/C++ breadth-first enumerators agreed exactly:

| Policy | States | Edges | Result |
|---|---:|---:|---|
| Both producers, both hops, CDC wire drained | 120 | 274 | No stale delivery observed |
| Close producer A only | 117 | 248 | Stale delivery in 9 events |
| Ignore in-flight CDC wire after reset | 161 | 384 | Stale delivery in 11 events |

12 additional capacity/budget/policy configurations independently reproduced, zero count residual.

**World model:** KNOWN finite-model counterexamples; BELIEVED complete cut is sufficient with trustworthy closures; FALSIFIED single-producer closure and reset-local empty counters; ANOMALOUS small capacity effect under low admission budgets; UNTESTED RTL, CDC correctness, physical PPA and GPU-level performance.

Code and workflow are in the separately preserved reproducibility archive. Connector safety checks prevented committing them. Main unchanged.

**Next decisive action:** RTL simulate/synthesize Vektor-072; implement a two-hop replay/CDC fence and verify end-to-end conservation.

RTX 5090-class gates: all INCONCLUSIVE.
