# Vektor-055 results — 2026-10-09

## Source inspection (static PTX virtual-register identities; not physical RF)
Pinned public 14-kernel hand-written BPF PTX: 272 eligible arithmetic/logic instructions, 564 explicit register-source uses, 10 repeated uses (1.773%), 20 three-source instructions, 0 three-source repeats. Compiler-produced vector-add PTX: 6 instructions, 13 uses, 0 repeats, 1 three-source instruction. Combined 10/577 = **1.733%** potential read reduction within the narrow eligible subset. All 10 repeats are `mul x,x` in the BPF PTX. No general GPU workload frequency is inferred.

## SOFTWARE-SIMULATED (two-slot masked collector, one request port)
40 x 1,500-cycle software-reference traces passed independent external-protocol checks, 60,000 cycles total.

| Workload proxy | Baseline completions | Dedup completions | Difference |
|---|---:|---:|---:|
| Zero alias | 803 | 803 | 0% |
| PTX-static-uniform | 856 | 865 | +1.05% |
| Synthetic 25% alias | 737 | 811 | +10.04% |
| Synthetic 50% alias | 737 | 878 | +19.13% |
| Mask correctness stress | 1,025 | 1,124 | +9.66% |

Exploratory 64-seed PTX-static-uniform holdout, 3,000 cycles/seed/policy: baseline 27,464 completions; dedup 27,657 (**+0.703%**), 40 wins, 19 regressions, 5 ties. Paired-seed bootstrap 95% interval +0.371% to +1.044% (10,000 resamples, fixed seed). Reads 57,229 -> 56,619 (−1.066%). This is a synthetic-seed interval, **not** application-general confidence.

**Falsification:** The Vektor-054 +5.77% improvement at deliberately injected 25% alias is not a justified typical application speedup for the audited source mix. The source count and realistic instruction mix must be treated as workload-dependent.

## RTL and synthesis
**Pending GitHub Actions evidence.** Software checks do not establish RTL correctness. No new silicon, clock, power, physical area, chip-level performance, or RTX 5090-class equivalence is claimed.
