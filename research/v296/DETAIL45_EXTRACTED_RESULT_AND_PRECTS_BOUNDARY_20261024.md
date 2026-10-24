# V296: matched 45% detailed-route OpenRCX result and pre-CTS boundary (2026-10-24)

## Provenance and frozen protocol

Source: [GitHub Actions run 40083815972](https://github.com/sushxnthd/vektor/actions/runs/40083815972), source commit `ffca24d3c620a8dfe2e7e895ae872676a38d7e4c`, preregistration `DETAIL45_MATCHED_EXTRACTED_PREREG_20261024.md`. This is a **completed two-contestant detailed-route, extracted-parasitics experiment**, unlike earlier global-route-only results. The independent aggregate job exited 3 **because the control failed the physical timing gate**, not because the two physical contestant jobs failed. Both contestant jobs completed successfully and their raw archives remain attached to the run. Artifact ZIP SHA-256 values from the Actions logs: pairwise `319f112eabbfa507915baf892ae875ecac473c980b2436b25f59b618c67a9d5d`; serial one-hot `a855583f145ec2fb8dffa970a420c81c04fb8c69b3c8fc92c05316198b53a667`. The independent audit artifact is `12555789130`. These checksums are from hosted upload/download logs; no separate local archive-byte verification is claimed here.

Both contestants used 45% placement target, same 140×140 µm die / 120×120 µm core, Nangate45, 3.5 ns period, high-RC 2× parasitic scaling, the same electrical and routing constraints, and full detailed route plus SPEF. The control received an additional fifth repair round. This is **matched floorplan and common resource ceiling**, not equal consumed area.

## Independent aggregate measurements

| Metric | V296 pairwise | Serial one-hot |
|---|---:|---:|
| Controller area (µm²) | 5,987.926155 | 6,942.599828 |
| Extracted ideal-clock setup slack (ns) | +0.418903 | −0.173046 |
| Extracted ideal-clock hold slack (ns) | +0.282110 | +0.267903 |
| Max slew violations | 0 | 0 |
| Max capacitance violations | 0 | 0 |
| Detailed-route DRC violations | 0 | 0 |
| Detailed-route/SPEF complete | yes | yes |
| Frozen physical gate: area ≤7,400; setup ≥0.050; hold ≥0 | **PASS** | **FAIL: setup** |

The measured controller area saving is **13.750953%**, and the extracted setup-slack advantage is **+591.949 ps**. Both meet the numerical conditional Pareto predictions (≥10% area saving and ≥200 ps setup lead). However, the preregistration requires **both contestants to pass** before classifying a matched feasible-control Pareto win. Since serial one-hot fails setup, the correct independent-audit decision is `CONTROL_INFEASIBLE_NO_MATCHED_PARETO_CLAIM`, **not a demonstrated architectural victory**. V296's own 45% detailed-route gate **passes**. The known 65% density failure remains in force.

## A falsifiable post-route clock-tree sensitivity boundary

A simple, optimistic *uniform effective skew* `k` changes setup and hold as
`S' = S + k - P_s`, `H' = H - k - P_h`. For chosen setup/hold guardbands `G_s,G_h`, simultaneous feasibility requires

`G_s + P_s - S ≤ k ≤ H - G_h - P_h`.

The corresponding *necessary optimistic* non-skew penalty budget is `S + H - G_s - G_h`. This assumes a single freely adjustable effective skew, fixed data paths, and no CTS-induced parasitic or area changes; real launch/capture endpoints have different, correlated skews, so this is **not sufficient for physical closure**. It is not a new universal predictive law.

| Analytical guardband and penalty scenario | V296 skew window (ps) | Serial one-hot skew window (ps) |
|---|---:|---:|
| 0 ps setup, 0 ps hold; zero penalties | 701.013 | 94.857 |
| 50 ps setup, 0 ps hold; zero penalties | 651.013 | 44.857 |
| 50 ps setup, 50 ps hold; zero penalties | 601.013 | −5.143 (infeasible in this model) |
| 50 ps setup, 50 ps hold; 20 ps non-skew penalty each | 561.013 | −45.143 (infeasible in this model) |

**Critical qualification:** the serial one-hot control could, in the optimistic model, recover 50 ps setup margin by trading at least 223.046 ps of hold margin for setup margin, leaving 44.857 ps hold. Thus the measured pre-CTS control setup failure does **not** prove it is intrinsically impossible to clock-tree-close the control when zero hold guardband is allowed. Conversely, V296's measured pre-CTS setup advantage cannot be extrapolated to post-CTS frequency without implementing CTS and hold repair.

The companion `detail45_postroute_envelope.py` is an independent fail-closed sensitivity analysis that reads the aggregate JSON, checks both contestant identities, evidence tiers, electrical cleanliness, finite values and agreement with the independent comparison, then emits these scenarios. It rejects contaminated or incomplete input. Its local adversarial self-test passed before commit.

## Decision and next discriminating experiment

- **Keep V296 as the sole provisional mechanism** and retain V287 as retired. Do not create a new active mechanism or PR.
- **Freeze** the 45% postroute numbers and guardband sensitivity above before any CTS results are opened.
- Next: implement and run *matched* CTS and post-CTS hold/setup repair on both extracted, detailed-routed designs, preserving clock-cell area, added wire/capacitance, final DRC, setup and hold endpoints. Compare with the same floorplan and control-advantaged repair protocol. Do not change the clock, area ceiling, RC model or density to rescue a failure.
- If CTS invalidates V296's own feasibility or eliminates the numerical area/timing advantage, record the falsification and retire or redesign the mechanism rather than reclassifying a failure.
- Even if CTS passes, **equal consumed area**, power/activity, tile-level critical-path propagation, memory/port limits, unseen workload predictions and a nontrivial positive boundary law remain unproven. Functional equivalence means no per-cycle admission advantage at the same resources and clock. Never claim RTX-5090 equivalence.

**Evidence tier:** matched detailed route + OpenRCX, ideal clock, no CTS, no switching-power measurement, no integrated GPU benchmark. **World-class completion gate: NOT REACHED.**
