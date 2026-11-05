# V317 physical no-go decision — 2026-11-05 UTC

## Evidence tier and decision

**Decision: KILL the positive V317 pairwise-versus-compact-greedy area / tile-density claim.** This decision applies to the existing routed implementation and frozen >=2% materiality criterion, not to all possible future arbitration architectures. Do not label this mechanism physically validated, and do not substitute more analytical scheduling checks for physical repair.

Source: preregistered three-way routed experiment, GitHub Actions run 41443576796; original frozen report in `research/v317/COMPACT_STRONG_BASELINE_ROUTED_FALSIFICATION_20261102.md`.

| Measurement | Compact greedy (strong control) | Pairwise V317 |
|---|---:|---:|
| Routed area, um^2 | 21,314.6 | 21,324.7 |
| Hold violations | 6 | 0 |
| Max-cap violations | 14 | 21 |
| Total reported hold/max-cap violations | 20 | 21 |

The candidate is 10.1 um^2 larger, not smaller. Its area saving is (21314.6 - 21324.7)/21314.6 = **-0.047385%**. The two implementations both fail electrical legality. No electrically legal matched timing, energy, or real-kernel throughput advantage has been established.

## Falsification logic

1. The frozen area materiality gate requires >=2% candidate saving versus the competent matched baseline; the observed saving is negative.
2. The electrical gate requires zero reported violations; neither route qualifies.
3. Under equal added tile hardware H >= 0 and equal resource budget B >= 0, pairwise area P > compact area C implies floor(B/(P+H)) <= floor(B/(C+H)). Therefore the candidate cannot support a positive *tile-count* claim from these measured areas.
4. The tile-count proof does not establish a throughput ordering if cycle count, operating frequency, occupancy, traffic, or energy differ. Those quantities require measured workload evidence, not speculation.
5. The candidate's lower reported frequency and greater wire length further weaken its case, but neither is used to claim a calibrated energy result.

## Required restart condition

Do not reopen V317 as a positive mechanism based on mathematical checkers or synthetic fixtures. A new *predeclared* physical experiment would require: repaired electrically legal RTL for both alternatives, identical PDK/library and floorplan constraints, independent report provenance, matched area and routed timing, actual useful-work throughput and traffic, and an unseen workload holdout. Compare against compact greedy, not only the weaker serial greedy. Freeze a predicted win and no-win regime before observing outcomes. If physical constraints erase any gain, retain the no-go.

**Scope:** This file records a falsification; it is not a new synthesis run, not electrical signoff, and not a GPU/RTX 5090 equivalence claim. V287 is historical. V296 physical validation must not be displaced by attempts to rehabilitate this rejected V317 interpretation.
