# V290 — Partial operand admission (preregistered protocol)

Status: sole active hypothesis; E0, no hardware evidence. V287 and V289 remain retired.

## Ten required items
1. Bottleneck law: when atomic 2-source admission cannot fit both reads, unused bank capacity U can coexist with waiting operands. Potential saved stalls are bounded by U and collector occupancy; partial reads cannot increase physical port bandwidth.
2. Mechanism: independently read one ready operand per bank into already allocated collector slots; track two per-slot ready bits; issue only when both operands present. No new RF ports or data storage.
3. Strongest control: optimal work-conserving atomic 2-source scheduling with request reordering, identical RF ports, four collector slots, and equalized metadata/logic area. Include a conventional operand-collector control.
4. Win boundary: bank pressure temporally skewed enough that atomic matching strands ports, yet collector occupancy and prefetch useful life permit partial admission. Lose/no-win under conflict-free demand, collector saturation or bandwidth saturation.
5. Smallest RTL: 2-bank/4-collector-slot operand-ready demonstrator with per-bank arbitration and exact operand value/age correctness.
6. Physical proxies: characterized mapped area, critical path, max-cap and slew, switching activity; sensitivity to output load and wire RC.
7. Metrics: completed 2-operand instructions per cycle, critical-path latency, total RF reads, collector occupancy, and energy/read proxy across compute-bound, memory-bound, divergent traces.
8. Falsify if optimal equal-budget atomic or conventional collector matches, if overfetch exceeds saved stalls, or if area/timing/energy erases any gain.
9. Frozen unseen prediction: positive regime is skewed hot-bank contention with idle cold-bank ports and available collector entries; no-win regime is conflict-free 2-source demand. No results evaluated at protocol freeze.
10. Tile consequence: change V-Tile operand collector only after clean equivalence, RTL sim, synthesis, electrical checks, matched STA/area, workload validation and unseen prediction; no RTX 5090 claim.

Evidence class: E0 hypothesis only. All results and failed gates must be committed to this branch. 
