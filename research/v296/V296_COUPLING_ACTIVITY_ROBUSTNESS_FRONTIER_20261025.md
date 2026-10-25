# V296: robust activity/coupling-correlation boundary (2026-10-25)

**Evidence tier:** original SHA-256-verified routed SPEF measurements plus an algebraic sensitivity analysis with independent dense-grid validation. **Not measured switching activity, power, physical closure, or a GPU speedup.** Both original integrated contestants remain physically infeasible at 3.5 ns. V296 remains the only provisional mechanism; V287 stays retired.

## New falsifiable result

The previous equal-correlation comparison predicted 12.63–12.80% lower external-capacitive switching coefficients for V296. That is insufficient to guarantee an advantage if candidate/control switching activities or interconnect correlations differ. This experiment derives the exact maximum tolerable correlation mismatch across **all** possible baseline correlations under a bounded activity ratio.

Original SHA-locked routed SPEF measurements from [run 40173311725](https://github.com/sushxnthd/vektor/actions/runs/40173311725), pF, rounded to six decimals:

| Design | Ground capacitance | Unique coupling capacitance |
|---|---:|---:|
| V296 | 21.788331 | 14.878993 |
| Serial one-hot | 24.937753 | 17.074129 |

Let a be the candidate/serial switching-activity ratio, and let delta be the maximum disadvantage in signed interconnect switching correlation, so rho_V296 >= rho_serial - delta, with both correlations in [-1,1]. Under equal voltage and the *aggregate* capacitive model E_ext proportional to alpha*[Cg+2Cc*(1-rho)], the **worst-case ratio** for this measured physical pair is

    max E_V296/E_serial = a*(21.788331 + 2*14.878993*delta)/24.937753.

Therefore a robust advantage exists precisely when

    delta < delta_star(a) = (24.937753/a - 21.788331)/(2*14.878993).

The maximum is attained at rho_serial=+1 and rho_V296=1-delta. Below rho_serial=-1+delta, candidate correlation saturates at -1 and the serial denominator falls monotonically. Above that point, the ratio of two affine functions has positive derivative proportional to Cc_serial*Cg_V296 - Cc_V296*Cg_serial + 2*Cc_serial*Cc_V296*delta; its constant term is positive for the original SPEF measurements. This proves the worst-case endpoint for all delta in [0,2] under the stated model.

## Sensitivity boundary

| Candidate activity upper bound | Largest guaranteed correlation disadvantage |
|---:|---:|
| 1.000x | **0.105835** |
| 1.050x | **0.065929** |
| 1.100x | **0.029651** |
| 1.145x | **No robust guarantee even at equal correlations** |

At a=1.10 and delta=0.02, the worst-case external coefficient ratio is less than one. At delta=0.04, it exceeds one. At delta=0, the robust activity ceiling across all correlations is 1.144546. The correlation-specific break-even values from the earlier report remain valid but are not uniform robustness guarantees.

## Independent checks

The executable [v296_coupling_robustness_envelope.py](https://github.com/sushxnthd/vektor/blob/research/v296-pairwise-bank-conflict/research/v296/v296_coupling_robustness_envelope.py) checks derivative sign, threshold constants, adversarial input rejection and 35 independent 1,001-point correlation sweeps. Its normal mode checks four activity levels on both sides of the threshold using 4,001-point sweeps. **Local self-tests and both-sided sweeps passed.** The tests validate the mathematical boundary, **not** actual switching behavior, per-net correlation, clock energy, internal cell energy or measured power.

## Research decision

The measured aggregate capacitance reduction does **not** guarantee lower dynamic power. Actual switching traces or defensible trace-derived bounds must establish that activity and correlation lie inside the predicted region. The measured high-capacitance tail is worse for V296, and both original integrated designs still fail setup/hold and three capacitance checks. No GPU speedup, feasible integrated clock or RTX-5090 equivalence is established.

The next decisive experiment remains the corrected, in-situ extracted critical-path audit for both contestants, followed only if justified by a separately preregistered matched electrical repair and independently optimized equal-resource serial control. Keep the failed physical gate, original evidence, sealed GPU holdouts and Kernellum PR #119 unchanged.
