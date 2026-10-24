# V296: frozen 3.5 ns nine-case postrepair physical falsification (2026-10-23)

## Evidence identity and integrity
- Preregistered experiment: `research/v296/ROUTED_RC_BOUNDARY_AND_3P5NS_PREREG_20261023.md`.
- Source: GitHub Actions run [39940723571](https://github.com/sushxnthd/vektor/actions/runs/39940723571), artifact [12496092048](https://github.com/sushxnthd/vektor/actions/runs/39940723571/artifacts/12496092048), 47 files, all nine matched cases present. Original failed checker artifact retained.
- Same-run Yosys/Nangate45 synthesis, OpenROAD 2.0-17598-ga008522d8, identical die/core/clock/RC settings and electrical-repair algorithm for the original, optimized one-hot and V296 controllers.
- These are **global-route estimated RC** results. They are **not** detailed-route extracted SPEF, signoff timing, dynamic power, measured frequency or tile-level performance.
- The independent checker initially rejected the artifact because the stage matcher matched `routed_preclosure` when requesting `routed`. A separate commit fixes the prefix collision and adds a regression test. The actual physical result below is **FAIL**, independent of that parser error. No workload holdouts were opened.

## Frozen postrepair/routed metrics

Area is postrepair standard-cell area in um2; slack is worst issue-data setup slack at the common 3.5 ns clock. Max slew violations are zero in all nine routed cases.

| RC scale | Original area / slack / cap | Optimized area / slack / cap | V296 area / slack / cap | V296 area saved vs smallest control | V296 slack lead vs fastest control |
|---|---|---|---|---:|---:|
| 0.5 | 5867.694 / -0.051959 / 0 | 5828.858 / +0.404365 / 0 | 5058.522 / +0.787251 / **1** | 770.336 um2 (13.216%) | +0.382886 ns |
| 1.0 | 6183.170 / +0.044824 / 0 | 6165.348 / +0.259952 / 0 | 5299.784 / +0.764527 / 0 | 865.564 um2 (14.039%) | +0.504575 ns |
| 2.0 | 6952.176 / +0.102248 / 0 | 6759.858 / +0.196749 / 0 | 5799.066 / +0.631322 / 0 | 960.792 um2 (14.213%) | +0.434573 ns |

**Decision: PHYSICAL_GATE_FAIL.** The low-RC V296 case retains **one max-capacitance violation** after the frozen single electrical-repair/reroute pass. The low-RC original control also misses the shared 3.5 ns setup target by 0.051959 ns. Nominal and high-RC cases meet the frozen 3.5 ns setup and slew/cap checks for all three designs, but the protocol requires **all nine** cases to pass.

## What this falsifies and what remains

1. The mapped 18.04% area saving must **not** be carried into the placed/repair experiment. Same-run postrepair saving is 13.216–14.213% of the smallest controller across the RC sweep.
2. A shared 3.5 ns clock means **no measured throughput gain** is established. The 0.383–0.505 ns relative slack lead is an implementation margin, not a frequency-ratio measurement.
3. A V296 timing/area advantage is still visible in all three modeled RC conditions; therefore this result does not yet satisfy the **area/timing erased** retirement condition. It does fail electrical closure and is **not** a physically validated mechanism.
4. Repair budget and slack are RC-sensitive. No conclusion about detailed routing, crosstalk, corner robustness, clock-tree effects, power, or GPU throughput follows.
5. No relaxation of the frozen gate is permitted. The next discriminating experiment must fix the low-RC capacitance violation and original-control setup failure **symmetrically** under the same timing and repair budget, or retire V296 if equal-resource repair removes its advantage. A prospective, independent detailed-route/SPEF check and full-tile resource integration remain mandatory before any architectural claim.

## Positive-law constraint (unvalidated)

With identical scheduling decisions, accepted issue/cycle `I`, occupancy `o`, control overhead `c`, and downstream bandwidth ceiling `M`:

```
T(f) = min(f * I * o/(1+c), M)
G = T(f_V296) / T(f_control)
```

At the same verified 3.5 ns operating clock, `G=1` for all workloads under those assumptions. In the downstream-limited regime, `G=1` even if one controller supports a higher clock. The postrepair controller-area saving is not a tile-area or performance gain; if controller fraction of tile area is `a`, then projected tile-area saving is `a * delta_controller`, conditional on unchanged integration and routing. Unseen workload predictions remain sealed.
