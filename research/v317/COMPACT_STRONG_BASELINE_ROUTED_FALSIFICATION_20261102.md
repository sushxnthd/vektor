# V317: strongest same-policy baseline physical falsification (2026-11-02)

## Source and prospective status
The [frozen three-way protocol](FROZEN_COMPACT_GREEDY_RF_PROXY_CHALLENGE_20261102.md) was committed before the hosted run. The source-pinned [GitHub Actions run #41443576796](https://github.com/sushxnthd/vektor/actions/runs/41443576796) completed successfully, including 4,096-cycle three-way RTL grant/operand/port equivalence, three matched full Nangate45 OpenROAD routes, and the independent extracted-RC audit. The **audit script passing is not electrical signoff**. [351-file raw artifact #13143485214](https://github.com/sushxnthd/vektor/actions/runs/41443576796/artifacts/13143485214) preserves the measurements. The physical source SHA in the audit is `96f4dae55effc33d3e8032cf1245b3384d18d5b2`.

All three variants used the same flop-mapped 16-bank, two-read-port RF proxy, 1,213 sequential cells, 0 SRAM macros, 3.0-ns target, 240x240-um die, placement density add-on 0.35, and equal mapping and output loads.

## Physical evidence (extracted RC; no electrical signoff)

| Metric | Historical serial source | Active pairwise V317 | Strong compact greedy |
|---|---:|---:|---:|
| Routed standard-cell area (um²) | 21,535.6 | 21,324.7 | **21,314.6** |
| Setup slack (ps) | +453.458 | +751.340 | +805.813 |
| Hold slack (ps) | -1.7813 | +3.9520 | -0.8122 |
| Hold violations | 10 | 0 | 6 |
| Max-cap violations | 15 | 21 | 14 |
| Routed DRC violations | 0 | 0 | 0 |
| Reported controller Fmax (MHz) | 392.689 | 444.709 | 455.750 |
| Routed wire (um) | 270,784 | 269,563 | **246,157** |
| Default-activity power proxy (mW) | 10.5201 | **10.3280** | 10.4516 |

The preregistered **raw no-win prediction PASSES**: pairwise area saving against compact is **-0.047385%**; compact is 10.1 um² *smaller*. The **legal material-win gate FAILS**: neither compact nor pairwise is electrically legal (21 and 14 max-cap violations, respectively), and pairwise does not reach the frozen >=2.0% area-saving threshold. Pairwise's positive hold slack does not cure its capacitance violations. Compact's area and wire advantage do not make it legal either. A route exit code of zero or zero DRC is not electrical signoff.

Compared with compact, pairwise uses 9.51% more routed wire (269,563 vs 246,157 um), has a 1.183% lower **default-activity power proxy**, and has a 2.42% lower reported isolated Fmax. These are *not* calibrated GPU power, tile-clock or performance results. The 4,096-cycle equivalence test establishes identical intrinsic issue service at fixed clock and ports: **1.000000x**.

## New exact area-dominance boundary

Let `C=21,314.6` be the compact whole-proxy area, `P=21,324.7` the pairwise area, `H>=0` any **identical** additional tile hardware area, and `B>=0` the area budget. Because `P>C`, for every possible `B,H`:

`floor(B/(P+H)) <= floor(B/(C+H))`.

Thus **no additional pairwise tile is possible under an equal-clock, equal-service, equal-occupancy, equal-common-hardware area-reinvestment model**. This is stronger than merely failing the frozen 2% threshold, but is conditional on equal hardware and service; it is not a general theorem about different physical tile architectures.

To achieve the *original* frozen 2% pairwise area advantage while holding compact fixed, pairwise would need area <= `0.98*C=20,888.308 um²`: **436.392 um² less** than its observed route. Holding pairwise fixed instead, compact would need area >= `P/0.98=21,759.898 um²`, **445.298 um² more** than observed. These are sensitivity boundaries, **not permissible post-hoc target changes**.

The result is reproduced by `rtl/strong_baseline_dominance.py` using the pinned `STRONG_BASELINE_THREE_WAY_AUDIT_20261102.json` summary, with negative mutation and discrete budget enumeration controls. That arithmetic script is **not** a substitute for the existing independent raw OpenROAD artifact checker.

## Research disposition

**FALSIFY V317's claimed material whole-RF-proxy area advantage against the strongest available same-policy RTL control.** The old serial-source comparison was implementation-quality confounded. Preserve the narrow historical controller-only optimization and every negative result, but do not revive V317 as a positive tile-throughput mechanism by relaxing the 2% criterion or selectively repairing only one challenger. No more density-only repeats of unchanged V317.

The next genuinely different candidate must be preregistered with a non-identical service/resource mechanism and matched legal physical baselines, before any new GPU throughput claim. This experiment contains **no SRAM macro, no datapath-complete tile, no multi-corner signoff, no measured GPU IPC, and no RTX 5090 equivalence**. The world-class completion gate remains unmet.
