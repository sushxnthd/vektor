# V296 four-way global-route falsification (2026-10-24)

**Decision: FAIL.** Ideal-clock, global-routing-only evidence; not detailed-route, CTS, extracted-SPEF, power, signoff or GPU throughput. V296 remains the sole provisional mechanism; V287 stays retired; workload holdouts remain sealed.

## Frozen physical experiment

[Actions run 40069058725](https://github.com/sushxnthd/vektor/actions/runs/40069058725), head `d4ea011776337d3e03b05be8bca9858a30fd480a`: Nangate45, 3.5 ns clock, high RC, 65% placement-density target, 7,400 µm² controller-area ceiling. All contestants receive four repair rounds; the controls are entitled to a fifth. All four jobs failed and preserved raw artifacts.

| Contestant | Last completed stage | Area µm² | Area above ceiling µm² | Setup slack ns | Slew / cap violations | Termination |
|---|---|---:|---:|---:|---:|---|
| V296 pairwise | Global final | **7,911.106** | **511.106** | **+0.004863** | **0 / 2** | Global route complete; **area and cap fail** |
| Serial one-hot | Fourth repair, before routing | 9,996.812 | 2,596.812 | −0.532275 | 0 / 4 | `GRT-0116` congestion |
| Parallel one-hot | Initial placement | 8,223.922 | 823.922 | −4.125862 | 3,850 / 432 | `DPL-0036` placement failure |
| Original | Fifth repair, before routing | 10,208.814 | 2,808.814 | −1.435621 | 0 / 4 | `GRT-0116` congestion |

**Important:** Only V296 completed the global-only route tier. Control rows are **intermediate**, not matched post-route PPA. Thus these data do not establish a four-way area/timing victory. The +4.863 ps setup margin is pre-CTS and not a robust physical timing result. The candidate itself **fails** the frozen global-only area and capacitance requirements.

## Audit-parser falsification

The original `audit_global_gate.py` assumed OpenROAD would emit `worst slack max NUMBER`. Pinned OpenROAD actually emitted `worst slack NUMBER` in all four archived logs. The original checker therefore incorrectly reported V296's complete record as malformed. Corrected audit code accepts both numeric spellings, retains intermediate evidence when routing/placement aborts, and fails closed on missing physics markers, area excess, timing failure and electrical violations. Archived original audit JSONs remain unchanged.

The separate `global_gate_fourway_forensics.py` verifies artifact ZIP SHA-256 values, independently parses the last completed physical stage without importing the primary checker, and reproduces the measured failure.

## Predictive physical boundary and next test

V296 at the 65% density target needs at least **511.106 µm² (6.46%)** of area reduction and elimination of **two capacitance violations** merely to clear the global-only feasibility gate. To maintain a hypothetical 50 ps setup guardband, the current ideal-clock +4.863 ps slack needs **45.137 ps** improvement, even before clock-tree effects.

The earlier 45%-density extracted V296 result was 5,987.926 µm², +0.418903 ns setup and zero slew/cap/DRC violations. The new 65%-density global-only result is **1,923.180 µm² (+32.12%) larger**, but floorplan and evidence tier differ. This is not a controlled causal estimate of density, and neither result proves superiority over a fully closed control.

**Next preregistration:** Repeat all contestants at matched floorplan, clock, RC and repair rules while varying density, and demand completed comparable physical stages. Freeze a density crossover prediction before observing new results. Do not relax the 7,400 µm² ceiling to rescue V296. Retire its claimed advantage if no shared feasible region exists or a feasible control catches up.

## Immutable evidence

- [V296 artifact 12550586404](https://github.com/sushxnthd/vektor/actions/runs/40069058725/artifacts/12550586404): `3a571b343a09631c2a8c561e89fd39b03db8c638ba54b84e6392d8e918d56746`
- [Serial artifact 12550207652](https://github.com/sushxnthd/vektor/actions/runs/40069058725/artifacts/12550207652): `adca74b536f30c37204145795608e957aba5bb47b1bee740cbe2528d1603e87b`
- [Parallel artifact 12550409973](https://github.com/sushxnthd/vektor/actions/runs/40069058725/artifacts/12550409973): `edf2f935b8bec213436568b67e6dca18048d6b664569ac0ce5e3b3b5a5d8f10c`
- [Original artifact 12549699690](https://github.com/sushxnthd/vektor/actions/runs/40069058725/artifacts/12549699690): `f231b3c0d708b0a8396774f607386e990076b2f1a165edcfa034d97079a2d933`

**World-class completion gate: NOT REACHED.**
