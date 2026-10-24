# V296 symmetric post-CTS setup-margin 150 ps control-rescue experiment — preregistered 2026-10-24

## Prior evidence, not new holdout

The sole active mechanism remains V296 pairwise bank-conflict admission. V287 stays retired. [Fanout-16 run 40108270016](https://github.com/sushxnthd/vektor/actions/runs/40108270016) completed detailed route and extracted propagated-clock CTS on both contestants at 45% placement target, 3.5 ns, 2x RC, Nangate45. V296 passed area/timing/electrical constraints (6239.828210 um2, +0.430410 ns setup, +0.284848 ns hold, zero slew/cap/DRC), while serial one-hot remained setup-infeasible (7167.901828 um2, -0.074402 ns setup, +0.275125 ns hold, zero slew/cap/DRC). Thus the aggregate correctly reported `FANOUT16_CONTROL_INFEASIBLE_NO_PARETO_CLAIM`. The output-net topology prediction succeeded (15 loads, down from 79), but that does **not** establish a feasible-control win. See [falsification and rescue boundary](CTS45_FANOUT16_PHYSICAL_CLOSURE_NO_PARETO_20261024.md).

## Frozen intervention

Retain the fanout-16 topology repair, **all** clock/load/geometry/RC and technology constraints, control's extra fifth pre-CTS optimization, and existing post-CTS hold repair. Change exactly one post-CTS setup command, identically for both contestants:

```tcl
repair_timing -setup -slack_margin 0.150
```

This replaces the previous `repair_timing -setup` after `set_max_fanout 16` and `repair_design -cap_margin 20 -slew_margin 40`. OpenROAD's resizer documentation describes `-slack_margin` as an additional timing margin for setup repair. It is **not** a clock relaxation; the frozen 3.5 ns period remains unchanged. Pinned OpenROAD version is unchanged; if this option is unsupported, report tool incompatibility rather than adjusting the intervention. Both contestants are independently synthesized and physically implemented. No candidate-only exceptions, no artificial control handicap, no changed output load, no extra rounds selected after observing outcomes.

## Prospective decision rules

1. **Completeness:** both contestants must complete CTS, detailed routing, fresh SPEF extraction, and independent parsing; zero DRC, slew and capacitance violations, hold >= 0 ns, area <= 7400 um2, setup >= +0.050 ns. Failed or incomplete contestants remain visible.
2. **Control rescue prediction (deliberately falsifiable):** the +150 ps margin is sufficient to bring the serial-onehot control to >= +50 ps extracted setup slack. If not, classify `CONTROL_RESCUE_FAIL`, not V296 Pareto superiority.
3. **Candidate survival:** V296 stays feasible under the same policy. If not, classify `CANDIDATE_GATE_FAIL` and do not claim a benefit.
4. **Pareto:** only when both pass, V296 final area saving >= 10% and extracted setup slack lead >= 200 ps. If either bound fails, the architecture's frozen Pareto claim is falsified in this setting. No equal-consumed-area claim even if both pass.
5. **Rescue budgets at historical starting point (NOT acceptance data):** control needs >=124.402 ps more setup slack than previous run and has only 232.098 um2 area ceiling headroom. Candidate may add only 211.283 um2 at unchanged control area before losing the 10% relative saving. Differential setup advantage may shrink 304.812 ps before falling below +200 ps.
6. **Holdouts:** workload holdouts remain sealed; no post hoc workload selection, tile throughput claim, power signoff, or RTX-5090 equivalence.

## Reproducibility and falsification

Use `research/v296/cts45_setup150.tcl`, `run_cts45_setup150.sh`, `audit_cts45_setup150.py` and `.github/workflows/v296-cts45-setup150.yml`. The independent checker verifies both frozen intervention markers, their post-CTS/pre-route order, all electrical evidence, and requires both contestants feasible for a Pareto decision. Preserve all negative artifacts and full logs. No branch or mechanism change.
