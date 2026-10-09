# Vektor-066 — bidirectional ACK replay (Discovery Protocol V2)
Date: 2026-10-09. All rates are synthetic software-model transactions/cycle, **not GPU IPC**. RTL authored, not silicon.

## Mechanism / preregistration / evidence

Vektor-065 counted physical DATA replicas but assumed ACKs never replay. Vektor-066 generates delayed, lossy, replicated DATA **and ACK** packets; sender retransmits DATA after timeout. The receiver deduplicates by immutable transaction UID. The sender requires full (tag, UID) ACK matching and closed DATA quiescence before tag reuse.

| ID | Preregistered prediction | Outcome | Residual and uncertainty | State |
|---|---|---|---|---|
| H1 DISCRIMINATION | Full immutable UID prevents stale ACK false credit | 0 false credits in 288 structured and 36 exploratory software-model configurations | 0 against prediction; assumes no UID wrap and unbounded receiver dedup history | KNOWN within model |
| H2 DISCRIMINATION | DATA quiescence alone cannot prevent tag-only replayed ACK miscredit | 43,964 false ACK credits in 16 adversarial tag-only simulations in the full package | falsifies unconditional tag-only safety; simplified link | FALSIFIED |
| H3 EXPLOITATION | Higher ACK loss increases retry pressure | 16/16 paired full-package tests regressed (ACK loss 0 to 0.6) | stochastic; not a universal monotonicity theorem | BELIEVED |
| H4 SURPRISE | No delivery fairness means no unconditional progress | 0 completions with all ACKs dropped | exact directed liveness counterexample | KNOWN |
| H5 DISCRIMINATION | Finite UID width is safe without replay bound | Independent C++ predicate oracle: 256/256 aliases after 8-bit wrap; 1,044,480 distinct-ID comparisons had zero full-ID alias vs 261,120 tag-only aliases | full UID alone cannot prevent wrap alias | FALSIFIED |

Full local reproducibility package also includes 16 loss pairs, 36 random probes (12.5% of structured budget), raw results, and a second extended model. The compact repository model reproduces the same mechanism and sweep, but may not have byte-identical stochastic results because it uses a separately edited driver.

## World model

**KNOWN:** DATA-side quiescence does not imply ACK-side quiescence. **BELIEVED:** bounded receiver tombstones plus a fabric-wide replay horizon can enable finite storage. **CONFLICTING:** full UID prevents modeled miscredit, but requires no UID wrap during stale-ACK lifetime and receiver deduplication state that the toy model never evicts. **FALSIFIED:** tag-only ACK matching remains safe under arbitrary replay; full finite-width UID is unconditionally safe. **ANOMALOUS:** the ACK path exposes an independent lifetime hazard after DATA retirement. **UNTESTED:** bounded receiver history, ACK replay fences, reset, congestion, formal proof, timing, PPA, GPU throughput.

## Adversarial roles and prior art

Explorer: full-UID ACK and DATA quiescence. Skeptic: UID wrap, hidden replay, receiver storage, reset. Experimentalist: tag-only ablation and loss pairs. Analyst: preserve failures and distinguish model from RTL. Anomaly Hunter: ACK-side lifetime hazard. Replicator: independent C++ predicate oracle and directed SystemVerilog. Theorist: tag reuse is safe only when old responses are impossible **or distinguishable**. Prior-Art Auditor: source IDs and response matching already exist in OpenTitan TileLink-UL (https://opentitan.org/book/hw/ip/tlul/doc/TlulProtocolChecker.html); NoC contention modeling exists in gem5 Garnet (https://www.gem5.org/documentation/general_docs/ruby/garnet-2/). **No novelty claim.**

## Next decisive action

Integrate a bounded receiver UID tombstone and ACK replay-retirement fence, test UID wrap and ACK loss under equal finite storage budgets, and verify full end-to-end RTL. Preserve Vektor-1A as an unvalidated architecture hypothesis. RTX 5090-class gates: all INCONCLUSIVE.
