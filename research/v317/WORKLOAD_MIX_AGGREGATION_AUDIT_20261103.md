# V317: Workload-mix aggregation audit (2026-11-03)

## Scope
A new exact-rational falsification of **averaging per-regime speedup ratios** when applying the V317 synthetic two-cycle oracle to workload mixes. No GPU trace, new hardware, or timing measurement is claimed. Previous area/electrical failures remain binding.

## Law
For regimes i with batch fractions w_i, bank counts B_i, mapping fractions q_i, and common fractional clock-period penalty d, define g_i=2+q_i[G(B_i)-2] and e_i=q_i P(B_i). Then the correct aggregate ratio is

R_mix = (sum_i w_i (g_i+e_i))/((1+d) sum_i w_i g_i).

The exact necessary-and-sufficient positive-win condition is sum_i w_i e_i > d sum_i w_i g_i. **Averaging regime-level speedup ratios with batch fractions is generally incorrect** because regimes contribute different baseline completed work. The correct ratio equals a baseline-completion-weighted average of regime-level ratios, not the batch-weighted average.

## Frozen deterministic comparison
The script specifies two equal-batch regimes (B=4 and B=64, q=1) and d=0.005, then compares the incorrect arithmetic average against the exact aggregate; it asserts inequality and verifies the correct weighted identity. Four additional mixed-q cases exercise the sign condition. All parameters are illustrative, not measured workload frequencies or routed delay.

## Decision
The previous single-regime no-win boundary remains valid under its assumptions. A workload-level claim requires measured batch fractions and bank-demand correlations, followed by matched physical timing. Do not use an average of speedups or treat synthetic mixture weights as observed GPU workloads. No scheduler promotion.
