# V296 matched integrated-slice repair frontier (2026-10-25)

**Evidence tier: algebraic sensitivity on original, measured, *failed* post-route physical results; no repair experiment has been performed.** Original paired physical run [40156470550](https://github.com/sushxnthd/vektor/actions/runs/40156470550) remains immutable and falsified. The in-situ extracted critical-path experiment [40173311725](https://github.com/sushxnthd/vektor/actions/runs/40173311725) was still running when this sensitivity was constructed. This analysis is independent of its unobserved endpoints and is not a replacement for extracted STA.

## Measured inputs and hard constraints

| Original post-route result | V296 | Serial one-hot |
|---|---:|---:|
| Setup slack (ns) | -1.047895 | -1.859922 |
| Hold slack (ns) | -0.036622 | -0.019796 |
| Cell area (µm²) | 17,857.644252 | 18,953.830505 |
| Cap violations | 3 | 3 |

Original gate: **setup ≥ +0.050 ns, hold ≥ 0 ns, cap/slew/DRC = 0, area ≤ 30,000 µm², both contestants**. Both failed; there is no feasible integrated GPU result.

Define hypothetical post-route changes in setup slack `g_s,j`, hold slack `g_h,j`, and cell area `dA_j`, with `j` either V296 or serial control. Exact necessary constraints, before any new routing or STA:

```
g_s,V296 >= 1.097895 ns           g_s,serial >= 1.909922 ns
g_h,V296 >= 0.036622 ns           g_h,serial >= 0.019796 ns
A_V296 + dA_V296 <= 30000 µm²    A_serial + dA_serial <= 30000 µm²
cap_V296 = cap_serial = 0        plus zero slew/DRC and new extracted STA
```

These are **minimum required improvements**, not achieved repairs or physically attainable estimates. Setup gains may conflict with hold, capacitance, congestion, power, and area; all must be re-extracted after actual changes.

## Quantitative falsifiers

1. **Symmetric setup-only repair is insufficient.** If both receive the same hypothetical +2.0 ns setup improvement, both setup checks pass, but both still fail hold and capacitance. This cannot be called closure.
2. **Closing both at exactly the minimum setup threshold removes the candidate's timing lead.** Original lead is `0.812027 ns`. After repair it is `0.812027 + g_s,V296 - g_s,serial`. At their respective minimum gains, this is exactly zero. Any claimed persistent +0.20 ns lead requires `g_s,serial - g_s,V296 <= 0.612027 ns` *and* both contestants passing all physical checks. Independent physical optimization could change this differential; it cannot be assumed.
3. **Area headroom is not an equal-area result.** V296's original final cell area is 1,096.186253 µm² smaller (5.78345%). The control could hypothetically reinvest this entire amount to reach equal consumed cell area; the timing, routing, and power effect of that reinvestment is unknown. A strongest-control study must permit its own optimization under the same budget.
4. **No frequency claim follows from negative slack.** The original 3.5 ns implementation fails setup/hold/capacitance. Dividing nominal clock period by a slack-adjusted period would not establish a realizable Fmax, especially with hold and cap violations. Same-clock admission throughput is equal by RTL equivalence.

## Falsification and reproduction

`python3 research/v296/paired_repair_frontier.py --self-test` exercises exact repair thresholds, the both-infeasible original, setup-only false positives, minimum-gain zero-lead case, hypothetical equal-area accounting, and invalid inputs. `--scenario original|setup_only|minimum_repairs` prints transparent numerical sensitivity output. It labels even its hypothetically passing setup/hold/area/cap case **NOT_EVALUATED** for full physical closure, since DRC/slew and re-extracted parasitics are unobserved.

## Next decision

Await in-situ path endpoints and source-hashed independent physical audit. If it completes, preregister a *new* symmetric or path-targeted repair **before** observing the new repair outcome, preserve the original failed gate, and include a truly area-budgeted optimized serial control. If it does not complete, report the tool failure and avoid invented endpoints. This analysis cannot rescue V296. V287 stays retired; prospective workload holdouts stay sealed; Kernellum PR #119 remains untouched.
