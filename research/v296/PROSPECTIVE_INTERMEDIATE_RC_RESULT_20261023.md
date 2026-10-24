# V296: prospective intermediate-RC prediction and electrical onset (2026-10-23)

## Frozen prediction, evidence and scope
- The interpolation law, RC points **1.25, 1.50, 1.75**, and absolute error tolerance **0.040 ns** were committed before these measurements in `FIXED_TOPOLOGY_SENSITIVITY_FALSIFICATION_20261023.md`.
- Executed in [GitHub Actions run 39949387182](https://github.com/sushxnthd/vektor/actions/runs/39949387182), raw artifact [12498724651](https://github.com/sushxnthd/vektor/actions/runs/39949387182/artifacts/12498724651). The independent prospective checker reports `BOUNDED_INTERPOLATION_SUPPORTED_NOT_PHYSICAL_PASS`; the original fixed-topology and adaptive electrical gates **both still fail**.
- The intermediate RC points were **unseen at forecast time**, but they are *electrical sensitivity points, not workload holdouts*. Workload holdouts remain sealed.
- All three nominal-implementation DEF SHA-256 hashes were unchanged through the sweep, independently rechecked from raw ZIP bytes. No resizing, rerouting, replacement or placement occurred after nominal repair/global route. These are **global-route estimated RC** values, not detailed-route extracted parasitics or signoff.

## Prospective predictions versus observed setup slack
Worst setup slack in ns at common 3.5 ns clock and 0.005 pF output load. Errors are observed minus preregistered linear interpolation between the prior RC=1 and RC=2 results.

| Variant | RC | Predicted slack | Observed slack | Error | Max-cap violations |
|---|---:|---:|---:|---:|---:|
| Original | 1.25 | +0.010493 | +0.010805 | +0.000312 | 1 |
| Original | 1.50 | -0.023838 | -0.023483 | +0.000355 | 2 |
| Original | 1.75 | -0.058169 | -0.058024 | +0.000145 | 3 |
| Optimized one-hot | 1.25 | +0.218541 | +0.219566 | +0.001025 | 0 |
| Optimized one-hot | 1.50 | +0.177131 | +0.178539 | +0.001408 | 1 |
| Optimized one-hot | 1.75 | +0.135720 | +0.136453 | +0.000733 | 3 |
| V296 pairwise | 1.25 | +0.727422 | +0.733825 | +0.006403 | 0 |
| V296 pairwise | 1.50 | +0.690318 | +0.699349 | +0.009032 | 1 |
| V296 pairwise | 1.75 | +0.653213 | +0.659738 | +0.006525 | 2 |

**Nine of nine** prospective slack predictions meet the frozen 0.040 ns absolute tolerance; maximum absolute error **0.009032 ns (9.032 ps)**. V296's worst prediction error is 9.032 ps. Its observed slack lead over the strongest optimized control is **+0.514259, +0.520810, +0.523285 ns** at RC=1.25, 1.50, 1.75, respectively. No candidate-only electrical violation was found at these three points.

## Bounded local law, not a GPU breakthrough
For each implementation `v`, define the preregistered *local interpolation* over `1 <= r <= 2`:
```
s_v(r) = s_v(1) + (r - 1) * [s_v(2) - s_v(1)]
```
This is a compact, *empirically supported local timing-sensitivity approximation* for one fixed nominal implementation and the stated OpenROAD model. It is **not** a mechanism-level predictive GPU throughput law, not validated across technology corners, and not proof of linear physics outside the measured interval. The intermediate points are not independent implementations or unseen workloads.

The electrical boundary is more restrictive than setup slack: V296 and optimized are cap-clean at RC=1.25 but both violate at RC=1.50; the original already violates at RC=1.25. Therefore **do not interpolate capacitance-violation counts or claim clean RC=1.5**. The actual electrical-closure crossover for V296 and optimized is bounded only to **(1.25, 1.50]** in this fixed implementation and discrete tested settings, without asserting a continuous threshold.

At the common 3.5 ns clock, equal scheduling decisions imply a theoretical same-clock issue-throughput ratio of 1 under equal downstream conditions; **no workload-level performance measurement was made**. Controller area remains 14.039% smaller at nominal placement, but this is not tile/GPU area.

## Decision
- **Prospective local interpolation: supported within the frozen tolerance.**
- **Full physical gate: FAIL** (remaining max-cap violations and original setup failure).
- **World-class architecture completion: NOT MET**. No detailed-route SPEF, signoff, power, tile integration, prospective workload transfer or measured frequency advantage.
- V296 remains the sole provisional mechanism because its matched area and timing-margin advantage persists. Retire it if symmetric electrical repair and the strongest equal-resource control eliminate that advantage. Preserve all failed gate evidence and workload holdouts.
