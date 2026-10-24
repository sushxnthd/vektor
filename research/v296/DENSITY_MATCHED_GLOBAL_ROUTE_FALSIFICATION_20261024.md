# V296 matched-density global-route evidence and falsification (2026-10-24)

## Provenance and status

Preregistered six-contestant run: [40075668363](https://github.com/sushxnthd/vektor/actions/runs/40075668363), head `c0b55ee36e2de7fa1cbc3cf48c2b5cb1bb3da29e`. Its independent aggregate job [120821633017](https://github.com/sushxnthd/vektor/actions/runs/40075668363/job/120821633017) reports `status=INCOMPLETE` because **both 65%-density controls failed to complete global routing**. This is a real physical implementation limitation, not an audit bug to suppress. All six job logs and the independent aggregate artifact are retained. The two frozen V296 density predictions were supported, but the six-way experiment did **not** meet its full completeness gate.

The companion mapped-STA run [40075668316](https://github.com/sushxnthd/vektor/actions/runs/40075668316) passed 2,048-cycle RTL comparison and reported a 1.279x *unrepaired mapped timing ratio* against the optimized control, but **failed electrical admissibility** (V296: 698 max-slew and 41 max-cap violations). It is not physical speedup evidence. Its different analysis stage must not be mixed with routed timing.

## Matched-floorplan global-route results (ideal clock, not signoff)

The six jobs use the preregistered 140 x 140 um die, 120 x 120 um core, 3.5 ns clock, Nangate45, 2.0x wire-RC setting and equal per-density floorplan, with controls given an extra repair round. Areas are controller cell areas, **not tile or GPU area**. All values below are extracted from the aggregate job's independent audit JSON.

| Variant | Placement target | Final global-route area (um^2) | Ideal-clock setup slack (ps) | Max-cap violations | Feasibility under <=7400 um^2, >=50 ps, zero electrical violations |
|---|---:|---:|---:|---:|---|
| V296 pairwise | 45% | 5987.926 | +678.804 | 0 | PASS (necessary global-route tier only) |
| Serial one-hot | 45% | 6942.600 | +190.476 | 0 | PASS (necessary global-route tier only) |
| Original | 45% | 7192.640 | +112.566 | 0 | PASS (necessary global-route tier only) |
| V296 pairwise | 65% | 7911.106 | +4.863 | 2 | FAIL |
| Serial one-hot | 65% | no final route | last-stage -532.275 | last-stage 4 | INCOMPLETE |
| Original | 65% | no final route | last-stage -1435.621 | last-stage 4 | INCOMPLETE |

At 45%, **V296 beats two physically feasible global-route controls on both area and ideal-clock setup slack**. Relative to serial one-hot, area is **13.751% lower** and setup slack **488.328 ps higher**. Relative to original, area is **16.749% lower** and slack **566.238 ps higher**. These are *matched floorplan and shared area ceiling*, **not strict equal-consumed-area, detailed-route or CTS comparisons**. The 65% results provide no matched feasible-control comparison.

## Measured density sensitivity and strictly limited boundary

V296 cell area increases **1923.180 um^2 (+32.118%)** between the two targets; its ideal-clock setup slack falls **673.941 ps**, and max-cap violations increase from 0 to 2. Thus density is a large physical implementation sensitivity under this exact flow. The evidence does not establish that all of this is caused by density alone if other non-frozen implementation details differ; input/toolchain SHA logs are retained for checking.

As a **descriptive two-point secant only**, linear interpolation places the area-ceiling crossing at target density **0.59685** and the 50-ps setup-guardband crossing at **0.63661**. The former would bind first *if* both interpolations held and capacitance remained clean. Neither interpolation is validated, and a discrete max-capacitance count cannot be interpolated. Do not call these thresholds a predictive positive law, infer monotonicity, or extrapolate to other libraries/floorplans.

Reproduce the calculations from the downloaded aggregate `density_audit.json` with:

```bash
python3 research/v296/density_secant_boundary.py --self-test
python3 research/v296/density_secant_boundary.py build/v296/density_gate/density_audit.json
```

## Falsification decisions and next discriminating experiment

1. **Keep V296 provisionally**, because the preregistered 45%-pass/65%-fail predictions were both observed and the 45%-density controls completed matched global route. Do not erase the failed 65% tier, the mapped electrical failure, or the falsified universal area law.
2. **Do not certify architectural superiority yet.** The independent aggregate gate is INCOMPLETE; no CTS, detailed-route/SPEF, switching power, strict equal-consumed-area comparison, tile throughput, or unseen workload law has passed.
3. Next physical test: **at 45%**, compare V296 and serial one-hot with matched extracted-SPEF detailed routing, CTS and clock-tree area, independent electrical checks, and explicit equal-consumed-area/resource budgets. Freeze the test before opening results. Abort or retire V296 if the matched feasible control erases the physical advantage.
4. Freeze a *new* 55%-density point before running it if a predictive density-boundary law is pursued; the already observed 45% and 65% outcomes are training data, **not unseen holdouts**.
5. Preserve the workload holdouts and Kernellum PR #119. V287 stays retired; V296 remains the only active Vektor mechanism. No RTX-5090-equivalence claim.
