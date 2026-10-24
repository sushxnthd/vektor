# V296 first placement/repair evidence: original control, low RC (2026-10-23)

Source: GitHub Actions run 39927207169, artifact 12489199681. The run used pinned OpenROAD v2.0-17598-ga008522d8 on Ubuntu 22.04, revision-pinned Nangate45 LEF/Liberty, and the same 140×140 µm die / 120×120 µm core intended for the matched comparison.

**Evidence tier: one exploratory placement-and-repair control case, not a completed equal-resource physical comparison.** No V296 candidate or optimized control placement result was obtained in this run. Workload holdouts remain sealed.

The original-controller, low-RC case reached placement and electrical/setup repair before stopping at an OpenSTA CLI incompatibility in `report_checks -group_path_count`. The error was repaired in commit `80a7d65012d90aaa8f1d081b68ad497bff03453f`. An additional correction converts OpenROAD's internal SI area units into µm²; the table below uses `report_design_area` from the raw log rather than the incorrectly labeled initial metric.

| Original control, low RC | After placement | After repair |
| --- | ---: | ---: |
| Standard-cell area (µm²) | 3,857 (reported rounded) | 6,172 (reported rounded) |
| Exact `rsz::design_area` converted to µm² | 3856.734 | 6171.732 |
| Maximum-slew violations | 1348 | 0 |
| Maximum-capacitance violations | 42 | 0 |
| Worst 2 ns setup slack (ns) | -3.748819 | -1.037068 |

Repair increased cell area by **2314.998 µm² (60.02%)**, while improving the worst slack by **2.711751 ns**. The repaired control is electrically clean at this placement-based parasitic estimate but **still misses the frozen 2 ns setup target**. OpenROAD reported 80 buffers inserted and 1348 cells resized during electrical repair, followed by 87 buffers, 209 resizes and 19 cloned instances during setup repair; these counts are tool diagnostics, not proof of physical signoff.

**Important cross-tool caveat:** This runner uses Ubuntu 22.04 Yosys, while the earlier mapped-area evidence came from another runner/toolchain. The old 681.758 µm² mapped difference cannot be assumed to be the break-even budget in this new flow. The decisive area comparison must use *same-run, same-tool* control and V296 measurements, both before and after repair.

The first run stopped before global routing because OpenROAD 2024 does not support the supplied `report_checks -group_path_count` option. Thus it supplies **no wire-topology sensitivity**, no candidate/control PPA comparison, and no basis to retire or validate V296. A corrected nine-case matched workflow was launched as run 39927501835. Do not open the frozen workload holdouts or claim a clock-frequency win until the full physical gate is independently audited.
