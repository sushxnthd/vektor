# V296 D4 matched routed prediction falsified: physical feasibility is asymmetric (2026-10-28)

## Evidence provenance and preregistration

- Frozen prospective protocol: [DEFERRED_WRITE_MATCHED_ROUTED_PREREG_20261028.md](DEFERRED_WRITE_MATCHED_ROUTED_PREREG_20261028.md), committed before this run's outcomes.
- Original four-way routed run: [GitHub Actions #40646515864](https://github.com/sushxnthd/vektor/actions/runs/40646515864), source commit `84245c21f485c191aea7d352652c0ef036d6d047`.
- Completed D4 pairwise job `122676592244`, original artifact `12800301495`; completed D4 optimized serial job `122676592295`, original artifact `12800782354`. Both report `complete: true`, zero cap/slew violations, and extracted-RC post-CTS metrics. The original audit requires DRC count zero, routed marker, DEF/SPEF, and propagated clocks. These are research PDK results, **not signoff**.
- D8 pairwise and serial jobs were still running at the time of this report; **no D8 outcome is inferred**. Existing holdouts remain sealed.

## Measured D4 extracted-RC result

| Metric | V296 pairwise | Strong optimized serial |
|---|---:|---:|
| Final routed area (µm²) | 19,543.019647 | 21,914.942749 |
| Setup slack at 3.5 ns (ns) | +0.066661 | -0.323617 |
| Hold slack (ns) | +0.010758 | -0.011207 |
| Cap/slew violations | 0 / 0 | 0 / 0 |
| Complete original route | Yes | Yes |
| Frozen +50 ps setup, >=0 hold, <=30,000 µm² metric gate | Pass | **Fail** |

The candidate saves **2,371.923102 µm² = 10.8233%** of the serial routed area and leads setup by **390.278 ps**. But **this is not a feasible matched Pareto win**, because the strong serial control misses both setup and hold.

The frozen **predicted-win D4 regime is falsified**, not confirmed. A green pair of routed jobs is not a successful matched physical comparison. The candidate alone satisfies the necessary reported metrics and has just **16.661 ps of setup margin above the frozen +50 ps guard**; modest unmodeled delay could remove that pass.

## Necessary repair and integration boundaries

Let `s` be extracted setup slack and `h` hold slack. The minimum *reported-metric* repairs are

`R_setup = max(0, 0.050 ns - s)` and `R_hold = max(0, -h)`.

The serial control requires **at least 373.617 ps of setup improvement and 11.207 ps of hold improvement**, with no assumption that both are independently achievable. Increasing the 3.5 ns clock period to at least **3.873617 ns** would satisfy only the *fixed-path* setup guard, not the negative hold slack. Re-optimization, clock changes and path migration can invalidate simple additive predictions.

At the frozen 30,000 µm² slice budget, both implementations fit exactly **one** independently replicated slice. Under an idealized *linear replication without inter-slice overhead* assumption, V296 would fit two at 39,086.039294 µm² and the serial control would fit two at 43,829.885499 µm². This is an area-packing boundary, **not a measured multi-slice tile or throughput advantage**.

## Falsification decision

1. Preserve D4 candidate physical feasibility as a **narrow, provisional necessary-metric pass**, not signoff.
2. Reject the preregistered D4 **matched feasible Pareto** prediction because the strongest serial control fails. Do not relax its clock or replace it with a weaker control to manufacture a win.
3. Keep V296 the sole provisional mechanism; V287 remains retired. Do not change branch/PR or claim a GPU speedup.
4. Await both D8 original jobs and run the existing fail-closed depth aggregate. A job success or one-sided feasible candidate is insufficient. Preserve failed and censored results.
5. Before another expensive route, test whether any symmetric repair could plausibly close the serial control's 373.617 ps setup and 11.207 ps hold deficits while preserving the candidate's 16.661 ps guard headroom. If not, reject this retiming strategy as a matched physical proof.
6. No power, production SRAM macro, tile-level frequency or unseen-workload result is established.

## Reproduction

`python3 research/v296/deferred_routed_d4_repair_envelope.py --self-test --json`

The standalone Decimal checker uses only the original D4 job metrics, explicitly rejects missing/nonfinite/electrical-invalid data and unobserved D8 results, and preserves evidence provenance. It is an independent **metric-envelope analysis**, not a replacement for the original artifact-level DEF/SPEF/DRC auditor.
