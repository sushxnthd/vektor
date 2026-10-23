# V296 matched placed/routed evidence: preregistered closure experiment (2026-10-23)

## Evidence and status
Source: GitHub Actions run 39927501835, artifact 12490957226 (47 files; 9 matched OpenROAD cases, Yosys/Nangate45, OpenROAD 2.0-17598-ga008522d8). This is global-route estimated parasitics, **not** detailed-route SPEF, signoff timing, power, or a tile-level GPU result. Frozen workload holdouts remain unopened. The fail-closed audit correctly returned `PHYSICAL_GATE_FAIL`.

The three architectures use the same 140 x 140 um die, 120 x 120 um core, 0.45 placement density, I/O loads, and 2 ns constraints. The strongest control is selected independently for area and timing; neither a weaker baseline nor a post-hoc speedup is permitted.

| RC multiplier | V296 routed area (um2) | Smallest control area (um2) | Area saving | V296 slack at 2 ns (ns) | Best-control slack (ns) | V296 max slew/cap violations | Best-control max slew/cap violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 5476.408 | 6171.732 | 11.266% | -0.314988 | -0.667352 | 0 / 1 | 0 / 0 |
| 1.0 | 5636.274 | 6360.060 | 11.380% | -0.420848 | -0.700007 | 0 / 0 | 0 / 0 |
| 2.0 | 6142.472 | 7076.930 | 13.204% | -0.542351 | -0.867967 | 0 / 1 | 0 / 1 |

At nominal RC, V296 is 723.786 um2 smaller than the smallest matched repaired control and has 0.279159 ns more setup slack than the fastest matched control. **Neither meets 2 ns.** One capacitance violation remains in the V296 low/high cases; the optimized control also has one in the high case. These are failures, not an electrical pass.

## Falsifiable area/timing boundary
Let `A_v(r)` be the post-repair V296 area and `A_b(r)=min(A_original(r),A_optimized(r))` the smallest equal-resource control at RC multiplier `r`. Let `S_v(r,T)` and `S_b(r,T)=max(S_original(r,T),S_optimized(r,T))` be the corresponding setup slacks under the same clock period `T`. The required **simultaneous** boundary is

```
for each preregistered r in {0.5,1,2}:
    A_v(r) < A_b(r)
    S_v(r,T) > S_b(r,T)
    S_v(r,T) >= 0 AND S_original(r,T) >= 0 AND S_optimized(r,T) >= 0
    slew_violations(r,each) = cap_violations(r,each) = 0
```

This separates a candidate-specific architectural gain from simply relaxing timing for everyone. Existing results satisfy the first two inequalities only. A normalized throughput consequence is **conditional**, not measured: for equal issue/cycle and effective occupancy, `G=min(f_v I o/(1+c),M)/min(f_b I o/(1+c),M)`; when both hit the downstream cap `M`, `G=1`. Any physical gain also must be amortized over the controller's fraction of full-tile area.

## Frozen next physical discriminator (before running it)
The previous 2 ns target is infeasible for *all* tested architectures. Rather than claim a frequency win from negative slack, use **3.5 ns** as a new **shared** feasible-clock closure experiment. This target is frozen here *before* the new experiment, and chosen conservatively above the worst observed 2 ns path budget (3.347 ns for the high-RC original control) by ~0.153 ns. This is a new experimental operating point, not a retroactive reinterpretation of the 2 ns run.

Run identical matched placement/repair and global-route RC cases at 3.5 ns. Re-run electrical repair against global-route estimates and then re-route after any cell changes. Audit all three variants across all three RC scenarios. Reject if any case is incomplete, electrically dirty, violates 3.5 ns, or loses either area or timing superiority to the strongest control. Report pre- and post-closure area, slack and residual violations, including any regressions. Do not open workload holdouts or claim a clock-rate advantage merely because the 3.5 ns constraint passes.

Even a pass is **provisional** until detailed routing/SPEF, realistic corner and load variation, dynamic power proxies, full tile integration and independent reproduction. This is a narrow physical implementation hypothesis, not a claim of novel GPU scheduling semantics.
