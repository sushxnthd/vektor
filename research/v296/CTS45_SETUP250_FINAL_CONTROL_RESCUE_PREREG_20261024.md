# V296 matched post-CTS setup250 final bounded control-rescue preregistration (2026-10-24)

**Frozen before running setup250.** Source evidence: completed setup150 workflow https://github.com/sushxnthd/vektor/actions/runs/40111559059 and result `CTS45_SETUP150_CONTROL_RESCUE_RESULT_20261024.md`.

## Question and hypotheses
Can the strongest existing serial one-hot control be brought above the *original* +50 ps setup guardband without exceeding the 7400 um^2 controller area ceiling, under the same physical constraints as V296? This is a **last bounded slack-margin escalation**, not a search for a favorable setting. The setup150 run produced serial +19.125 ps, 7221.899967 um^2, zero slew/cap/DRC, and failed its +50 ps feasibility gate.

**Prospective conditional prediction:** increasing the *identical* post-CTS setup repair target from 150 ps to 250 ps for both contestants may close the serial control's remaining 30.875 ps deficit within its 178.100 um^2 area headroom; V296 is predicted to remain feasible. The possibility of a null response or a loss of candidate advantage is explicitly retained.

## Frozen controls and intervention
- Sole active mechanism: V296 pairwise arbitration; strongest control: serial one-hot. V287 remains retired.
- Same RTL, synthesis flow, 3.5 ns clock, Nangate45 pinned platform, 45% placement density, identical floorplan, 2x OpenRCX resistance and capacitance, propagated-clock CTS, 16 maximum fanout, 250 ps max transition, 7400 um^2 area ceiling, 50 ps setup guardband and nonnegative hold slack.
- Same control-only fifth pre-CTS optimization already used in prior matched experiments. **Do not remove control optimization.**
- Only intervention versus setup150: both variants use `repair_timing -setup -slack_margin 0.250` instead of 0.150. Identical `repair_design -cap_margin 20 -slew_margin 40`, `repair_timing -hold`, global/detailed route, SPEF write/read, extraction, and independent audits.
- Do not alter clock period, density, technology, wire RC, output load, fanout, or area ceilings to force a pass.

## Independent decisions
- Incomplete evidence => `INCOMPLETE_NO_PHYSICAL_CLAIM`.
- Candidate fails area, 50 ps setup, hold, electrical or DRC => `CANDIDATE_GATE_FAIL`.
- Control fails same => `CONTROL_RESCUE_FAIL_NO_PARETO_CLAIM`.
- Both feasible but candidate area saving <10% or setup advantage <200 ps => `FEASIBLE_PARETO_FALSIFIED`.
- Both feasible and candidate area saving >=10% and setup advantage >=200 ps => `FEASIBLE_PARETO_SUPPORTED`, **still not strict equal-consumed-area superiority or signoff**.

A failed setup250 result ends blind setup-margin escalation. Next science must analyze control critical-path structure, matched equivalent-resource architecture options, and/or integrated tile bottlenecks, not repeatedly tune the margin. Preserve every negative result. Existing workload holdouts remain sealed; zero same-clock issue IPC gain is the null expectation.
