# Vektor-071: bounded physical-copy router

Evidence date 2026-10-10. Classes: DISCRIMINATION, CAPABILITY-BUILDING, SURPRISE. Cost: $0.

## Preregistered predictions and outcomes
P1: cloned ingress creates two counted physical copies. PASS (directed RTL).
P2: first ACK delivery does not establish quiescence while a second ACK remains. PASS (directed RTL).
P3: closed producers + empty DATA/ACK queues + no external-inflight packet is required for modeled quiescence. PASS (directed RTL).
P4: integrated sender/router/receiver completes two sequential same-UID transactions under the modeled fence. PASS (directed RTL).
P5: deque and indexed-ring implementations agree across 1,200 deterministic 200-cycle traces. PASS (240,000 cycles, exact).

## Verified evidence
GitHub Actions https://github.com/sushxnthd/vektor/actions/runs/37999812399 : Icarus Verilog router and integrated directed tests PASS, Yosys generic synthesis PASS, 300 generic cells at UID_W=4 and DEPTH=4. Yosys converted packet arrays to registers. This is not routed area/timing or SRAM evidence. See RTL_EVIDENCE.md.

## Preserved falsification
A throughput model resampling backpressured cloned packets produced an invalid 0.62122 logical transactions/cycle at 50% offered clones and 80% physical service. Accepted clone fraction was 0.28705, revealing selection bias. Holding payload stable until admission gave 0.53360 with 0.50322 accepted clones. See THROUGHPUT_ANOMALY.md.

## Discovery Protocol V2 world model
KNOWN (model/RTL directed): two physical ACK copies must both terminate before fence; tested bounded queue conserves physical copies.
BELIEVED: truthful producer closure plus terminal accounting enables bounded UID reuse.
CONFLICTING: early reuse improves occupancy but violates replay isolation.
FALSIFIED: first ACK delivery or sender closure alone proves quiescence; resampling a backpressured request is a valid throughput benchmark.
ANOMALOUS: the invalid generator preferentially excluded two-copy transactions.
UNTESTED: hidden external replay, cross-clock reset, multi-hop NoC, formal end-to-end safety, physical PPA, full GPU execution.

Adversarial roles: Explorer proposes counted bounded fabric; Skeptic identifies hidden replay and reset; Experimentalist stalls second ACK; Analyst separates RTL-directed evidence from formal proof; Anomaly Hunter identifies workload-selection bias; Prior-Art Auditor treats ABA/replay as established; Replicator uses deque/ring independent models; Theorist states conditional terminal-conservation law.

Single next decisive action: implement explicit delayed replay and independently verified producer closure, then bounded formal proof of no stale credits under UID wrap and reset. Multi-tile performance and equal-area search follow.

External target: https://www.nvidia.com/en-in/geforce/graphics-cards/50-series/rtx-5090/
Vektor-1A architectural values remain unvalidated targets. All RTX 5090-class gates INCONCLUSIVE.
