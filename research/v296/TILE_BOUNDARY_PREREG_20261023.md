# V296 tile-level positive-law boundary and sealed prospective regimes (2026-10-23)

## Scope and nonclaims

V296 is a **controller implementation-topology** mechanism with functional equivalence to the optimized issue controller. Its same-clock issue-throughput improvement is exactly **0%** when scheduler decisions, clock and resources are held fixed. No benchmark of the controller alone establishes GPU instructions/second, energy, or RTX 5090 equivalence. This protocol is frozen **before** any integrated-tile timing, workload or power outcome is inspected.

The new independent, dependency-free `research/v296/tile_boundary.py` implements the following **analytical** boundary. It has self-tests for positive, critical-path-negative and bandwidth-negative controls, but has **no empirical validation yet**.

## Predictive law

Let `A0` and `A1` denote matched repaired controller cell areas, `At` the full baseline tile area, `Tc0` and `Tc1` the respective physically characterized effective control-limited minimum clock periods **in an integrated tile**, and `To` the minimum clock period of all other tile paths. Let `I` denote workload instructions per cycle, `m` mean bytes transferred per retired instruction and `B` effective sustainable bytes/ns of the complete tile's memory path.

Under unchanged occupancy, instruction mix, scheduler decisions, resource allocation, and no new physical coupling:

```
controller_area_fraction f = A0 / At
controller_area_reduction r = (A0 - A1) / A0
tile_area_reduction = f * r

T0 = max(Tc0, To)
T1 = max(Tc1, To)
R0 = min(I / T0, B / m)
R1 = min(I / T1, B / m)
potential tile throughput gain = R1 / R0 - 1
```

For `m=0`, the traffic limit is unbounded. `Tc` **cannot** be inferred naively from a single isolated controller's slack; tile integration, critical path identity, clock-tree loading and wire parasitics must be measured. If occupancy, traffic, `I`, `B`, or resource allocation change, this law must be extended and revalidated rather than silently reusing the same prediction.

## Frozen prospective win/no-win regimes

- **Predicted-win (conditional):** `Tc1 < Tc0`, `To <= Tc1`, `B/m >= I/Tc1`, and unchanged occupancy. Then the **potential** frequency-limited gain is `Tc0/Tc1 - 1`; the tile-area gain is `f*r`. Neither the premise nor the result has been observed in an integrated GPU tile.
- **Predicted-no-win A (critical path elsewhere):** `To >= Tc0`. Then `T0=T1=To` and predicted throughput gain is **0%** even with a smaller controller.
- **Predicted-no-win B (bandwidth saturated):** `B/m <= I/T0`. Then both rates are capped at `B/m` and predicted throughput gain is **0%**.
- **Unfavorable physical regime:** if detailed route, CTS, load or tile integration erases `Tc1<Tc0` or makes the controller area saving nonpositive, retire the mechanism under the original physical gate rather than claiming a speedup.

These boundaries must be evaluated prospectively on unseen workloads with matched area/resources, fixed frequency and independently clock-optimized variants, realistic bandwidth, tile-critical-path tracing, and uncertainty intervals. The two predicted-no-win cases are **not** optional. Do not cherry-pick the positive case. Report the number of workloads crossing each boundary and out-of-regime prediction errors.

## Numeric illustration only — not a Vektor result

If the controller is 3% of tile area and is 14% smaller, the full-tile area reduction is **0.42%**, not 14%. A controller that is 16.7% faster cannot accelerate a tile whose critical path is elsewhere or whose memory bandwidth is saturated. All numbers in this paragraph are hypothetical.

## Evidence gates

The detailed-route 3.5 ns six-case protocol remains unchanged, and the [partial extracted-RC falsification](DETAILED_ROUTE_PARTIAL_FALSIFICATION_20261023.md) already shows original-control setup failures. The workload holdouts remain sealed. The tile law is an **unvalidated hypothesis**, not a claimed discovery, and is not a substitute for the full GPU completion gate.
