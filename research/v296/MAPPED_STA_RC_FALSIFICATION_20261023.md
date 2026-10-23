# V296 mapped-STA evidence audit: electrical gate fails (2026-10-23)

Source: https://github.com/sushxnthd/vektor/actions/runs/39916324950
Raw evidence: https://github.com/sushxnthd/vektor/actions/runs/39916324950/artifacts/12485466262
Independent reproduction: `python3 research/v296/physical_evidence_audit.py build/v296/sta/sta_summary.json` (intentional exit code 3 when the physical gate fails).

## Corrected interpretation of the actual mapped timing paths

The corrected `report_checks` data-path report in all nine cases begins at a **coreclk-triggered flip-flop** and ends at **issue_valid[3]**, not at asynchronous reset recovery. The updated data-path evidence is therefore more informative than the preceding reset-dominated report. However, the summary's `report_worst_slack` values remain numerically identical to its full-path values; these are **pre-placement path-budget proxies, not validated fmax**. Do not claim a 27.86% clock-frequency improvement.

| Nominal Nangate45 mapped variant | Cell area (um^2) | 2 ns setup slack (ns) | Path-budget proxy (ns) | Slew violations | Cap violations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 4046.126 | -3.000501 | 5.000501 | 987 | 39 |
| Optimized equal-resource control | 3780.126 | -2.801229 | 4.801229 | 979 | 35 |
| V296 pairwise | 3098.368 | -1.755002 | 3.755002 | 698 | 41 |

The nominal path-budget ratio is 4.801229/3.755002 = **1.278622**, conditional on this **electrically invalid** netlist model. Both matched designs miss the 2 ns clock and violate slew and capacitance limits. The mapped controller-area saving is **681.758 um^2**, or **18.0353%** against the optimized control. No repaired physical area or timing advantage has been demonstrated.

## Wire/load sensitivity falsification

Across the three nominally low/medium/high uniform per-net RC settings, the modeled critical-period proxies changed by:

| Variant | Low-to-high change (ns) | Fraction of nominal proxy |
| --- | ---: | ---: |
| Original | +0.001312 | 0.02624% |
| Optimized control | +0.001258 | 0.02620% |
| V296 | +0.001128 | 0.03004% |

**The current RC sweep barely perturbs the path** despite changing both nominal lumped per-net capacitance and resistance by a factor of four. This experiment does not establish realistic wire sensitivity, placement robustness or physical routability. Uniform lumped RC is not extracted interconnect. A meaningful next gate requires matched placement and electrical repair, with extracted parasitics or a clearly validated length/fanout model.

## Compact physical break-even boundary

Let `A_c^0=3780.126` and `A_p^0=3098.368` um^2 be mapped controller areas; `R_c` and `R_p` the additional area of matched electrical/timing repairs. The area advantage survives iff

```
R_p - R_c < 681.758 um^2.
```

A controller timing/throughput win additionally requires both repaired designs to meet the same electrical limits and `D_p^repair < D_c^repair` on a comparable critical path. For an occupancy-limited or bandwidth-limited tile, a faster controller need not improve workload throughput. The frozen unseen win/no-win workload regimes remain sealed.

**Decision: physical gate FAIL, mechanism provisionally active pending matched electrical repair and placement.** Do not unseal holdouts, integrate the tile, or claim a frequency, power or RTX 5090-class advantage. Retire V296 if the repaired equal-resource comparison removes its area/timing benefit or its implementation cannot satisfy the electrical gate. V287 remains retired.
