# V317 frozen tile-consequence falsification protocol (2026-11-01)

## Question and evidence boundary
The fixed-priority pairwise bank-credit implementation is grant-equivalent to the original. The 24-fF matched BUF_X1 pre-route result is source 785.498 um^2 / 1.26 ns and pairwise 260.414 um^2 / 0.59 ns. These are **isolated standard-cell numbers**, not tile silicon or routed delays. Can the savings imply *any* tile-level throughput consequence without silently assuming a clock-critical arbiter, replication, or unconstrained bandwidth?

## Locked predictive law
For design j, use N_j = floor(A_budget / (A_other + A_arb,j)), T_j = max(T_other, D_arb,j + delta_wire,j), C_j = N_j * r / T_j, and R_j = min(lambda, B, C_j), where lambda is offered work per ns, B is the system-wide traffic/port ceiling (work/ns), and r is effective work per tile cycle (identical because grants and ports are identical). Gain G=R_pairwise/R_source. A_j is the matched mapped *arbiter* area only; A_other is hypothetical all-other tile area. Wire penalties and all tile assumptions are explicit inputs. No actual GPU throughput is claimed. If R_source=0, report indeterminate rather than divide by zero. For equal N, equal clock and shared r, gain is identically 1.0.

## Frozen regimes (compute only after this protocol commit)
Use the *within-run* BUF_X1 24-fF values above, A_other=40,000 um^2, r=1 work/tile-cycle, delta_wire,source=delta_wire,pair=0, T_other=1.50 ns.
1. **No-win:** A_budget=1,000,000 um^2, lambda=B=100 work/ns. Prediction: no additional tile and G=1.0000.
2. **Discrete area-step predicted win (conditional):** A_budget=1,010,000 um^2, lambda=B=100 work/ns. Prediction: pairwise admits exactly one more hypothetical tile than source, G>1.04.
3. **Bandwidth-kill control:** same as (2), B=16 work/ns, lambda=100. Prediction: G=1.0000 despite extra tile.
4. **Critical-path-only conditional:** same as (1), T_other=0.80 ns, lambda=B=100. Prediction: G>1.50 due solely to hypothetical clock bottleneck.
5. **Differential wire-kill:** same as (4), delta_wire,pair=0.70 ns and delta_wire,source=0. Prediction: G<=1.0 (0.70 ns is larger than observed isolated 0.67 ns delay margin).

## Validation and independent controls
Implement a dependency-free Python exact calculator, an independent integer-count tile enumerator, and a deterministic finite-horizon workload executor. Check the five frozen regimes and at least 50 independently generated, unseen parameter combinations. Test monotonicity of the area-budget and bandwidth caps where mathematically applicable. Any mismatch or counterexample is retained, not tuned away. No use of simulated timing as a substitute for routed RC. Report discrete area steps, critical-path dependence, and workload/traffic ceiling explicitly.

## Kill criteria
If any claim of GPU speedup requires unverified critical-path or tile replication assumptions, reject it as a measured result. If equal-tile-count, noncritical arbiter, and identical grants/ports hold, throughput benefit is exactly zero. Do not infer RTX-5090 parity. Keep the same V317 branch/draft PR #34 and leave Kernellum PR #119 unchanged.