# V288 ACTIVE: bank-saturation-conditioned producer forwarding (hypothesis)

V287 retired in its own research branch after the existing four-grant/four-scheduler V-Tile resource bound. V288 is the sole active architecture kernel. **E0 proposal, no measured gain.**

1. **Bottleneck law:** Let d be attempted RF operand reads per bank per cycle, c=2 physical read ports, h the fraction whose exact full physical register address matches a ready forwarded producer. With no other bottleneck, the optimistic throughput ratio is
   G = min(1,c/(d*(1-h))) / min(1,c/d).
   This is an upper bound, not a measured GPU speedup; if d<=c or h=0, G=1.
2. **Exact mechanism:** Hold one recent producer destination/value in a forwarding slot; compare full physical register address on each consumer request; satisfy matching requests from the forwarded value without occupying a bank read port. Never coalesce merely because bank indices match.
3. **Strongest equal-resource baseline:** Two-read-port bank plus one-entry write-through operand cache or conventional ALU forwarding of identical tag/storage/fanout budget. If the control achieves the same hits, retire as redundant. Compare same buffering, banks, read ports and input/output bandwidth.
4. **Predicted boundary:** Win only when exact producer-consumer reuse h>0 and read pressure d>2; no gain in compute-bound or memory-bound workloads, or with d<=2. High fanout, forwarding latency and wire capacitance can erase the gain.
5. **Smallest RTL:** Two-port admission logic with exact address compare, one bypass tag/value slot, 4 request inputs, and explicit forwarded/granted masks. Full RF array not implemented yet.
6. **Physical proxies:** Matched Nangate45 cell area, path delay, load/slew/cap checks and activity proxy; no PPA claim without characterization. Area-budget control must receive equivalent comparator/slot resources.
7. **Workload metric:** Retired operand requests and wave operations per cycle, RF bank reads, bypass hits, dependency stalls and power/traffic proxy across compute/memory/divergent traces.
8. **Decisive falsification:** If a same-budget one-entry write-through cache/standard bypass matches, or forwarding mux/control delay erases benefit, retire.
9. **Unseen predictions frozen before evaluation:** WIN: d=3, c=2, h=0.5, no downstream bottleneck -> ideal G=1.5. NO WIN: d=1.5, c=2, h=0.5 -> G=1.0. NO WIN: d=3, h=0 -> G=1.0. Freeze these regimes; do not tune after observing.
10. **Architecture consequence:** Only if physical matched-control tests pass, consider forwarding path at RF bank/operand collector interface. No V-Tile modification now.

**Prior-art risk:** Conventional CPU/GPU forwarding, operand caches and register-file bypass networks are established. V288 is a targeted falsifiable architecture experiment, not a novelty claim. No RTX 5090 equivalence claim. V153/V156 FP32 cutset electrically disqualified.
