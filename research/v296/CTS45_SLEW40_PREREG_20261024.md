# V296 fixed-margin post-CTS slew-repair falsification (preregistered 2026-10-24)

## Single-mechanism and evidence status

The sole active Vektor mechanism remains V296 pairwise bank-conflict admission. V287 stays retired. This is a *new* experiment; the preceding 10%-slew-margin post-CTS result remains a physical-gate FAIL (32 violating pins, all on `issue_wave0[0]`). The 40% repair setting below is frozen **before** observing any new physical results. Do not modify prior logs, reopen workload holdouts, or interpret a failed control as proof of equal-resource superiority.

## Causal hypothesis and fixed intervention

A pre-route, post-CTS fanout/slew-repair margin of **40%**, rather than the earlier **10%**, will give OpenROAD sufficient incentive to distribute the high-fanout issue-wave output before detailed routing. The intervention is exactly the single post-CTS command substitution `repair_design -cap_margin 20 -slew_margin 40` for the former `repair_design -cap_margin 20 -slew_margin 10`. Do not add selective net-specific buffers, relax `set_max_transition 0.25`, modify port loads, alter RTL, add repair passes, or change CTS topology parameters. Apply the same policy to V296 and the strongest serial-one-hot control; preserve the control's extra fifth pre-CTS repair round.

This is a hypothesis, not evidence that 40% will close electrical constraints. Because the historical baseline was inspected, any 10%→40% improvement is an *interventional follow-up*, not a prospective holdout.

## Frozen implementation and comparisons

- Technology: same pinned Nangate45 cells, pinned OpenROAD/OpenRCX, same Yosys netlist generation.
- Geometry: identical 140×140 µm die, 120×120 µm core, 45% placement-density target.
- Constraints: 3.5 ns clock, 0.25 ns max transition, 0.005 pF output load, 2× high-RC extracted model.
- Same CTS, clock buffers, propagated clocks, post-CTS setup/hold repair, detailed routing, SPEF extraction and zero DRC tolerance.
- Both contestants must complete. Preserve and report tool errors, incomplete routing, zero-violation failure, and setup failure as separate categories.
- Independent audit must confirm the exact `40` marker, same frozen constraints, CTS buffer insertion, extracted SPEF, route completion and post-route setup/hold/electrical values.
- Measure pre/post intervention controller area, inserted buffers if identifiable, setup/hold slack and per-net violating endpoints. Archive logs/DEF/SPEF/DRC and SHA-256 input digests.

## Predeclared kill gates

Candidate *physical feasibility*: area ≤7,400 µm², extracted setup slack ≥+0.050 ns, hold slack ≥0 ns, zero max-slew, zero max-cap and zero routing DRC violations. If any fails, **40%-margin policy is falsified** as a sufficient physical repair. If control also fails, report no feasible-control Pareto victory. Do not silently increase the margin or choose a post-hoc alternative.

Candidate *matched feasible-control Pareto advantage*: both feasible, V296 at least 10% lower **post-repair** area and at least +0.200 ns better **extracted** setup slack. If both feasible but these differences vanish, retire V296 under the current mechanism-selection gate. The older baseline had a 269.138 µm² candidate area-growth budget at fixed control area; recompute using actual paired results rather than treating that as a new measured outcome.

No same-clock, same-resource issue-throughput gain is predicted because V296 and serial one-hot have identical admission semantics. Even a successful electrical repair is **not** equal-consumed-area tile evidence, power signoff, GPU throughput validation, or an RTX-5090-equivalence claim. Unseen workload holdouts remain sealed.

## Falsification of the proposed cause

If 40% margin leaves the 32 violating pins or migrates violations to other nets, the single-net repair hypothesis is insufficient. If all violations disappear but setup, area or control Pareto gates fail, the policy is physically insufficient despite improved slew. Report per-net failures rather than optimizing after seeing the results.
