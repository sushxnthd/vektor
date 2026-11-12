# V312 synthetic two-choice admission result (2026-10-31)

## Evidence status
Local Python stdlib run completed against the prospectively frozen protocol in `REJECTION_FALLBACK_PREREG_20261031.md`. Source-controlled hosted workflow and independent audit were subsequently committed. **Do not promote to independently verified until the hosted workflow passes.** This is a synthetic per-opportunity admission screen, not GPU throughput, RTL timing, area, electrical signoff, or architecture novelty.

## Observed versus pre-outcome finite-state prediction
All regimes use 16 banks, two read ports/bank, four slots, two operands per instruction and up to one ready backup per slot. Exactly 100,000 seeded opportunities per regime. The finite-state law enumerates all head/backup availability configurations and computes E[admissions] under each policy before sampling holdouts.

| Frozen regime | Baseline predicted/observed | Fallback predicted/observed | Exact two-choice oracle predicted/observed | Candidate/baseline observed |
|---|---:|---:|---:|---:|
| Hotspot win | 2.000000 / 2.000000 | 3.900000 / 3.899450 | 3.9995125 / 3.999520 | **1.949725x** |
| Disjoint no-win | 4 / 4 | 4 / 4 | 4 / 4 | **1.000000x** |
| Perturbed transfer | 2.9453125 / 2.948920 | 3.736328125 / 3.737350 | 3.976104736 / 3.975550 | **1.267362x** |

On the hotspot, the candidate captures **97.50%** of the exact same-information, equal-port oracle's admitted instructions. On perturbed transfer it captures **94.01%**. The oracle is not a timing-matched hardware comparator.

## Predictive boundary
For a fixed-prefix final slot, let r=P(primary rejected), a=P(backup ready | rejected), c=P(backup compatible | rejected and ready). Then
`G=1 + r*a*c/(1-r)`, when r<1. A controlled test with (r,a,c)=(0.35,0.75,0.8) predicted 1.323076923x and sampled 1.325273336x (100,000 trials). This **single-slot** formula does not automatically apply to the four-slot scheduler because early substitutions change later port occupancy.

The **full four-slot** exact synthetic prediction is the ratio of finite-state expected admissions, `G = (sum_s P(s) A_fallback(s)) / (sum_s P(s) A_head(s))`. It is predictive given a specified distribution over primary-bank pairs, backup-bank pairs and readiness. It is not yet a compact empirically calibrated law for real workloads, and it omits occupancy stalls, memory bandwidth, control overhead and clock frequency.

## Kill and limitations
- The frozen >1.50x hotspot gain and >=0.90 oracle-fraction gates pass locally. The frozen no-win equals exactly 1.0x.
- **Do not claim incremental novelty:** bank-aware candidate selection and operand-collector approaches are established; the strong two-choice oracle leaves only an implementation/physical Pareto opportunity.
- The present baseline is the existing head-only issue path; a competent *hardware-realizable, timing-matched* two-choice alternative is required. An equal-capability controller may erase any claimed incremental advantage.
- The present test is IID opportunity-level; temporal warp readiness, scoreboard, fairness, power, load, timing, port multiplexing, full register IDs, forwarding and area are not modeled.
- The next step is synthesizable four-slot fallback RTL with an independent oracle and equal-resource standard-cell/placement comparison, followed by real trace-driven scheduling. Kill if clock retention, area, or port/bandwidth constraints erase the admission gain.
- Historical retired mechanisms V287/V296/V309/V310/V311 remain untouched.
