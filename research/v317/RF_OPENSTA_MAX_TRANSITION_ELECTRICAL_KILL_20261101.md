# V317 electrical falsification: the high-load crossover is outside legal slew (2026-11-01)

## Source-pinned gate and retained failures

[Frozen electrical protocol](FROZEN_RF_OPENSTA_ELECTRICAL_LIMITS_20261101.md) committed at `31aad758` before the electrical checks. This is a **post-timing diagnostic** of previously observed six-load data, not a new timing holdout. The initial OpenSTA 2.0.17 electrical attempts #41304839929 and #41304932450 failed because that legacy tool does not support modern `report_check_types -max_capacitance` or `-max_slew` flags. The supported no-flag `report_check_types` was used instead, and its built-in **max_transition** table was independently parsed and checked.

[Final source-pinned workflow #41305144815](https://github.com/sushxnthd/vektor/actions/runs/41305144815) **PASSED** at commit `409f311247ed72b1070a7f6d0e79cd7886c8c2b8`. The run regenerated four matched Nangate45 mapped netlists, analyzed 24 grant-output paths at six loads, produced 24 max-transition reports, passed eight independent Python tests and archived raw evidence at [artifact #13082768085](https://github.com/sushxnthd/vektor/actions/runs/41305144815/artifacts/13082768085).

## Worst max-transition status (Nangate45 typical limit approximately 0.20 ns)

| External load | Source fixed | Pairwise fixed | Source rotating | Pairwise rotating |
|---:|---|---|---|---|
| 2 fF | **MET** (0.16 ns) | **MET** (0.10 ns) | VIOLATED (0.76 ns) | VIOLATED (0.40 ns) |
| 20 fF | **MET** (0.17 ns) | **MET** (0.18 ns) | VIOLATED (0.76 ns) | VIOLATED (0.40 ns) |
| 40 fF | VIOLATED (0.31 ns) | VIOLATED (0.33 ns) | VIOLATED (0.76 ns) | VIOLATED (0.40 ns) |
| 60 fF | VIOLATED (0.45 ns) | VIOLATED (0.47 ns) | VIOLATED (0.76 ns) | VIOLATED (0.40 ns) |
| 80 fF | VIOLATED (0.59 ns) | VIOLATED (0.61 ns) | VIOLATED (0.76 ns) | VIOLATED (0.41 ns) |
| 100 fF | VIOLATED (0.74 ns) | VIOLATED (0.75 ns) | VIOLATED (0.76 ns) | VIOLATED (0.51 ns) |

These are **worst reported cell-pin max-transition checks**, not necessarily the external grant-output pin; the rotating control's worst offender can be an internal net. Values are rounded by the legacy OpenSTA report.

## Decisive correction

**The previously observed 100-fF fixed-priority delay ranking reversal is NOT an electrically legal physical timing comparison.** Both fixed-priority implementations violate characterized max-transition constraints at 40 fF and above. The prospective 40/60/80-fF interpolation predictions remain mathematically valid for the raw **unrepaired netlists**, but their physically actionable scope is withdrawn. The 2-fF and 20-fF fixed-priority pairwise timing/area improvements survive the checked max-transition gate, but not max-capacitance, routed RC, actual tile timing or power.

The rotating implementations violate max-transition even at 2 fF; their pre-route delay comparisons cannot be treated as electrically admissible until those paths are repaired with buffers, resizing or remapping under equal resources. An actual legal optimization must rerun mapping, equivalence, area, timing and workload checks after the repairs. OpenSTA 2.0.17 could not provide a max-capacitance report, so **max-capacitance remains UNVERIFIED**; do not infer it passes.

## Research decision

Keep pairwise fixed as a lower-area **grant-identical implementation optimization** with a narrowly bounded low-load cell-timing advantage, not a GPU architecture breakthrough. **Kill unconditional timing dominance and the electrically invalid high-load crossover as physical claims.** Same-clock intrinsic scheduling gain remains exactly 1.0x. Strong fairness-aware baseline, wire/placement, full electrical signoff, integrated GPU workload and tile-level consequences remain open. No RTX 5090 equivalence claim. Kernellum PR #119 untouched.
