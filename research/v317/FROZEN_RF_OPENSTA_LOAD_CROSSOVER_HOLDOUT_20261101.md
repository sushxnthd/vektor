# Frozen prospective V317 output-load crossover holdout (2026-11-01)

**Freeze boundary:** this file must precede all holdout 40/60/80-fF OpenSTA evaluations. The previous 2/20/100-fF data were already observed in source-pinned run #41304535696; they are **training points**, not new holdouts. Do not refit this prediction after opening the holdouts.

## Predicted law (explicitly restricted to Nangate45 mapped, pre-route, fixed-priority RTL)

Let \(D(L)=t_{pairwise,fixed}(L)-t_{source,fixed}(L)\), in ns, for external grant-output capacitance \(L\) in fF. Linear interpolation from the observed 20- and 100-fF differences gives

\[
\widehat D(L)=-0.58 + (L-20)(1.19/80)\quad\mathrm{ns},
\qquad \widehat L_* = 20+80(0.58/1.19) = 58.99\,\mathrm{fF}.
\]

Predictions for **previously unmeasured loads**:

| Holdout load | Predicted difference \(\widehat D\) | Frozen qualitative prediction |
|---:|---:|---|
| 40 fF | -0.2825 ns | pairwise fixed is faster |
| 60 fF | +0.0150 ns | near crossover: absolute difference <= 0.20 ns |
| 80 fF | +0.3125 ns | pairwise fixed is slower |

**Independent prospective test:** rerun the exact same four RTL maps and pinned Liberty, 20-ps input transition, ideal-wire OpenSTA flow, adding 40/60/80-fF loads to the original 2/20/100-fF sweep. Parse and archive all 24 paths. Do not silently drop load points or replace the strongest source-fixed baseline. Report numerical prediction residuals, qualitative sign success, and whether a monotone reversal exists. No inference about actual routed GPU clock or power is allowed.

**Falsification:** if 40-fF difference >=0, 80-fF difference <=0, or the 60-fF absolute difference exceeds 0.20 ns, the frozen qualitative boundary prediction fails. Independently report the interpolation's maximum absolute holdout error; no fitting on the holdouts. The candidate remains an equal-grant implementation optimization even if all predictions pass, not a new GPU scheduling mechanism.

The stronger equal-resource fairness comparator remains rotating/oldest-first. The older V287/V296 directions are historical; the existing V317 branch and draft PR #34 remain unchanged in scope.
