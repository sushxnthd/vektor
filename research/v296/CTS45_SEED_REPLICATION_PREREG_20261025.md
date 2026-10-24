# V296 preregistration: independent placement perturbation replication (2026-10-25)

## Hypothesis and immutable protocol
The completed matched 5 fF and 10 fF post-CTS comparisons support a controller-level V296 advantage over a physically feasible serial one-hot control, but share one deterministic placement. Test whether this result survives independent placement perturbations, not merely an output-load change.

**Freeze before outcomes:** exactly two new placement seeds, **17 and 43**. For each seed, run **both** pairwise and serial one-hot using the identical `global_placement -random_seed SEED -perturb_dist 500` (500 nm) policy. Keep the 3.5 ns clock, 45% placement density, 2x extracted RC, Nangate45, 5 fF output load, 16 max fanout, 250 ps post-CTS setup repair, extra serial-control pre-CTS optimization, and 7400 um² area ceiling unchanged. The original unseeded experiment is a historical reference, not a third independent replication. Do not add or cherry-pick seeds after results.

The runner creates seeded copies from immutable original Tcl and shell files, guarded by exact source anchors, and records SHA-256 provenance. If the pinned OpenROAD build does not accept these placement options, record a tool incompatibility and **do not silently substitute another intervention**.

## Frozen falsification
All four routed implementations must complete propagated-clock CTS, detailed routing, 2x OpenRCX extraction, zero slew/capacitance/DRC violations, nonnegative hold slack, >= 50 ps setup slack and <= 7400 um² cell area. Both contestants must be physically feasible at both seeds. At **each** seed, V296 must retain >= 10% lower controller area and >= 200 ps extracted setup advantage. The independent audit must preserve failures and never select only the winning seed. Outcomes: `ALL_SEEDS_FEASIBLE_PARETO_SUPPORTED`, `SEED_ROBUSTNESS_FALSIFIED`, or `INCOMPLETE_NO_REPLICATION_CLAIM`. A failed seed invalidates the *replicated robustness* claim and requires causal diagnosis, not retrospective exclusion.

## Claim boundary
This tests placement robustness only. It does not establish strict equal-consumed-area, full GPU-tile clock improvement, power, signoff or unseen-workload speedup. Because the controllers implement equivalent admissions, same-clock throughput gain with matched ports and resources is exactly zero. A positive throughput law still requires measured integrated tile periods and unsaturated bandwidth: `T=min(I*occupancy/((1+overhead)*max(controller_period,other_tile_period)), bandwidth_GBps/bytes_per_op)`. Preserve sealed win/no-win workload regimes. No RTX-5090-equivalence claim. V296 remains the only active mechanism; V287 stays retired; Kernellum PR #119 is untouched.

## Reproduce
`python3 research/v296/seed_replication.py --self-test`

`python3 research/v296/seed_replication.py --seed 17`

`python3 research/v296/seed_replication.py --seed 43`

`python3 research/v296/seed_replication.py --aggregate build/v296/cts45_seedrep`
