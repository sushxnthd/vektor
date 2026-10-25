# V296: physically constrained tile-level upper bound, not a GPU speedup (2026-10-25)

**Evidence tier:** exact-rational *counterfactual* sensitivity on original, independently audited post-route area. Original paired physical run [40156470550](https://github.com/sushxnthd/vektor/actions/runs/40156470550) is **BOTH_INFEASIBLE** at 3.5 ns: V296 setup -1.047895 ns, hold -0.036622 ns, 3 capacitance violations; serial setup -1.859922 ns, hold -0.019796 ns, 3 capacitance violations. The same-clock RTL admission counts are equal. **No measured GPU throughput, Fmax, tile power or feasibility is implied.**

## Derivation and falsifiable upper bound

Original matched final cell areas: V296 `17,857.644252 µm²`, serial `18,953.830505 µm²`. Define measured slice area saving `s = 1 - A_V296/A_serial = 0.05783454973446`. Define `f` as the fraction of a *hypothetical baseline replicable tile's area* occupied by exactly one such serial slice, `r = F_V296/F_serial` as the ratio of **feasible** clocks (not known), and `H >= 1` as the shared-bandwidth headroom relative to the serial design's baseline traffic rate (not known). If each slice admits the same useful work per clock and generates the same traffic per useful work, and all other tile area is identical:

```
A_tile,V296 / A_tile,serial = 1 - f*s
ideal replica count ratio          = 1 / (1 - f*s)
optimistic throughput ratio        <= min(r / (1 - f*s), H)
clock-ratio break-even (if H > 1)  = 1 - f*s
```

This is an **optimistic continuous-area ceiling** under explicit idealized assumptions, not a prediction of actual tile speedup. Occupancy, fixed overhead, register-file replication, bank/port limits, memory contention, interconnect, cooling, voltage, clock trees and physical repair can only make this area-only scenario less reliable; the original hardware has not closed timing. The strongest independently optimized serial implementation has not been evaluated at strict equal consumed area.

## Frozen counterfactual regimes (not unsealed workload holdouts)

| Baseline slice fraction f | Feasible clock ratio r (assumed) | Bandwidth headroom H (assumed) | Optimistic throughput ceiling | Interpretation |
|---:|---:|---:|---:|---|
| 0.10 | 1.00 | 1.10 | 1.005817x | At most **+0.582%** |
| 0.25 | 1.00 | 1.10 | 1.014671x | At most **+1.467%** |
| **0.50** | **1.00** | **1.10** | **1.029778x** | **Predicted possible-win** *idealized* regime, ceiling +2.978% |
| **0.50** | **1.00** | **1.00** | **1.000000x** | **Predicted no-win** bandwidth-saturated regime, gain ceiling zero |
| 0.50 | 1.00 | 1.01 | 1.010000x | Only +1.0% with 1% bandwidth headroom |
| 0.50 | 0.97 | 1.10 | 0.998885x | A 3% clock reduction erases all area-derived gain |
| 1.00 | 1.00 | 1.10 | 1.061385x | Absolute optimistic all-slice extreme, +6.138% |

The two bold regimes are *analytic scenario declarations*, not real workloads or prospective unseen GPU validation. The genuine workload holdouts remain sealed. In particular, this model **cannot** show that the candidate improves the same fixed-size tile: at equal clock and equal admission work/cycle, its throughput is identical unless area savings are converted into additional productive hardware and resources remain available.

At `f=0.50`, the clock break-even is `r > 0.971083`. An unmeasured frequency slowdown of just **2.892%** eliminates even the optimistic replication gain. The original negative slacks are **not** frequency measurements and must not be converted into a clock ratio.

## Discrete tile replication falsifier

Under the same optimistic `f=0.5` and fixed total silicon area, integer packing yields:

| Baseline tiles | Maximum whole V296 tiles | Area-only idealized ratio |
|---:|---:|---:|
| 16 | 16 | 1.000000x |
| 64 | 65 | 1.015625x |
| 1024 | 1054 | 1.029297x |

Continuous replication exaggerates gains at small scale. These are exact floor operations on idealized areas, **not a fabricated GPU configuration or measured GPU result**.

## Reproducibility and decision

Run `python3 research/v296/optimistic_tile_consequence_bound.py --self-test` and then `python3 research/v296/optimistic_tile_consequence_bound.py`. The exact-rational arithmetic, invalid-input rejection, boundary checks and integer-packing inequalities passed locally on 2026-10-25. Hosted independent validation is not yet claimed.

**Decision:** the physical evidence can support a conditional *area-replication ceiling*, not a positive integrated GPU performance law. V296 remains the sole mechanism under falsification, V287 remains retired, and no RTX-5090-equivalence claim is defensible. Next experiment must first recover independently audited extracted critical paths, physically close both candidate and strongest equal-resource serial control, then measure real workload throughput, traffic, switching activity and integrated power. If matched closure or bandwidth removes the gain, kill the performance claim. Preserve the original failed gate and all negative results.
