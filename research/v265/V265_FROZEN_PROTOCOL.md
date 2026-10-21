# V265 — locality-bounded bank-output escape fabric

Sole active kernel after V264 retirement (2026-10-21). Frozen E0 hypothesis, not validated.

Four banks and four collectors split into two clusters; two local 2x2 switches and one shared one-word escape channel in each direction. No extra buffers or RF ports. Bound: T <= min(4,1/qAB,1/qBA), where qAB and qBA are fractions of total responses crossing each direction. This is a necessary cut bound, not a throughput guarantee. Also enforce destination capacity.

Compare strongest full 4x4 crossbar and same-budget sparse escape fabric. Positive holdout seed 265101: qAB=qBA≈0.08, predict no raw-service penalty; clock-adjusted win only if measured frequency ratio >1.02. Negative seed 265102: qAB=qBA≈0.40 with balanced destinations, predict <=2.5 responses/cycle vs feasible full-crossbar 4. Divergent seed 265103: bursts and delayed credits; predict lossless completion and longer sparse tail. Freeze generator hash before opening.

Minimum gates: equivalence, RTL simulation, synthesis, electrical max-cap/slew, matched timing/area, modeled workload throughput, 0.5/1/2x wire sensitivity. Metrics: completion rate, bank stalls, tail, toggles, area, timing, cap, energy. Retire if matched sparse equals candidate or electrical checks fail after one repair. No V-Tile change without physically credible Pareto win. Prior art risk high. No GPU product equivalence claim.
