# V312 prospective matched-physical kill protocol (2026-10-31)

Status: frozen **before** the first V312 Nangate45/OpenROAD timing result. This extends, not replaces, `REJECTION_FALLBACK_PREREG_20261031.md`.

## One mechanism
Retain only rejection-aware two-choice warp admission. V287/V296/V309/V310/V311 are historical negative controls, not active mechanisms. V312 RTL has four issue slots, sixteen banks, two reads per instruction, two read ports per bank, one primary and one backup candidate per slot.

## Physical comparators
- **Optimized head-only greedy**: the source-preserved V309 compact greedy implementation, not a strawman variable-indexed counter. It is a *weaker policy baseline* because it cannot choose backups.
- **Factored V312**: current RTL with primary/backup inputs. Inputs not used by the baseline are legitimately absent from the mapped baseline, since they incur hardware cost only for V312.
- **Strong buffered two-choice collector**: a required *future* same-information, equal-resource throughput comparator. No novelty or real throughput gain can be claimed from winning against head-only alone.

## Frozen experimental setup
- Nangate45 typical Liberty, same synthesis flags, Yosys/ABC and OpenROAD binaries in one pinned container image; record source hashes.
- Combinational virtual clock 1 ns, identical input transition 50 ps, output load 20 fF, zero input/output delay.
- Place both mapped designs at **30 x 30 um** and **45 x 45 um** die sizes with the corresponding 3/27 and 4.5/40.5 um core margins, density 0.65.
- Use OpenROAD placement-estimated metal3 wire RC. This is **not** detailed routing, extracted parasitics, or electrical signoff.
- Parse *data arrival time*, not required time. Explicitly record max-slew and max-capacitance reports. Fail the audit on errors, missing evidence, nonfinite delays, or electrical violations. Do not reinterpret a tool failure as a physical failure.
- Record mapped cell area and ratio. All data and scripts preserved in workflow artifacts.

## Predicted workloads and precommitted decisions
- **Predicted win**: hotspot synthetic admissions G=1.9500, but clock-limited *upper bound* is G/d and the more realistic Amdahl upper bound is `1/[(1-f)+f/G]/d`. At f=0.5, the ideal admission-limited speedup is 1.3220x before clock and other costs.
- **Predicted no-win**: disjoint banks, G=1.0. Any d>1 is a strict clock-limited regression, not an improvement.
- **Unseen transfer**: G=1.268568; f=0.5 requires d<=1.0167 for a 10% upper-bound tile speedup with zero other overhead. Freeze this stringent boundary rather than relaxing it after timing.
- **Physical rejection**: kill this V312 RTL implementation if mapped area >1.50x compact greedy, if electrical violations occur, or if the f=0.5 transfer upper bound is <=1.0 in either placed corner (equivalently d>=1.1184), before any extra costs. Do not label a prelayout or estimated-RC pass a routed pass.
- **Research novelty rejection**: kill the *architecture novelty* claim if a competent buffered two-choice controller with the same information and resources reproduces V312 admission and sustained throughput.

This physical comparison can only establish whether the extra fallback logic is plausible relative to optimized head-only arbitration. The stronger collector test is still necessary.
