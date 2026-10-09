# Vektor-070 — finite receiver deduplication and UID reuse fence

Evidence date: 2026-10-10. Experiment classes: DISCRIMINATION, CAPABILITY-BUILDING, EXPLOITATION. No personal spend.

## Mechanism and prediction
Vektor-069 retransmits DATA after ACK loss but assumes unbounded receiver dedup history. Finite UID wrap makes old and new packets observationally indistinguishable when the same UID is reused. A trusted post-retirement fence must certify that all older DATA/ACK copies are terminal and no older producer can emit more. This is a necessary identity-lifetime condition, not an original transport invention.

## Outcomes (synthetic event simulation)
96 structured runs, 12 minimally guided probes (12.5% of structured budget). Strong fence: 18,197 retirements, 0 stale-origin DATA credits, 0 stale-origin ACK credits. Unsafe early reuse: 17 false DATA and 15 false ACK credits across 8/48 runs.

Preregistered holdout: 24 unseen paired strong/early runs plus 12 strong mid-flight reset runs. P1/P2/P3 PASS: strong 5,236 retirements and 0 false credits across 36 runs; early reuse 255 false DATA and 115 false ACK credits across 7/24 runs. These are software-simulated, not measured hardware, and share the same simulator implementation.

## RTL boundary
`rtl/receiver_dedup_070.sv` implements one bounded active UID, one delivery bit, re-ACK of duplicate DATA, and a fresh post-retirement fence token. `rtl/reliable_sender_069.sv` is the experimental retry sender. Directed receiver and integration benches exercise ACK loss, retry, forced same-UID reuse and fencing. An external router must certify `fence_ack`; this component does NOT establish its truthfulness. Integration is zero-latency and lacks realistic packet queues.

## Discovery Protocol V2
- KNOWN (model): tag-only early reuse can credit stale DATA/ACK; conditional strong-fence runs show zero stale-origin credits.
- BELIEVED: bounded receiver + truthful quiescence is sufficient for safe reuse with terminal accounting and producer closure.
- CONFLICTING: aggressive reuse may increase modeled capacity but violates safety; conservative fences may reduce occupancy.
- FALSIFIED: finite tag-only dedup always distinguishes wrapped transactions; ACK receipt proves no older physical copies remain.
- ANOMALOUS: stale DATA and stale ACK arise in distinct latency/clone regimes; identify regime boundaries next.
- UNTESTED: truthful router terminal reports, broken fence tokens, bounded hardware packet queues, formal RTL equivalence, timing, physical area, power, multi-tile scaling.

Explorer: bounded receiver; Skeptic: UID-wrap indistinguishability; Experimentalist: clone/loss/latency sweep; Analyst: model-only claim; Anomaly Hunter: ACK/DATA failure split; Prior-Art Auditor: known transport mechanisms; Replicator: independent event-model replication pending; Theorist: identity lifetime must not overlap reuse.

## External target ledger (NVIDIA official specs checked 2026-10-10)
RTX 5090: 21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit interface, 575 W TGP, fifth-gen Tensor with marketed 3,352 AI TOPS, fourth-gen RT with marketed 318 RT TFLOPS. Official: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/

Vektor-1A 160 x 128 x 2 x 2.56 GHz = 104.8576 TFLOPS is peak arithmetic projection only. 128 MB L2, 2.56 GHz, <=575 W, <=750 mm2 remain hypotheses. FP32, tensor by datatype/sparsity, memory bandwidth/capacity, cache, raster/texture, ray, physical PPA, KPX and software execution: **INCONCLUSIVE**.

## Single next decisive action
Validate directed RTL and generic synthesis on free GitHub Actions, then integrate a bounded router with verified quiescence token production and formally test reset, replay, loss, UID wrap and backpressure. Main remains unchanged.
