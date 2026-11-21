# V317 legal-clock source repair: matched physical falsification and conditional resource boundary (2026-11-02)

## Frozen protocol and provenance

The [precommitted protocol](FROZEN_LEGAL_CLOCK_CROSSOVER_CHALLENGE_20261102.md) fixed both 2.050-ns and 2.200-ns clock targets, both source and pairwise RTL, Nangate45, 10-fF load, 100-ps uncertainty, ABC_AREA=1, seed 7, placement density add-on 0.05, identical 120x120-um die / 112x112-um core, and a **7%** minimum material-area criterion. No retuning or seed selection was performed after outcomes. GitHub Actions [run 41387898294](https://github.com/sushxnthd/vektor/actions/runs/41387898294) succeeded; its [immutable 468-file artifact 13116801260](https://github.com/sushxnthd/vektor/actions/runs/41387898294/artifacts/13116801260) contains source SHA `e9c2799b1c8eb331c6f89b5fd270f9f64ea44d24`, pinned OpenROAD image `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`, 4096-cycle RTL equivalence log, SDCs, logs, routed metrics, electrical reports and route artifacts.

The raw ZIP was downloaded and independently inspected. Values below were read from `6_report.json` and `5_2_route.json`, rather than inferred from workflow success. All four status files have `exit_code=0`; each final detailed-route DRC count is 0; each extracted-RC report has positive setup and hold slack and zero reported setup/hold, max-slew, max-capacitance and max-fanout violations. No SRAM macros are present. The existing [independent audit script](rtl/audit_legal_clock_crossover.py) can re-check extracted artifact directories; a separate ZIP-native local audit reproduced the same numbers.

## Matched physical results

| Clock target | Variant | Routed stdcell area (um2) | Setup slack (ps) | Hold slack (ps) | Fmax (MHz) | Routed wire (um) | Default-activity power (mW) |
|---|---|---:|---:|---:|---:|---:|---:|
| 2.050 ns | Source | 7244.78 | +5.619 | +16.553 | 489.146 | 57505 | 5.28869 |
| 2.050 ns | Pairwise | 6576.58 | +117.674 | +15.692 | 517.511 | 55418 | 5.05501 |
| 2.200 ns | Source | 7096.08 | +45.663 | +16.677 | 464.180 | 57697 | 4.85175 |
| 2.200 ns | Pairwise | 6560.36 | +193.543 | +15.387 | 498.391 | 55187 | 4.71284 |

**All four**: final detailed-route DRC 0; reported setup/hold/slew/cap/fanout violations 0. This is **one Nangate45 typical corner**, one placement seed and a control-only design; it is not multi-corner silicon signoff.

At 2.050 ns, pairwise reduces controller cell area **9.223%**, routed wire **3.629%**, and default-activity power proxy **4.418%**. At 2.200 ns, the respective savings are **7.550%**, **4.350%**, and **2.863%**. Both pairs pass the prospectively frozen >=7% material-area criterion. The power figures are uncalibrated default-activity estimates, not measured energy per useful GPU operation.

## Decisive falsification

**The source controller is physically legal at both relaxed clocks.** Therefore the earlier hypothesis that pairwise is *necessary* for a legal issue controller is **false** once the tile can tolerate >=2.050 ns. Retain only a narrower controller **area/power implementation** claim against the legally timed original. Do not translate its controller Fmax into GPU IPC or claim that the 2.200-ns hypothetical tile path has been measured.

This was the strongest existing legal-source control under the frozen matched settings, not a proof of optimality against all alternative RTL, synthesis choices or physical libraries. No claim of architectural novelty follows from the fixed-priority arbiter rewrite alone.

## New conditional positive boundary law (deterministic capacity accounting)

The [reproducible sensitivity script](rtl/legal_clock_resource_boundary.py) uses these legal-clock measured standard-cell areas. With hypothetical other tile area `A_other`, area budget `B`, and source/pairwise controller areas `A_s,A_p`:

`N_s = floor(B/(A_other + A_s)); N_p = floor(B/(A_other + A_p))`.

At an **equal externally determined clock**, let `q` be the pairwise/source useful per-tile service ratio after occupancy and control overhead, and `b` be sustained shared bandwidth normalized to source's unconstrained aggregate throughput. For **persistently backlogged deterministic service**, the exact conditional aggregate throughput ratio is:

`G = min((N_p/N_s)*q, b) / min(1,b)`.

This is a resource/bottleneck identity, **not** an independently validated new GPU law. It does not apply unchanged to stochastic unqueued arrivals; prior V317 evidence falsified a fluid no-win prediction in that regime. It also assumes tile-count reinvestment is physically feasible, a condition not established by this control-only experiment.

At **hypothetical** `A_other=40000 um2`, the integer budget windows in which source fits exactly 24 tiles and pairwise exactly 25 are:

- 2.050 ns: **1,164,415–1,181,119 um2** (16,705 integer budgets).
- 2.200 ns: **1,164,009–1,177,401 um2** (13,393 integer budgets).

At `B=1,170,000 um2`, both comparisons produce 24 vs 25 tiles; area savings at *tile* scale shrink to **1.414%** and **1.138%**, respectively. At `B=1,150,000 um2`, both fit 24 tiles, hence 1.000x at `q=1`. At `A_other=50000 um2, B=1,170,000 um2`, both fit 20 tiles, also 1.000x at `q=1`.

### Frozen **future** workload-model predictions (not yet validated)

The following regimes are predeclared **after** the physical routes but **before** any future independent workload evaluation. They must not be called held-out physical predictions. For `B=1,170,000, A_other=40000` and 24-vs-25 tiles:

| Backlogged workload regime | Normalized bandwidth b | Per-tile occupancy/control ratio q | Predicted ratio G | Interpretation |
|---|---:|---:|---:|---|
| Predicted win | 1.10 | 1.00 | **1.041667x** | Only if 25th tile can be integrated |
| Predicted bandwidth no-win | 0.95 | 1.00 | **1.000000x** | Shared bandwidth saturates both |
| Predicted occupancy reversal | 1.10 | 0.95 | **0.989583x** | A 5% per-tile loss defeats 25/24 replication |

The unconstrained occupancy break-even is `q > 24/25 = 0.96`. Any real test must calibrate `q`, bandwidth, RF port contention, workload queue semantics and tile power **independently**. A physically unintegrable extra tile or shared-clock SRAM path invalidates the 25-vs-24 premise. These are **prospective falsifiers**, not demonstrated performance improvements.

## Next hard gates

1. Integrate RF SRAM/banking and datapath timing into an actual tile with fixed area/port constraints; verify whether the pairwise controller changes the critical path and whether 25 tiles can physically fit.
2. Independently measure backlogged and unqueued workload traffic, occupancy and power. Evaluate the frozen win, bandwidth no-win and occupancy-reversal regimes without post-hoc fitting.
3. Test multi-corner timing/electrical legality, wire/load perturbations, and a stronger optimized original/alternative. Preserve negative results.
4. Prior-art audit and independent reproduction. No RTX-5090-equivalence, real GPU IPC or measured energy claim.

**Decision: retain as a bounded control implementation optimization, kill necessity and unconditional throughput claims. World-class completion gate remains open.**
