# V295 — parallel bank predecode on the V-Tile issue critical path (sole active hypothesis)

Status: E0 preregistration. V293 and V294 retired; V287 remains retired.

1. **Bottleneck law.** Existing issue-control path is wave-ready -> warp pick -> 128:4 bank-index mux -> bank arbiter -> accept. If its bank lookup and arbitration dominate, parallel predecoding can reduce logic depth; if scheduler selection or wire fanout dominates, it cannot. No symbolic headroom is a timing result.
2. **Mechanism.** Precompute compact bank occupancy masks for eligible candidate waves in parallel with scheduler selection, then select and arbitrate already-decoded masks. Preserve exactly the same four accepted wave IDs and two-reads-per-bank safety rule as existing vektor_issue_control unless a separate fairness/performance test explicitly allows changed scheduling. No added RF ports, buffers or lanes.
3. **Strong control.** Existing V-Tile issue_control + rf_bank_arbiter synthesized with identical constraints and optimized mux/logic; plus an area-matched optimized predecode control. If simple retiming/logic synthesis equals V295, retire.
4. **Derived boundary.** Let T_old=T_sched+T_bankmux+T_arb+T_accept, T_new=max(T_sched,T_predecode)+T_select+T_arb_new+T_accept+T_wire. Timing improvement requires T_new<T_old, with clean max-cap/slew and equal or lower effective area. For workload service T=min(f*I, B_mem/m), G=min(f_new*I,B_mem/m)/min(f_old*I,B_mem/m), assuming identical IPC/issue behavior.
5. **Smallest RTL.** Four issue candidates, 16 RF banks, two read ports/bank, wave32 IDs, bank masks; equivalence checker against existing issue_control and arbiter. Account for all predecode fanout and wire cost.
6. **Physical.** Icarus functional equivalence -> Yosys/Nangate45 -> OpenSTA cap/slew/timing -> matched area -> wire/load 0.5x/1x/2x -> switching power proxy. A generic logic count is NOT area or clean STA.
7. **Workloads.** Compute-bound saturated ready waves, memory-bound return-limited waves, divergent masks/occupancy. Metrics: accepted waves/cycle, frequency-limited throughput, bank conflicts, area, critical path, toggles and sensitivity.
8. **Decisive falsification.** Any functional mismatch, excessive predecode area/fanout, dirty electrical checks, or failure to improve throughput/energy against area-matched optimized original. Fix at most once.
9. **Frozen unseen predictions.** Compute-bound high-ready/high-RF-demand should improve in instructions/sec **only if** measured f_new>f_old and no bubbles; memory-bound with B_mem/m < f_old*I predicts ~1.000x despite fmax change. Holdouts unopened until functional equivalence and physical timing gates pass.
10. **Tile consequence.** Replace only the V-Tile issue critical path if characterized matched-resource win survives real workloads; no RTX 5090 equivalence.

Prior art: retiming, bank-aware scheduling and bank predecode are established ideas. Claim only a measured, reproducible Vektor-specific timing/throughput boundary if it survives controls.

**Next run:** Implement paired RTL and prove equivalence, then run characterized timing/area or kill. Do not spend more than one run on CI setup.
