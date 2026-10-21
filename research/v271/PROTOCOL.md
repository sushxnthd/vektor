V271: MSHR credit lending. Sole active hypothesis; no breakthrough.

Law: with arrival rate lambda and latency L, outstanding occupancy n is approximately lambda*L. Fixed 4+4 MSHR partition blocks at class occupancy above 4. Hybrid 3+3 local slots plus 2 shared slots can serve (5,1) and (1,5) occupancy without additional slots.

Mechanism: eight tagged MSHR entries, three dedicated to each class and two shared. One shared allocation per cycle. Return by slot ID.

Controls: fixed 4+4, 5+3, 3+5, 6+2, 2+6 and fully shared eight entries. All use the same two request inputs, two response ports and 16-bit tags.

Boundary: alternating skew should beat every fixed partition; balanced 4+4 should not win; single-class demand above five should lose to fully shared. Global sharing is the strongest throughput control, so only matched physical PPA can establish a Pareto result.

Smallest implementation: parameterized eight-slot RTL allocator, randomized scoreboard test, Nangate45 mapped synthesis, characterized electrical STA and workload sensitivity.

Falsification: any tag corruption, dominated equal-resource PPA, or failure to pass electrical checks after one repair. Frozen holdout seeds 271901/271902/271903. Integrated tile unchanged.

Evidence: E1 behavioral model only. Novelty unestablished; shared MSHRs are established prior art.