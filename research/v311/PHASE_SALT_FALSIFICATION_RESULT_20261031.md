# V311 result: prospective phase-cohort XOR bank salting fails ideal admission materiality gate

Date: 2026-10-31. Evidence: **analytical + locally executed synthetic holdout**; hosted GitHub Actions is separately required. No RTL, P&R, electrical signoff, or GPU throughput evidence is claimed.

## Frozen experiment and measured holdouts

The [preregistered protocol](PHASE_SALT_PREREG_20261031.md) preceded the executable and outcome examination. The [reproduction script](phase_salt_falsifier.py) uses Python's standard library only; run `python3 research/v311/phase_salt_falsifier.py --json`. Two 16-cohort regimes contain 400,000 independent synthetic opportunities each. Every cohort receives one immutable XOR salt at warp allocation, and each warp reads one operand per opportunity.

| Regime | Predicted candidate/static | Holdout candidate/static | Static admissions | Candidate admissions |
|---|---:|---:|---:|---:|
| 16 rotating hot-bank cohorts (prospective win) | 1.02276129x | **1.02271968x** | 775,099 | 792,709 |
| Stationary hot bank (prospective no-win) | 1.00000000x | **1.00000000x** | 792,697 | 792,697 |

Three adversarial controls rejected a salt change during a live cohort, a non-optimal static comparator, and a non-bijective bank map. The independent probability auditor enumerates all 256 ordered bank pairs per salt. Both frozen predictions passed the 0.01 absolute ratio tolerance.

## Compact exact predictive boundary

For independent operand bank distributions `p` and `q` over 16 banks, a warp-B salt `s` has bank-collision probability

`C(s) = sum_{b=0}^{15} p_b q_{b XOR s}`.

With two simultaneous reads, one port per bank, and no other stalls, expected admissions are `A(s)=2-C(s)`. A phase-cohort oracle chooses `s_t=argmin_s C_t(s)`; the **strong static comparator** chooses `s*=argmin_s sum_t C_t(s)` using the complete phase mixture. The predicted ideal ratio is

`G_ideal = [sum_t (2-C_t(s_t))] / [sum_t (2-C_t(s*))]`.

For the frozen hot probability 0.85 and uniform remaining probability 0.01, aligned hot banks give `C=0.7240`, misaligned give `C=0.0184`. Across all 16 equally frequent hot-bank rotations, any fixed salt aligns exactly once, hence `C_static=0.0625`; the phase-aware candidate avoids all alignments and has `C_candidate=0.0184`. Thus `G_ideal=1.9816/1.9375=1.02276129`.

A broader upper bound for this exact uniform-rotation family follows from `C_candidate >= 0`: `G_ideal <= 2/(2-1/16)=1.03225806`, even with perfect one-hot operands. This is a **model-specific ceiling**, not a bound on four-slot V-Tile scheduling or on real GPU programs.

## Falsification decision

**RETIRE V311 for the frozen two-warp one-read phase-cohort mechanism.** The 2.276% ideal gain is below the prospectively frozen 5% materiality threshold *before* XOR address generation, launch-time salt selection, metadata, power, clock impact, occupancy, or other stalls. Stationary workloads show no gain. An equal-capability per-cohort oracle with the same information produces the identical selection, so there is no incremental algorithmic novelty over that stronger control.

The mechanism is physically constrained to warp-lifetime salts: changing the salt mid-warp would require live-register migration, and is forbidden by the protocol. No claim about RTX 5090 equivalence is supported.

## Scientific consequences and limitations

This result rules out spending place-and-route resources on this **narrow** salt policy/regime, not all bank coloring or all bank-conflict optimizations. Four-slot/two-source/two-port admission, dependent instructions, register liveness, real workloads, bandwidth, and physical datapath costs were not modeled. Prior art in bank-aware allocation, register-file hashing, operand collection and warp scheduling requires an explicit audit before any future novelty claim. The historical V287/V296/V309/V310 negative results remain unchanged.

Next primary mechanism must show an incremental advantage over a reuse-aware, equal-resource comparator in a V-Tile-relevant model *before* promotion to physical RTL. Do not recycle V311 by changing only the baseline.
