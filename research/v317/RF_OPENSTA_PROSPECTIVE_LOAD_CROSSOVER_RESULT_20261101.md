# V317 prospective cell-delay crossover transfer (2026-11-01)

## Frozen provenance and source-pinned run

The [holdout protocol](FROZEN_RF_OPENSTA_LOAD_CROSSOVER_HOLDOUT_20261101.md) was committed first at `7e220cb`, before 40/60/80-fF STA evaluation. The original 2/20/100-fF training points were already measured in run #41304535696 and were never represented as unopened holdouts.

[Hosted prospective workflow #41304674526](https://github.com/sushxnthd/vektor/actions/runs/41304674526) **PASSED** on source SHA `37df7ef4cc9fdc1227cd4805c4b590ffd4867d41`: four matched Nangate45 mapped RTL implementations, six external capacitances, 24 actual OpenSTA 2.0.17 timed grant-output paths, five independent parser regression tests, source-pinned raw netlists and logs. This is pre-route characterized-cell timing with **ideal wires**.

## Unseen fixed-priority holdouts

\(D(L) = t_{pairwise\ fixed}(L)-t_{source\ fixed}(L)\), ns. Negative favors pairwise.

| Unseen load | Frozen predicted D | Observed D | Residual | Frozen prediction |
|---:|---:|---:|---:|---|
| 40 fF | -0.2825 ns | **-0.38 ns** | -0.0975 ns | faster: **PASS** |
| 60 fF | +0.0150 ns | **-0.12 ns** | -0.1350 ns | within 0.20 ns: **PASS** |
| 80 fF | +0.3125 ns | **+0.21 ns** | -0.1025 ns | slower: **PASS** |

All three frozen qualitative predictions survived; maximum absolute quantitative interpolation error was **0.135 ns**. The previously predicted crossover of 58.992 fF was **not quantitatively accurate**: the new 60/80-fF measurements imply a **post-hoc linear crossing around 67.3 fF**, which must not be advertised as a prospectively verified exact boundary.

### All six load points (ns)

| Load fF | Source fixed | Pairwise fixed | Source rotating | Pairwise rotating |
|---:|---:|---:|---:|---:|
| 2 | 1.19 | 0.52 | 2.60 | 1.33 |
| 20 | 1.28 | 0.70 | 2.67 | 1.39 |
| 40 | 1.38 | 1.00 | 2.77 | 1.49 |
| 60 | 1.48 | 1.36 | 2.87 | 1.59 |
| 80 | 1.58 | 1.79 | 2.97 | 1.69 |
| 100 | 1.68 | 2.29 | 3.08 | 1.79 |

**Interpretation:** generic/mapped cell-area reduction alone is insufficient to certify lower physical latency; a high external load can reverse the grant-equivalent fixed-priority timing ranking. The rotating pairwise version remains faster than source rotating at all six loads but still has more area than equally optimized fixed and no established incremental GPU service advantage. This is a predictive **implementation load boundary**, not the required GPU throughput/occupancy/port-pressure law.

## Open physicality gates

Next: independently audit max-capacitance, max-slew and fanout violations under the same loads; output drivers may be electrically illegal at high loads and require buffers/resizing. Then placement and extracted wire RC, actual integrated tile timing, power and real workload measurements. No clock-frequency signoff, routed RC, power, GPU IPC or RTX 5090 equivalence is claimed. The existing V317 branch and draft PR #34 remain the only active research container; V287/V296 are historical and Kernellum PR #119 remains untouched.
