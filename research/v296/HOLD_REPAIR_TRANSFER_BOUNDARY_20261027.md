# V296: prospective hold-repair transfer and area boundary (2026-10-27)

**Evidence tier: conditional sensitivity analysis, not routed evidence.** This analysis is frozen while the symmetric +25 ps OpenROAD hold-target trial [#40494515995](https://github.com/sushxnthd/vektor/actions/runs/40494515995) is running. It does not change its RTL, Tcl, thresholds, or original holdouts. The original fixed-word implementation remains **rejected**; V296 pairwise bank admission remains the sole provisional mechanism, and V287 is retired.

## Original extracted-RC anchors (unchanged)
From the independently SHA-verified [matched full-route audit](https://github.com/sushxnthd/vektor/blob/research/v296-pairwise-bank-conflict/research/v296/FIXED_WORD_MATCHED_EXTRACTED_BOUNDARY_20261027.md): candidate setup +74.236 ps, hold -12.622 ps, area 13,379.001906 um^2; strongest fifth-stage serial setup -751.540 ps, hold -9.430 ps, area 15,779.651363 um^2. The frozen setup requirement is >=+50 ps. **Both are infeasible.**

## Prospective predictive boundary, not an assumed physical repair
Let x be an **effective added minimum-path delay**, eta in [0,1] the fraction actually transferred into the worst hold slack, kappa >=0 the setup-slack cost per unit x, u_h >=0 the adverse hold drift, and u_s >=0 the adverse setup drift (all in ps). The conditional model is

H_new = -12.622 + eta*x - u_h
S_new = 74.236 - kappa*x - u_s.

Candidate timing feasibility requires

x >= (12.622+u_h)/eta, and
x <= (24.236-u_s)/kappa,

with the usual zero-coefficient limiting cases. Thus the feasible transfer region obeys
**kappa/eta <= (24.236-u_s)/(12.622+u_h)**.
At zero drift, the ratio must be <=**1.920139**; with 10 ps setup drift it tightens to **1.127872**. This is a necessary local-model boundary, not a sufficient physical signoff law. The actual hold25 Tcl uses a **25 ps repair slack-margin target**, which is not the same thing as x. Never substitute one for the other.

| Frozen hypothetical regime | x (ps) | eta | kappa | u_h / u_s (ps) | Predicted hold (ps) | Predicted setup (ps) | Candidate timing |
|---|---:|---:|---:|---:|---:|---:|---|
| Local input-path insertion, predicted win | 25 | 1.00 | 0.25 | 0 / 2 | +12.378 | +65.986 | Conditional pass |
| Shared critical-path penalty, predicted no-win | 25 | 1.00 | 1.20 | 0 / 0 | +12.378 | +44.236 | Fail setup |
| Low hold transfer, predicted no-win | 25 | 0.45 | 0.25 | 0 / 0 | -1.372 | +67.986 | Fail hold |
| Route headwind, predicted no-win | 25 | 0.75 | 0.80 | 3 / 6 | +3.128 | +48.236 | Fail setup |

These are **prospectively specified sensitivity cases**, not measured workload or timing results. The real hosted run must be audited independently and compared to these regimes without fitting eta or kappa after seeing the outcome. A single routed trial cannot identify both coefficients or validate this model on unseen wires/loads.

## Equal-resource and tile consequences
The strongest serial implementation currently needs **801.540 ps of setup improvement** just to meet the same +50 ps guard and 9.430 ps of hold recovery. Even if the candidate closes, a **matched feasible Pareto win is not established unless both controls pass**, as required by the preregistration. Do not compare against a serial implementation that remains physically infeasible.

The *hypothetical* 18-candidate-versus-16-serial packing condition is 18*(13,379.001906+deltaA) <= 16*15,779.651363, so candidate-only area overhead must not exceed **647.354861 um^2 per slice**. This ignores integrated tile interconnect, RF depth, wires and SRAM. No GPU speedup, power benefit, or RTX-5090 equivalence follows.

## Independent reproduction and decision
Run `node research/v296/hold_repair_transfer_boundary.js` to execute integer-unit self-tests and emit machine-readable conditional results. The checker rejects out-of-domain parameters and verifies positive and negative scenarios. Its boundary is fixed before inspection of routed hold25 artifacts.

When [#40494515995](https://github.com/sushxnthd/vektor/actions/runs/40494515995) completes, first verify source hashes and original artifacts, then compare extracted setup, hold, cap, slew, DRC, area and both contestants to the frozen gates. A physical failure retires this hold25 repair without relaxing thresholds. Prospective workload holdouts remain sealed. Kernellum PR #119 remains untouched.
