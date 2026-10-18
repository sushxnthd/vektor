# V198 symbolic load results

Independent second-parser checks: PASS 8/8 headroom/mode cases. Regression tests: PASS 6/6. No physical STA executed.

| Headroom | Mode | First violating added wire load (fF per sink) | Violations at 0.5 fF/sink | Violations at 1.0 fF/sink |
| --- | --- | ---: | ---: | ---: |
| 0% | Control | 0.012233 | 38 | 68 |
| 0% | Cutset | 0.010735 | 28 | 65 |
| 10% | Control | 0.179003 | 27 | 57 |
| 10% | Cutset | 0.205676 | 20 | 57 |
| 20% | Control | 0.401853 | 14 | 44 |
| 20% | Cutset | 0.430663 | 8 | 45 |
| 30% | Control | 0.728665 | 0 | 20 |
| 30% | Cutset | 0.627255 | 0 | 21 |

Evidence class: symbolic unplaced Nangate45 mapped-netlist capacitance stress; no extracted wire model, timing, power, or novelty. Executable code and raw JSON are preserved in the local V198 evidence ZIP but are not committed because GitHub safety checks rejected executable and CSV writes.
