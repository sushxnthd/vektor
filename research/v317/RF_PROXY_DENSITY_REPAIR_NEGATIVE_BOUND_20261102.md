# V317 density-repair extracted-RC falsification and materiality boundary (2026-11-02)

## Decision: NO MATERIAL WIN; ELECTRICAL GATE FAIL

The prospectively frozen matched density-repair experiment completed successfully as a *workflow*, but **all four physical routes remain electrically illegal**. Neither matched pair reaches the frozen 2.0% raw whole-proxy area saving. Do not mistake the workflow's successful exit for a passed physical gate.

- Source SHA: `f53a808ccb15b9baaf571fb8ec5d7a6ce786d60f`, unchanged V317 RTL; branch `research/v317-sass-provenance-gate`, draft PR #34.
- Workflow: https://github.com/sushxnthd/vektor/actions/runs/41429483633 ; artifact: https://github.com/sushxnthd/vektor/actions/runs/41429483633/artifacts/13135637209 ; artifact SHA256: `7718f5e7f71988e7bd97bc16aa52807e432a6f0ec61af78d81f7e106dd299993` (465 files, 269,339,553 ZIP bytes).
- The hosted checker `audit_rf_proxy_density_repair.py` verified the 4,096-cycle RTL pass, source SHA, pinned container digest, frozen SDC/mapping, both density settings, all four extracted-RC routes, setup/hold/cap/slew/fanout/DRC and sequential/macro counts. Its `any_legal_material_win` is **false** and `all_legal_no_material_win` is also **false**, correctly because the designs are illegal.
- Original 0.05 physical gate remains an immutable historical FAIL; the 0.15 and 0.35 settings were frozen before outcomes. All configurations use Nangate45, a 3.000-ns SDC, 240x240-um die, 16-bank 2R RF flop proxy, 1,213 sequential cells and zero SRAM macros.

| Density add-on | Source area (um²) | Pairwise area (um²) | Raw saving | Source hold / violations | Pairwise hold / violations | Max-cap source / pairwise |
|---|---:|---:|---:|---|---|---|
| 0.05 historical | 21,610.6 | 21,432.2 | 0.825521% | -1.574 ps / 3 | -0.400 ps / 4 | 11 / 8 |
| 0.15 prospective | 21,533.5 | 21,404.2 | 0.600460% | -2.798 ps / 6 | -0.758 ps / 2 | 16 / 14 |
| 0.35 prospective | 21,535.6 | 21,324.7 | 0.979309% | -1.781 ps / 10 | +3.952 ps / 0 | 15 / 21 |

All routes passed setup and detailed-route DRC, but each matched pair failed hold and/or max-cap constraints. At density 0.35 the pairwise hold constraint is repaired, **not** its 21 capacitance violations or the source's 10 hold violations.

## Independent algebraic kill bound

Let `A_s` and `A_p` be measured matched routed areas and `H>=0` identical additional tile hardware. Under the explicitly optimistic *additive common-area* assumption, the total relative saving is

`g(H) = (A_s - A_p) / (A_s + H)`, with `dg/dH = -(A_s-A_p)/(A_s+H)^2 < 0` when the pairwise controller is smaller.

For the frozen 2% threshold, `H <= (A_s-A_p)/0.02 - A_s` is necessary. The inferred upper bounds on H are **-12,690.6**, **-15,068.5**, and **-10,990.6 um²** at 0.05, 0.15, and 0.35 respectively. Because these are negative, **no nonnegative amount of identical added hardware can turn the measured raw saving into a >=2% material win** without changing the controller implementation or physical interactions. This is a mathematical bound for the additive model, not a physical prediction for new P&R.

At the observed pairwise area, the additional area reduction needed merely to reach 2% of the measured source is **253.812**, **301.370**, and **219.812 um²** respectively. At density 0.35 this is still **1.031% of the entire pairwise proxy**, on top of the measured saving. Electrical repair could change routed areas, so this is a frozen-observation bound, **not a proof that every future optimization fails**.

## Wire and power sensitivity

At density 0.15, pairwise has **2.598% more routed wire** and only **0.108% lower default-activity power proxy**. At 0.35, pairwise has **0.451% less wire** and **1.826% lower default-activity power proxy**. These are not characterized silicon power measurements, and neither density is electrically legal.

## Architectural interpretation and next decisive action

The controllers are grant/operand-equivalent; same-clock intrinsic scheduling throughput remains **1.000x**. The previously hypothesized tile-packing throughput gain has no legal RF-proxy materiality support and must not be promoted as GPU performance. **Kill V317 as a demonstrated tile-level architectural performance mechanism.** Preserve the narrower controller-only implementation observation and all negative evidence in this draft PR. Do not revive V287 or relax the preregistered 2% gate.

A future candidate must change a genuine hardware resource bottleneck, preregister a positive boundary law and no-win regime, beat the strongest matched legal source implementation, and demonstrate integrated SRAM/datapath P&R, electrical legality and unseen workload benefit. Additional density-only reruns of unchanged V317 are not a rational route to a world-class architecture result. No RTX 5090 equivalence, GPU IPC gain, SRAM-macro integration or silicon power claim is established.

Reproduction: `python3 research/v317/rtl/rf_proxy_materiality_boundary.py` checks the arithmetic and synthetic positive/negative controls using the immutable transcribed extracted-RC observations. This algebraic check is **not** a substitute for the raw-artifact checker or independently measured silicon.
