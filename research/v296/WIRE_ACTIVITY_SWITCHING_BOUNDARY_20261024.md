# V296 activity-weighted interconnect boundary (2026-10-24)

**Evidence tier:** immutable measured OpenRCX SPEF capacitance inputs + new analytical sensitivity/falsification, **not** measured power. Source: [detailed-route run 39995731088](https://github.com/sushxnthd/vektor/actions/runs/39995731088), artifact 12523741140; net summaries in [EXTRACTED_SPEF_LOAD_CONCENTRATION_20261024.md](EXTRACTED_SPEF_LOAD_CONCENTRATION_20261024.md). Reproduce: `python3 research/v296/wire_switching_boundary.py --self-test` and `--sweep`. V296 remains the sole provisional mechanism; V287 retired. This does not change the failed six-case physical gate.

## Positive/negative boundary law

For fixed voltage and clock, a deliberately simplified interconnect-switching proxy is proportional to `sum_n(alpha_n * C_n)`, where `C_n` is the SPEF declared `*D_NET` capacitance and `alpha_n` is effective net transition activity. This **excludes** cell internal power, glitch-model uncertainty, short-circuit current, leakage, clock tree, supply effects, coupling correlations, and physical signoff. The separately routed netlists have no established per-net activity correspondence. It is not valid to equate summed SPEF capacitance with measured power.

Under the **explicit uniform-activity-within-design assumption**, V296's proxy beats a control if and only if:

```
alpha_V296 / alpha_control < C_control / C_V296
```

The control must be the **lowest-capacitance alternative**, not merely the optimized one-hot variant. For the observed high-RC hotspot `issue_wave0[0]` of `C_hot=0.127312 pF`, if the rest of V296 switches at `alpha_bg`, the hotspot can have activity at most

```
alpha_hot <= (alpha_control*C_control - alpha_bg*(C_V296-C_hot))/C_hot
```

before the candidate's interconnect proxy loses its advantage. These equations are exact for the stated proxy and **not** a claim of a physical power law.

## Frozen analytical sensitivity sweep

| RC | V296 SPEF sum (pF) | Lowest-cap control (pF) | Uniform equal-activity proxy saving | Maximum uniform V296 activity ratio before reversal |
|---|---:|---:|---:|---:|
| Nominal | 6.995384 | Original: 7.531230 | 7.115% | 1.07660 |
| High | 14.361370 | Original: 16.040663 | 10.469% | 1.11693 |

Against the **optimized one-hot** control, the corresponding equal-activity savings are 9.862% nominal and 11.033% high RC; break-even candidate/control activity ratios are 1.10941 and 1.12401. The original controller is the lower-capacitance control in both cases, although it **fails the fixed 3.5 ns extracted setup gate**. This proxy comparison does not establish an equal-performance or equal-resource control.

**Constructive no-win counterexamples, frozen before switching traces:**

- With the control at effective activity 0.05 and V296 at 0.06 on every net (20% higher candidate activity), V296's wire proxy **increases by 11.462% nominal and 7.437% high RC** versus the lowest-capacitance control. This reverses the conclusion from aggregate capacitance alone.
- Under high RC, with background activity 0.05 for both architectures but V296's observed `issue_wave0[0]` net at activity 1.0, V296's wire proxy **increases by 4.611%** versus the lowest-capacitance control. The exact crossover hotspot activity is **0.709519** for the assumed background and control activity 0.05. This scenario is a sensitivity test, not an observed switching pattern.

## Prospective validation and kill condition

Before inspecting any workload switching outcomes, preserve the three distinct regimes: **uniform-activity predicted wire-proxy win**, **20%-activity-skew predicted no-win**, and **hot-net predicted no-win**. Measure net transition counts on previously sealed workload traces using matched post-route netlists and identical workloads, clocks, voltage and toggle-window accounting. Attribute net activity independently, including the high-fanout issue-wave hotspot. Validate the **sign** of the activity-weighted proxy against those counts; compare total power only after independently accounting for internal/leakage/clock energy and post-CTS parasitics. Recompute after the pending fourth-round electrical repair; its buffering may change both capacitance and glitch activity.

**Falsifier:** if workload-measured switching or post-CTS power erases the advantage, no V296 energy saving may be claimed even if total SPEF capacitance is lower. If physical repair or equal-resource control optimization erases V296's area/timing dominance, retire V296 under the existing primary gate. This sensitivity study cannot rescue a failed electrical gate.

**Research status:** prospective power-proxy sensitivity only. The fourth-round high-RC electrical experiment remains the decisive primary physical validation. Same-clock issue-throughput gain remains 0%; tile power, tile throughput and RTX-5090 equivalence are unproven. Workload holdouts remain **SEALED**.
