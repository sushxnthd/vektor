# V296 matched 45%-density extracted-route falsification — preregistration (2026-10-24)

## Scope and prior evidence

V296 is the sole provisional Vektor mechanism. V287 is retired. Preserve the existing branch and draft PR #13. The prospective workload holdouts remain sealed. The prior six-way **global-route-only** test (Actions 40075668363) measured V296 at 5,987.926 µm² and +0.678804 ns ideal-clock setup slack, versus serial one-hot at 6,942.60 µm² and +0.19048 ns. Both passed the 45%-density global-only necessary gate; V296 failed its own 65%-density gate. Neither result establishes detailed-route or CTS closure.

This preregistration is committed **before** new detailed-route execution. The next tier is matched detailed routing with extracted parasitics for **V296 pairwise** and the strongest 45%-density area/timing control, **serial one-hot**. Original control is weaker on both 45%-density global metrics and is excluded to conserve no-cost runtime. This is not a new mechanism.

## Frozen experiment

Each contestant is independently synthesized from the existing RTL and Yosys command in `run_density_matched.sh`. Use unchanged `control_advantaged_pareto.tcl` with its full detailed-route path, not the global-only exit. Both contestants use the same 140×140 µm die, 120×120 µm core, Nangate45 Liberty/LEF, 3.5 ns clock, 0.15 ns IO delays, 0.005 pF output load, 0.25 ns max transition, metal2–metal10, placement target 0.45, high-RC 2×, identical repair rounds 1–4, and the same routing/extraction calibration. The control alone retains the preregistered fifth repair round. Separate jobs preserve partial evidence if detailed routing aborts or times out. Tool and technology hashes are recorded.

The experiment retains the 7,400 µm² controller-area ceiling and requires a completed routed DEF, extracted SPEF, zero DRC/max-slew/max-cap violations, **setup slack >= +0.050 ns**, and **hold slack >= 0**. Setup/hold are **ideal-clock, pre-CTS** measurements. Do not call this signoff or a measured GPU throughput result.

## Frozen predictions and kill decisions

1. **Candidate physical feasibility prediction:** V296 will complete detailed route and pass the above extracted gate at 45%. If complete but failing, V296's 45%-density physical gate is falsified; retire or redesign rather than rescue it by changing area, clock or RC constraints.
2. **Conditional Pareto prediction:** *If both contestants complete and pass the same physical gate*, V296 will use at least **10% less controller area** than serial one-hot and have at least **+0.200 ns** more extracted setup slack. Failure falsifies the predicted Pareto advantage.
3. If serial one-hot is incomplete or infeasible, **do not declare architectural superiority**. Preserve its last measured stage and classify the matched comparison as inconclusive or no feasible-control comparison. If V296 is incomplete, report incomplete rather than failure or success.
4. A common area ceiling is **not strict equal-consumed-area matching**. Do not generalize to GPU tile area, switching power, clock-tree closure or RTX-5090 equivalence.

The prior 65%-density failure is a **known no-win physical regime**, not a new blind prediction. No workload holdout is opened in this experiment. A new workload positive boundary law must later be frozen against independent workload regimes, incorporating compatibility probability, mask overlap, bandwidth/port pressure, occupancy and controller overhead.

## Independent evidence and next gate

An independent Python checker, separate from the Tcl flow, verifies identity, density, clock, RC multiplier, control-only repair entitlement, stage markers, finite extracted timing, DRC, DEF and SPEF. It must preserve incomplete results and fail closed. Both contestant artifacts and the aggregate audit must be uploaded even if the workflow fails.

Even a passing extracted-route result is **pre-CTS**. Next steps remain matched clock-tree synthesis and hold repair, realistic activity/power, strict equal-resource comparison, workload-level throughput/traffic, independent checker, unseen predictions, prior art and tile-level consequence. The world-class completion gate remains **NOT REACHED**.
