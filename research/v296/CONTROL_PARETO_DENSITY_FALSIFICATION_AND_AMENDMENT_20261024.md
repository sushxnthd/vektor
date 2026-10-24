# V296 control-advantaged Pareto: failed-density forensic result and prospective uniform-density amendment (2026-10-24)

**Mechanism unchanged:** V296 pairwise bank-conflict admission only. V287 retired. This is a separate amendment to the previously frozen four-way high-RC control challenge, not a retroactive pass. Holdout workloads remain SEALED.

## Immutable failed run and measured facts

[Run 40044253063](https://github.com/sushxnthd/vektor/actions/runs/40044253063) completed with failure; [35-file raw artifact 12542240080](https://github.com/sushxnthd/vektor/actions/runs/40044253063/artifacts/12542240080), artifact ZIP SHA-256 `e524a557cb581aebf84393d7f8bee96b68ca12b8a19cfab4222703d4ed4c9783`. Original and serial one-hot each completed a fifth control-only repair, detailed route, SPEF extraction and post-extraction checks. Parallel one-hot failed at initial global placement; V296 never ran. The four-way audit **cannot pass**; no same-run candidate-vs-control conclusion is available.

| Variant | Extracted cell area (um^2) | Extracted setup slack (ns) | Extracted hold slack (ns) | Slew / cap / DRC | Interpretation |
|---|---:|---:|---:|---:|---|
| Original | 7192.639817 | -0.127790 | +0.249569 | 0 / 0 / 0 | Routed and electrically clean; setup FAIL |
| Serial one-hot | 6942.599828 | -0.173046 | +0.267903 | 0 / 0 / 0 | Routed and electrically clean; setup FAIL |
| Parallel one-hot | Not routed | Not measured | Not measured | Not measured | OpenROAD `GPL-0302` at global placement |
| V296 pairwise | Not run | Not measured | Not measured | Not measured | Blocked by fail-fast predecessor |

Parallel one-hot's initial standard-cell area is **8223.922 um^2** in a **14099.064 um^2** snapped core. Initial utilization `u=A_cells/A_core=0.5832956` exceeds the frozen placement target `d=0.45`; OpenROAD requested `d>=0.59`. This is an **implementation-capacity falsification**, not a V296 performance victory. Its initial cell area also exceeds the frozen **7400 um^2 common cell-area ceiling by 823.922 um^2 (11.13% of the ceiling)**; a future physical optimizer would have to shrink it by **at least 10.019%** to qualify. We do not assume that repair monotonically increases area, so the initial overshoot is a *warning*, not a mathematical proof of post-route ineligibility.

## Compact predictive placement boundary

For an unchanged synthesized netlist, initial placement requires approximately

```
u = A_mapped / A_core <= d_target
A_core_min = A_mapped / d_target
```

before additional placer-specific margin. At `d=0.45`, parallel one-hot would need at least **18275.382 um^2** of core, **29.621%** more than the frozen core. This explains the specific GPL-0302 failure but does **not** predict routability, electrical closure, post-route area, clock frequency or GPU throughput. Merely enlarging the floorplan would alter wire lengths and violate the original matched physical experiment.

## Prospective amendment, frozen before new execution

Keep the **same 140 x 140 um die, snapped core, Nangate45 technology, 3.5 ns clock, 2x high-RC extraction, 0.25 ns max slew, 7400 um^2 cell-area ceiling, output load, tie mapping, and four-way control-advantaged repair sequence**. Change only the **global-placement target density from 0.45 to 0.65 for ALL FOUR variants**, not just the parallel control. This is a *new amended experiment*, so its physical measurements must be compared only within its own run. A single optional `V296_PLACE_DENSITY` environment variable defaults to 0.45 for all older workflows; this new workflow sets 0.65 and the independent audit requires the exact 0.65 marker in every completed variant.

The 0.65 choice is prospective: it is above the measured 0.5833 initial utilization and the tool's 0.59 recommendation while leaving 6.67 percentage points of nominal density headroom. It may increase congestion or alter relative performance, so **a failed route or lost V296 advantage is scientific negative evidence**, not a reason to cherry-pick a new density. No variant-specific density, floorplan, constraints, timing guardband or repair changes are allowed.

### Frozen predictions and kill conditions

- P1: the parallel control should clear its *initial global-placement density check* at 0.65; detailed-route feasibility and its post-route cell area are unknown. If it still fails, preserve the failure and do not claim a four-way physical pass.
- P2: the controls' 0.45-density extracted setup failures (127.790 ps original, 173.046 ps serial) may change at 0.65; they are not assumed permanent. The original fourth-round high-RC V296 result is a prior, **not** a same-run comparison.
- P3: V296 must independently route, pass extracted setup/hold/electrical/DRC, retain >=10% cell-area saving against the smallest measured control and >=0.20 ns setup lead against the fastest. If not, retire/re-evaluate V296 under the original frozen kill policy. A control must itself close to be a valid physical alternative; strict equal-area superiority remains unproven unless a feasible area-matched control is actually measured.
- The older 0.45-density run stays **FAILED**. A new 0.65-density pass does not erase it. Preserve all failures, raw logs and checker verdicts. Do not unseal workloads, infer same-clock IPC gain (predicted 0%), or claim GPU tile / RTX-5090 equivalence.

## Next evidence tier

Run the uniform-density four-way experiment and independently audit every DEF/SPEF/DRC and timing endpoint. If V296 survives, pursue real CTS and a feasible equal-consumed-area control; if it fails, retain the falsification and kill/re-evaluate. Kernellum PR #119 is separate and untouched.
