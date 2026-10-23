# V296 post-route differential-penalty boundary and matched-resource falsifier (2026-10-23)

**Evidence tier: analytical sensitivity applied to preregistered measured global-route areas/slacks and the already-opened three-case detailed-route control artifact. Not an extracted V296 result.** This analysis was recorded while full six-case detailed routing was in progress (run 39995731088), before any V296 extracted-route result was available. It neither changes the frozen 3.5 ns physical gate nor opens workload holdouts.

## Inputs and provenance

The matched three-repair global-route experiment (run 39976579976; `THIRD_ROUND_GLOBAL_ROUTE_RESULT_20261023.md`) measured the optimized one-hot control and V296. The interrupted detailed-route experiment (run 39982695395; `DETAILED_ROUTE_PARTIAL_FALSIFICATION_20261023.md`) measured only original/nominal, original/high and optimized/nominal extracted results. In particular, **the original control already fails extracted setup at 3.5 ns**; the all-six gate is already falsified regardless of the V296 outcome. The full rerun is needed for V296's relative dominance, not to relabel the frozen gate as a pass.

| RC | Optimized control area (µm²) | V296 area (µm²) | Control global slack (ns) | V296 global slack (ns) | Optimized extracted slack (ns) |
|---|---:|---:|---:|---:|---:|
| nominal | 6249.936000 | 5370.806000 | 0.360324 | 0.762884 | 0.284155 |
| high | 6939.142000 | 5985.266000 | 0.179987 | 0.678807 | **unknown** |

## Exact differential-penalty law

Let `dA_p` and `dA_o` be **additional** V296 and optimized-control cell areas from future matched CTS/electrical repair. Let `L_p` and `L_o` be the corresponding loss of setup slack between global route and extracted route, measured under the *same* clock and constraints (negative values are allowed for an improvement). Define `D_A = dA_p - dA_o` and `D_T = L_p - L_o`.

- V296 retains **strict area dominance** iff `D_A < A_o - A_p`.
- V296 retains **at least 10% area reduction** iff `dA_p - 0.9*dA_o <= 0.9*A_o - A_p`. Note this is *not* equivalent to `D_A <= constant` when both designs grow.
- V296 retains **strict setup-slack dominance** iff `D_T < S_p - S_o`.
- V296 retains the preregistered **at least +0.20 ns extracted setup lead** iff `D_T <= S_p - S_o - 0.20 ns`.
- V296 itself meets the fixed **3.5 ns setup constraint** iff `L_p <= S_p`. This is necessary but not sufficient for the frozen all-six physical gate, which also requires controls, hold, DRC and electrical checks to pass.

| RC | Strict area advantage survives if `D_A <` (µm²) | 10% area reduction requires `dA_p - 0.9*dA_o <=` (µm²) | Slack dominance if `D_T <` (ns) | +0.20 ns lead if `D_T <=` (ns) | V296 setup if `L_p <=` (ns) |
|---|---:|---:|---:|---:|---:|
| nominal | 879.130000 | 254.136400 | 0.402560 | 0.202560 | 0.762884 |
| high | 953.876000 | 259.961800 | 0.498820 | 0.298820 | 0.678807 |

For **nominal RC only**, optimized control's measured extracted loss is `0.360324 - 0.284155 = 0.076169 ns`. Thus V296 can lose at most **0.278729 ns** to preserve a +0.20 ns extracted lead over that measured optimized implementation; its strict lead survives while `L_p < 0.478729 ns`. No analogous high-RC absolute loss bound can be inferred because optimized/high detailed route had not completed. Both statements are conditional predictions about the yet-unobserved V296 result, **not** V296 timing measurements.

## Frozen differential timing sensitivity sweep

These are algebraic outcomes for hypothetical *relative* post-route loss `D_T`, not measured route data.

| Relative loss `D_T` (ns) | Nominal predicted setup lead (ns) | High-RC predicted setup lead (ns) | Both retain +0.20 ns lead? |
|---:|---:|---:|---|
| 0.000000 | 0.402560 | 0.498820 | yes |
| 0.100000 | 0.302560 | 0.398820 | yes |
| 0.200000 | 0.202560 | 0.298820 | yes |
| 0.300000 | 0.102560 | 0.198820 | no |
| 0.400000 | 0.002560 | 0.098820 | no |
| 0.500000 | -0.097440 | -0.001180 | no |

**Important falsifier:** an additional V296-specific extracted loss relative to the optimized control above **0.202560 ns nominally** or **0.298820 ns at high RC** falsifies the +0.20 ns predictive margin even if V296 still has smaller cell area. At least one area or slack dominance reversal requires retiring V296 under the previously frozen rule. Do not confuse failure of the +0.20 ns *quantitative prediction* with an automatic reversal of strict dominance: the two thresholds are different.

## Equal-resource interpretation

The nominal **879.130 µm²** and high-RC **953.876 µm²** postrepair cell-area gaps are budgets the optimized controller could hypothetically spend on independent timing optimization at fixed overall controller area. They are **not** evidence that it can recover the observed slack deficit. A decisive equal-resource Pareto comparison must allow optimized control independent buffering, placement, CTS and power optimization within the *same integrated tile resource envelope*. Identical repair iterations alone do not provide that comparison.

## Decision rule and next action

When the six-case detailed-route evidence completes, extract each variant's final area, setup, pre-CTS hold, max slew/cap and DRC. Apply the independent `audit_detailed_route.py` without altering its frozen acceptance criteria. Compute actual `L_p-L_o` for both RC regimes and compare against this boundary; preserve the original control's 3.5 ns setup failure. If V296 loses area or setup dominance in either regime, retire. Otherwise preserve a **relative controller result only**, then test matched CTS/post-CTS hold, power, equal-tile-resource optimization and prospective workload/tile consequences. No RTX 5090 equivalence or same-clock IPC gain is supported.
