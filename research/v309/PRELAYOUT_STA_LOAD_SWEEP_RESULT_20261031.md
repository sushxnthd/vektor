# V309: independently audited prelayout STA load sensitivity (2026-10-31)

**Result: PASS at the frozen optimistic prelayout timing screen.** [GitHub Actions #41158628194](https://github.com/sushxnthd/vektor/actions/runs/41158628194), source commit `77fd70db3ce22d1c54cd2640b2fdd1292756ec0a`, completed matched synthesis, six OpenSTA analyses, and the independent corrected arrival-time audit. [Raw source-pinned evidence artifact #13026455231](https://github.com/sushxnthd/vektor/actions/runs/41158628194/artifacts/13026455231). **This is preplacement, zero-extracted-wire-RC timing, not routed timing or GPU clock frequency.**

## Preserved audit correction

The [first STA attempt #41158430070](PRELAYOUT_STA_FIRST_ATTEMPT_TOOL_FAILURE_20261031.md) failed because the installed OpenSTA 2.0.17 rejected unsupported report options. A later run #41158508978 returned an apparent 1.00 ns delay for both designs and passed its first checker, but that **was a false positive**: the loose regex matched the next line's 1.00 ns virtual-clock required time rather than the preceding 0.50 ns arrival. **Invalidate that pass.** The checker was repaired to accept exactly one positive, line-anchored `data arrival time` value, reject Tcl errors, and include an adversarial fixture that would catch the false 1.00 ns parse. Only the corrected run #41158628194 below is accepted.

## Frozen symmetric input-slew and output-load results

The source-verified NangateOpenCellLibrary typical corner and Ubuntu 22.04 OpenSTA 2.0.17 were used for both designs, with 36 matched input bits, four matched grant outputs, a virtual reference clock, zero external delays, and no pipeline stages. Each row reports the worst constrained input-to-output data arrival time rounded to 0.01 ns by this OpenSTA build.

| Frozen corner | Input transition | Output capacitive load | Compact greedy | Factored exact-max | Candidate/baseline delay ratio |
|---|---:|---:|---:|---:|---:|
| Optimistic | 0.020 ns | 0.005 pF | **0.50 ns** | **0.45 ns** | **0.9000x** |
| Nominal | 0.050 ns | 0.020 pF | 0.51 ns | 0.47 ns | 0.9216x |
| Stressed | 0.100 ns | 0.100 pF | 0.53 ns | 0.49 ns | 0.9245x |

The **frozen optimistic kill ceiling** was `D_exact/D_compact < 1.0973483338585934`, derived before outcomes from the prospective hot2 admission-gain prediction. The observed **0.9000x** passes with margin. Across these three **zero-wire** corners, the candidate's mapped combinational delay is approximately 7.5–10% lower than compact greedy's, despite the candidate's 20.85% larger mapped area in the separately matched Ubuntu-latest Nangate45 synthesis run.

These values are reported to only two decimal places, so small differences should not be overinterpreted. The difference between generic logic depth (18 vs 16) and mapped STA delay (0.45 vs 0.50 ns) demonstrates why generic path edges cannot substitute for cell timing.

## Scientific decision

**Retain the single factored exact-max mechanism for the next physical gate.** It has passed RTL functional checks, generic-cell and matched standard-cell area ceilings, prospective IID issue-admission prediction, and a frozen prelayout timing screen against a competent same-policy greedy baseline. This is a credible *early-stage circuit result*, not yet a physically validated GPU architecture result.

**Remaining hard blockers:** placement and routing, extracted interconnect parasitics, max-cap/slew/fanout electrical violation checks (unsupported in the installed older OpenSTA command set), actual buffering and wire-length sensitivity, fairness/liveness, real GPU operand-bank traces, queue/occupancy/bandwidth and tile-level throughput. Any of these may erase the gain; the mechanism must be killed if the integrated matched-resource boundary fails. The old brute-force implementation remains rejected; V287 and V296 physical no-go evidence remain preserved. No RTX 5090 equivalence claim.
