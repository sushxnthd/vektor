# V317 degree-head RTL adversarial control: independent small-bank result (2026-11-03)

## Evidence chronology
Frozen [protocol](FROZEN_DEGREE_RTL_CHALLENGE_20261103.md) committed first at `115a29e`, before RTL and testbench. RTL `b1fcc03`, independent testbench `fad87c1`, exhaustive Python checker `723f7a3`. The Python checker was executed locally on all stated configurations before this report. Hosted RTL/synthesis results remain **pending**, not passed.

## Independent exhaustive combinational evidence
Every request has two charged reads, every bank has two read ports, four candidate slots, oldest slot mandatory if valid, all 16 request-valid masks.

| Banks | Cases | Compact greedy grants | Degree grants | Exact head grants | Degree wins / losses vs greedy |
|---|---:|---:|---:|---:|---:|
| 2 | 4,096 | 5,210 | 5,226 | 5,258 | 16 / 0 |
| 3 | 104,976 | 158,409 | 158,529 | 159,225 | 216 / 96 |

The exact 2-bank snapshot gain is only **1.003071x** degree/greedy, and the 3-bank gain only **1.000758x**. These are aggregate *snapshot grant counts under uniform enumeration*, not throughput, measured GPU IPC, or a realistic workload distribution. The degree heuristic is not a dominance theorem: the 3-bank exhaustive audit finds **96 cases where degree is worse than greedy** and 696 cases where degree loses a grant versus the exact oldest-preserving selector. All counted grants obey bank capacity and head inclusion. The checker does not import the RTL or any prior simulator.

Frozen witness where degree wins: valid 1110, requests [(0,0),(0,1),(0,0),(1,1)]; greedy grants 0010, degree 1100. Frozen witness where degree loses: valid 1111, requests [(0,1),(0,2),(1,2),(2,2)]; greedy grants 0111, degree 1001. These demonstrate the mechanism's context dependence and prevent an unconditional positive claim.

## RTL scope
`degree_head_simple_control.sv` sorts three non-head requests by valid-neighbor bank-overlap degree and feeds the unchanged V309 compact greedy bank admission logic through a permutation. It has no new ports, no operand reuse and no extra queue entries. The added sorting and muxes are real RTL cost, not assumed free. `tb_degree_head_simple_control.sv` independently enumerates 4,096 two-bank cases, checks bank legality and frozen win/loss witnesses. The GitHub Actions workflow separately synthesizes both controllers with identical generic Yosys settings.

**Physical status:** generic Yosys cells, routed area, clock, power, wire, load and electrical signoff have not yet been confirmed. Do not interpret the model's small snapshot gains as silicon throughput. The prior V317 RF-proxy physical failures remain binding.

## Decision
This experiment is a *competent low-cost adversarial control*, not a new active architecture mechanism. The uniform-enumeration average grant advantage is too small to justify a GPU claim without a workload-derived concentration predictor, finite-source queueing and physically legal matched RTL. If the degree RTL fails independent simulation or its cost dominates the service benefit, reject it. Do not revive the already-falsified V317 integrated-area case or the historical V287 dual-warp fusion.

## Reproduction
```sh
python3 research/v317/rtl/audit_degree_head_exhaustive.py > /tmp/v317-degree-audit.json
iverilog -g2012 -s tb_v317_degree_head -o /tmp/v317-degree-tb \
  research/v317/rtl/compact_greedy_equal_policy.sv \
  research/v317/rtl/degree_head_simple_control.sv \
  research/v317/rtl/tb_degree_head_simple_control.sv
vvp /tmp/v317-degree-tb
```
Hosted workflow: `.github/workflows/v317-degree-simple-control.yml`. All negative counterexamples must be preserved even if RTL/synthesis later passes.


## Hosted RTL and generic synthesis outcome (verified 2026-11-03)

The first hosted run [#41509456281](https://github.com/sushxnthd/vektor/actions/runs/41509456281) **failed**: Icarus exposed stale bank-tag sensitivity caused by helper functions reading module-global inputs, and Yosys rejected a nonconstant expression in a constant function. This failure was preserved. Commit `e613dd0` repaired both by making bank buses explicit pure-function inputs.

The repaired [GitHub Actions run #41509686509](https://github.com/sushxnthd/vektor/actions/runs/41509686509) **passed** independent Python enumeration, Icarus RTL simulation, both frozen witnesses and identical generic Yosys synthesis. The 4,096 two-bank RTL cases passed, matching 5,226 degree grants and 5,210 compact greedy grants.

Generic Yosys synthesis (same `read_verilog -sv; synth -top ...; stat` flow):
- Compact V309 greedy: **260** generic cells.
- Degree-head challenger: **734** total generic cells, including the compact admission submodule and sorting/permutation logic.
- Relative generic-cell cost: **2.823x** compact greedy, or **+182.3%**, for just **+0.0758%** aggregate three-bank snapshot grants in the independent enumeration.

These are generic technology-independent cells, **not** matched standard-cell area, physical timing, electrical signoff, power or sustained GPU throughput. The evidence is strongly unfavorable to the degree-control hardware case, but it is not a substitute for a legal matched physical comparison. No positive architecture promotion is justified. Preserve the negative result rather than tuning the snapshot distribution post hoc.
