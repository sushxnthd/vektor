# V296 extracted-SPEF net-load concentration audit (2026-10-24)

**Evidence tier:** independent read-only postprocessing of the six immutable detailed-route/OpenRCX SPEFs in [run 39995731088, artifact 12523741140](https://github.com/sushxnthd/vektor/actions/runs/39995731088/artifacts/12523741140). Code: `research/v296/spef_load_summary.py`. **Exploratory diagnostic, not a preregistered endpoint prediction.** The frozen extracted physical gate remains **FAILED**.

## Measured SPEF structure

Each net's `*D_NET` total is recorded in pF (`*C_UNIT 1 PF`). The table sums those reported net totals, **not** switched capacitance or power. Cell-input connections are counted from `*CONN` `*I ... I` records, excluding top-level ports. Independent placement, resizing and routing were performed for each scenario.

| Controller | RC | SPEF nets | Sum of declared net totals (pF) | Largest declared net total (pF) | Maximum cell-input connections on one net |
|---|---|---:|---:|---:|---:|
| Original | nominal | 3738 | 7.531230 | 0.048816 | 54 |
| Original | high | 3853 | 16.040663 | 0.097159 | 54 |
| Optimized | nominal | 3591 | 7.760770 | 0.059401 | 73 |
| Optimized | high | 3629 | 16.142257 | 0.122497 | 73 |
| **V296** | nominal | **3216** | **6.995384** | **0.061701** | **79** |
| **V296** | high | **3264** | **14.361370** | **0.127312** | **79** |

At high RC, V296 has **10.06% fewer SPEF nets** and **11.03% lower sum of reported net total capacitances** than the optimized control, yet its **largest individual net capacitance is 3.93% higher**, and its maximum counted cell-input connections per net is **79 versus 73**. V296 high RC has **33 maximum-slew violations**; optimized high RC has zero, although optimized high RC fails setup. Lower aggregate reported capacitance therefore **does not guarantee slew closure**.

## High-RC V296 high-capacitance candidates

| Net | SPEF declared total (pF) | Cell-input connections |
|---|---:|---:|
| `issue_wave0[0]` | 0.127312 | 79 |
| `issue_wave1[0]` | 0.119551 | 69 |
| `issue_wave0[1]` | 0.118062 | 62 |
| `issue_wave3[1]` | 0.109197 | 61 |
| `issue_wave3[0]` | 0.107112 | 66 |
| `issue_wave2[1]` | 0.101154 | 58 |

These are **load-concentration candidates only**. They are **not** identified as the 33 violating endpoints. Pin transition depends on driver sizing, net RC distribution, fanout, and input slew, not solely total net capacitance.

## Testable physical hypothesis

The high-RC electrical failure may be concentrated in a small set of high-fanout `issue_wave` nets rather than distributed across the controller. This is a hypothesis, **not a finding**. The separately preregistered immutable DEF/SPEF OpenROAD replay must first reproduce all 33 violations and report the actual violating pins. If the offending pins do not map to these nets, **reject this concentration hypothesis**.

Only then freeze matched, independent post-route repair for V296 and both controls. The conditional V296-only high-RC area budget for >=10% savings against the unchanged optimized control is **259.961874 um2**. Equal-resource Pareto controls, setup/hold, DRC, and slew/cap closure remain mandatory.

**Limitations:** `*D_NET` sums are not power estimates; independent routing means the nominal/high ratio is not fixed-topology sensitivity; the summary does not establish a frequency, IPC, tile, or GPU improvement. No workload holdouts opened. V287 remains retired.
