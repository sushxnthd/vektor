# V296: fourth-round critical-path decomposition and closure falsification (2026-10-26)

## Evidence and reproducibility

The paired hosted diagnostic [run 40270157106](https://github.com/sushxnthd/vektor/actions/runs/40270157106) **completed both contestants** at the identical fourth pre-CTS global-routing checkpoint. Pairwise artifact **12628653770**, ZIP SHA-256 `0e19aad4f16a01ad513218c8eb21f199f265e2638b5a1c75ae05049d0080a6c4`; serial artifact **12628959676**, ZIP SHA-256 `c54f81fe263e94a8f5cd72c08a6c844e45aabf59015bfbf207227085fedac178`. The independent [checker](fourth_cone_independent_audit.py) reads each immutable ZIP, validates its digest, checks physical tier and 3.5 ns clock, maps STA start/end cells back to mapped netlist flops, reconciles path delay to arrival time, and partitions the actual reported worst path by buffer/inverter versus other cells. Reproduce with `python3 research/v296/fourth_cone_independent_audit.py PAIRWISE.zip SERIAL.zip`. A deliberately corrupted local ZIP was rejected by the SHA gate. Frozen observations are in [JSON](FOURTH_CONE_INDEPENDENT_RESULTS_20261026.json).

**This is pre-CTS STA with global-route-estimated parasitics, not extracted post-route timing or signoff.** No CTS, routed DRC closure, or fifth-stage serial rescue is included. The two worst paths are different, so per-path cell-class differences are *descriptive*, not an experiment isolating the cause of V296's lead.

## New physical result

| Metric | Pairwise V296 | Serial one-hot, same fourth stage |
|---|---:|---:|
| Reported worst setup slack | **-0.270212 ns** | **-0.755018 ns** |
| Worst path launch flop | `candidate.issue.scheduler.rr3[0]` | `strongest_serial.issue.scheduler.rr1[2]` |
| Worst path endpoint flop | `executed_data[31]` | `executed_data[7]` |
| Path arrival time | 3.729346 ns | 4.210938 ns |
| Reported path cells | 83 | 99 |
| Buffer/inverter cells | 31 | 42 |
| Buffer/inverter path delay | 0.864292 ns | 1.262620 ns |
| Other-cell path delay, including launch flop | 2.865023 ns | 2.948262 ns |
| Largest contiguous buffer run | 15 cells / 0.414697 ns | 9 cells / 0.253844 ns |
| Largest reported pin capacitance on this path | 66.700 fF | 177.390 fF |

**Falsification:** The critical path in *both* designs launches from a scheduler round-robin pointer and ends in the executed-data register, crossing the banked RF read and downstream execution combinational cone in the same cycle. The fourth-stage V296 slack lead is **484.806 ps**, but V296 itself still misses the +50 ps setup guard by **320.212 ps** before CTS and detailed routing. Serial misses it by **805.018 ps** at this checkpoint.

The two paths' data-arrival gap is 481.592 ps, of which 398.328 ps (82.71%) is the difference between their *reported buffer/inverter* contributions. This is a **path accounting observation, not a causal estimate**: endpoints, fanouts, routes and other cells differ. A pure gate-depth optimization cannot be presumed sufficient, and indiscriminate rebuffering cannot be presumed to close the candidate.

## Physical closure boundary, not an architecture speedup law

For the current path and *unchanged* required time, a prospective repair must satisfy
`delta_arrival_reduction >= 0.050 ns - measured_slack + delta_required_time_adversity`.
At the frozen pre-CTS checkpoint, the best-case required reductions are **320.212 ps V296** and **805.018 ps serial**. If **only** buffer/inverter delays could improve while all else remained fixed, this would require removing at least **37.05%** and **63.76%** of their respective current buffer contributions. Those are unrealistic optimistic thresholds, not demonstrated attainable savings; clock-tree skew, hold repair, coupling and detailed-route RC may make the target worse. These thresholds are **not** the required positive architecture law.

## Decision and next experiment

1. Preserve V296 as the sole provisional mechanism and V287 as retired. The frozen result neither establishes a feasible clock nor justifies a new mechanism.
2. Target the *scheduler round-robin pointer → RF operand-port selection/return → execute arithmetic → executed-data register* chain. Diagnose the actual mapped gate and wire bottlenecks. Any retiming/pipelining intervention must be **symmetric**, cycle-accurate, and checked for throughput, latency, occupancy and write/read hazards before physical promotion. A timing-only shortcut that changes execution semantics is not admissible.
3. Retain the serial control's independently optimized **fifth** repair for the final strongest-control comparison. Do not claim the fourth-stage area/slack lead is a matched final result.
4. The next decisive gate remains matched post-CTS and post-route setup >= +0.050 ns, hold >= 0, zero relevant electrical/DRC violations, matched consumed resources and bandwidth-constrained prospective workload gains. At equal clocks and identical slice counts, V296's formally equivalent admission grants imply **zero** issue-throughput gain.
5. No GPU speedup, measured power reduction, RTX-5090 equivalence, or world-class completion is claimed. Preserve original negative routing results and the Kernellum PR #119 holdouts without modification.
