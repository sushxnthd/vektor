# V296: tile-normalized throughput/area boundary (2026-10-23)

**Analytical prediction only; no new silicon, post-route, workload or power evidence.**
V296 preserves issue decisions and issue ports. Its only demonstrated advantage is an initial mapped-controller area estimate. Any workload throughput gain must come from a **measured** frequency change or independently demonstrated resource effect.

Let `delta=(A_c-A_p)/A_c` be the controller-only fractional area saving, and let `a=A_c/A_tile` be the baseline controller fraction of tile area. Under a single controller substitution with all other tile resources unchanged:

```
A_tile,p / A_tile,c = 1 - a*delta
T_p / T_c = min(f_p * I * o/(1+c), M) / min(f_c * I * o/(1+c), M)
(T_p/A_tile,p) / (T_c/A_tile,c) = (T_p/T_c)/(1-a*delta)
```

Here `I` is accepted issue capacity, `o` occupancy, `c` control overhead and `M` downstream throughput ceiling. The **compute-bound throughput-density break-even** is `f_p/f_c > 1-a*delta`. This is an *area-efficiency* criterion, not an authorization to retain V296 after a failed timing/electrical gate.

For the preliminary `delta=0.180353`, if controller area is 1%, 5%, or 10% of tile area, the tile area savings are respectively **0.1804%, 0.9018%, 1.8035%**. Corresponding compute-bound frequency-ratio break-even values are **0.998196, 0.990982, 0.981965**. These are conditional examples; Vektor's actual `a` has not been measured.

When both designs are bandwidth-limited (`M <= min(f_p,f_c)*I*o/(1+c)`), throughput gain is **exactly 1**. Any improvement in throughput density in that regime is area-only. For a strict architecture-survival claim, require verified mapped connectivity, timing, electrical limits and non-regressing integration. The earlier positive/no-win workload predictions remain sealed.

Implementation: `research/v296/predictive_boundary.py`. The self-tests verify arithmetic only. A true positive law still needs independent held-out workload traces, measured clocks, tile area and electrical/power constraints.
