# V245 frozen protocol: paired operand issue
Frozen 2026-10-20 before any V245 evaluation. Sole active kernel. No claimed win.
1. Bottleneck law: baseline two dual-source instructions need 4 RF reads. Pair sharing a source saves one read. With p=sharing probability, normalized read-energy benefit requires p*E_RF>E_compare+E_multicast; issue throughput must account for stalls.
2. Mechanism: opportunistically pair ready instructions sharing one source, fetch once and multicast to two consumers; never wait more than one cycle. Same ports, issue slots and buffers.
3. Strongest equal-resource baseline: work-conserving dual-issue scheduler with operand reuse/bypass and identical RF ports, queue entries, multicast tree and wire budget. If this control can replicate candidate, retire before PPA.
4. Boundary: positive high p, high RF-port saturation, high ready-window occupancy; negative low p or divergent low occupancy. Sweep p, fanout, occupancy and ports.
5. Smallest RTL: two-source equality, pair-select arbitration and 32-bit two-sink multicast enable. No full scheduler.
6. PPA: functional equivalence, RTL simulation, synthesis, clean max-cap/slew, matched STA and mapped area; toggle activity with fanout/wire sensitivity, no power claims from toggles.
7. Workloads: compute, memory and divergent. Metrics instructions/cycle, RF reads/instruction, issue bubbles, load/area/energy proxies.
8. Falsification: equal-resource controller duplicates behavior, or physical timing/area overhead defeats gain. Max two substantive toolchain attempts.
9. Frozen unseen: positive seed=245101 occupancy>=6, p=0.75, RF pressure>0.9 predicts fewer RF reads vs naive scheduler; no assumed win vs strong control. Negative seed=245102 occupancy<=2, p=0.02, divergence=0.7 predicts no Pareto gain. 2 pp activity and 2% throughput tolerance.
10. Consequence: integrate only after full physical evidence and a distinct advantage vs strongest control. Otherwise unchanged tile.
Prior-art risk: GPU operand collectors, RF operand reuse caches, dual-issue pairing and operand multicast. Audit first.
