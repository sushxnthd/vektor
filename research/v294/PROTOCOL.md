# V294 — bounded lookahead conflict escape (sole active hypothesis)

Evidence class: E0 preregistration only. V293 is retired on exact banked-control equivalence. V287 remains retired.

1. **Bottleneck law.** With two RF read ports per each of 16 banks and four schedulers, primary-candidate bank collisions create unused issue slots. For one candidate pair, let p be primary rejection probability, a the probability of a valid alternative, and q its conditional rejection probability. If alternative choice does not displace later grants, ideal gain is G=1+p*a*(1-q)/(1-p). For independent equal-conflict alternatives q=p, G=1+a*p. This is a *local service law*, not a tile throughput prediction.
2. **Mechanism.** A two-candidate per-scheduler issue selector with one-step bank-pressure lookahead. Before consuming bank ports, compare primary and alternate candidates; prefer the one that leaves more bank-port capacity for other scheduler requests. No new RF ports or collector entries.
3. **Strong controls.** (i) Two-choice primary-first greedy with the same candidate metadata and muxes; (ii) bank-pressure greedy with identical metadata and comparable logic budget; (iii) exhaustive max-cardinality assignment oracle as an upper bound, not an area-matched physical control. Kill if an equal-area pressure-greedy control matches.
4. **Predicted boundary.** Gain only when primary conflicts occur and an available alternative avoids them without displacing another grant. No gain when conflicts are absent, alternative invalid, or RF throughput is not limiting. Must quantify adverse cases too.
5. **Smallest RTL.** Four issue slots; two candidates per slot; each candidate uses two 4-bit RF bank IDs; one-cycle combinational selector and capacity-two bank grant tracking. Integrate only after electrical gate.
6. **Physical.** Functional oracle, Icarus randomized RTL, Yosys/Nangate45 mapping, OpenSTA max-cap/slew and timing with 0.5/1/2x output load and wire estimates. Count metadata/mux area in both mechanisms.
7. **Workloads.** Compute-heavy (high issue pressure), memory-heavy (few ready waves), divergent (variable ready count). Report issue grants/cycle, fairness, RF bank occupancy, area, critical delay, toggle proxy and no-win regimes.
8. **Falsification.** RTL mismatch; no gain against equal-budget greedy; gain erased by matched timing/area; violation of electrical checks; adverse tail regression or fairness failure.
9. **Frozen unseen holdouts.** (a) two-choice escape with one primary overbooked bank pair and alternative disjoint: predicted positive if control cannot recover; (b) four disjoint bank pairs: predicted 1.000x. Do not tune on holdouts. The local probability-law check at p=.5,a=1,q=.5 predicts 1.5x service, but not necessarily 1.5x four-slot grants.
10. **Tile consequence.** Replace existing issue candidate selection only if equal-resource RTL/PPA and workload gates pass. Never claim RTX 5090 equivalence.

Prior art risks: conflict-aware GPU warp scheduling, operand collectors and bank arbitration are established. Audit exact competing schedulers before novelty claim.

**Acceleration:** No more than one CI/plumbing-only run. Next substantive run must implement the paired selector and independent checker and test strongest equal-resource control.
