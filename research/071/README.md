# Vektor-071 — bounded router and physical-copy conservation

Date: 2026-10-10. Class: DISCRIMINATION / CAPABILITY-BUILDING. Spend: $0.
Parent: Vektor-070. Status: model verified locally; RTL/CI requires GitHub Actions.

## Preregistered predictions (before GitHub CI)
P1. Two accepted DATA copies create occupancy 2. Dropping one copy does not erase the other.
P2. Delivering the first of two ACK copies does not establish quiescence.
P3. The fabric reports quiescence only after both bounded physical queues drain, both producer channels are closed, and no externally modeled in-flight packet remains.
P4. An integrated sender/receiver with duplicate suppression and retry can complete two same-UID transactions when a physical-copy fence is respected.
P5. Independent deque and indexed-ring models agree on 1,200 deterministic 200-cycle traces.

## Mechanism and boundary
A strong fence is a **physical terminal-accounting contract**, not a synonym for sender closure or first ACK arrival. This block models two finite FIFO links (DATA and ACK), with an optional second physical copy at ingress, drop/delivery terminals, backpressure, and a one-bit external-inflight veto. Quiescence requires sender closure and no pending ACK production. It does **not** prove closure of producers outside the test harness or hidden router buffers.

The one-active-transaction restriction is intentional. No multi-hop NoC, cross-clock/reset behavior, out-of-band replay, ordering guarantee, multi-tile throughput, physical PPA, or GPU-level capability is established.

## Outcomes and residuals
Locally executed Python paired models: 1,200/1,200 exact traces, 240,000 cycles, depths 2/3/4/5/8. Residual: zero model disagreements. This is model-to-model evidence, **not** RTL equivalence.

Counterexample: enqueue two identical ACK copies, deliver first, close sender, reuse UID prematurely, then deliver second to new transaction. An unsafe first-ACK policy falsely credits the new transaction; the bounded queue prevents quiescence while the second copy remains. This is an established replay/ABA problem, not a novel GPU law.

## Discovery Protocol V2 world model
- KNOWN (model): physical-copy conservation is preserved by the tested queue semantics; early reuse with an ACK copy remaining is unsafe.
- BELIEVED: verified terminal accounting can support a safe finite-UID reuse fence.
- CONFLICTING: early ACK-based reuse reduces retirement latency but violates replay isolation.
- FALSIFIED: first ACK acceptance or sender closure alone establishes physical quiescence.
- ANOMALOUS: the earlier Vektor-070 direct-wire integration bypassed queue residence and did not stress in-flight ACK clones.
- UNTESTED: RTL simulation results, formal equivalence, cross-reset safety, physical area/timing, multi-hop NoC, bandwidth under load.

## Adversarial review
Explorer: use finite physical-copy queues as a verifiable source of quiescence.
Skeptic: untracked external replay or clock-domain reset invalidates the fence.
Experimentalist: hold one ACK clone after sender closure and attempt UID reuse.
Analyst: zero model residual does not prove RTL or hardware correctness.
Anomaly Hunter: investigate long-tail drain latency and ACK queue occupancy.
Prior-Art Auditor: packet replay and sequence-number ABA are established problems.
Replicator: independent deque and ring implementations compared cycle by cycle.
Theorist: if all producers are closed and all admitted physical copies have terminal events, no old copy remains in the modeled finite fabric.

## Next decisive action
Obtain passing directed RTL + generic synthesis evidence, then extend the router with tracked delayed replay and an independently proven producer-closure handshake; run bounded formal checking of the complete sender/router/receiver system. Only then explore multi-tile scaling and equal-area alternatives.

## External GPU target gate
RTX 5090 official: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/
21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit interface, 575 W, fifth-gen Tensor cores, fourth-gen RT cores. 1,792 GB/s derives from 28 Gb/s/pin times 512 bits / 8. Marketing AI/RT TOPS are not directly comparable to unvalidated Vektor matrix engines.
Vektor-1A: 160 tiles, Wave32, 128 FP32 lanes/tile, 2.56 GHz *target*, 128 MB L2 *target*, 512-bit GDDR7 *target*. All RTX 5090-class gates: INCONCLUSIVE. No physical GPU measurement.
