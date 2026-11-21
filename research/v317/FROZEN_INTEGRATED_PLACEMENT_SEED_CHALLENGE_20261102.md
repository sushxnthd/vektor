# V317 prospective placement-seed legal-source challenge (frozen 2026-11-02)

## Hypothesis and reason for this test
The source 32-wave integrated controller missed the 2.000 ns setup target by only 13.550 ps under the area-oriented mapped route, while the pairwise bank-credit implementation passed by 65.469 ps. The subsequent ABC speed-mapping control was a decisive failure for both variants, including source hold and max-cap violations. Neither experiment excludes a legal *source* solution from a different placement initialization. This experiment challenges the uniqueness of the timing-enabling claim without changing the mechanism or RTL.

## Freeze before evaluating outcomes
- Immutable reference run: [area-oriented integrated route 41352990340](https://github.com/sushxnthd/vektor/actions/runs/41352990340), source SHA `20c5165651d0a941d3c60f918e4255961b8a2a90`. Area-oriented source: 7386.29 um2, period 2.013551 ns, setup -13.550 ps; pairwise: 6599.46 um2, period 1.934532 ns, setup +65.469 ps. Both have 0 DRC/antenna/cap/slew/fanout/hold violations.
- Failed speed-mapped control: [run 41354169431](https://github.com/sushxnthd/vektor/actions/runs/41354169431); do not reclassify its illegal source as a feasible control.
- New **held-out placement seeds**: 7, 19, 37, frozen in this file. Run both original and pairwise at each seed. The earlier unseeded default remains an opened pilot, not a held-out result.
- Identical RTL, 356 sequential cells, 2.0 ns SDC, 10 fF output loads, Nangate45 typical, 120x120 um die, 112x112 um core, ORFS container digest `sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8`, ABC_AREA=1, GPL_TIMING_DRIVEN=1. Only `GPL_RANDOM_SEED` changes between seed pairs. No RF SRAM, no datapath.
- Each route must independently complete and pass final DRC, antenna, setup, hold, max capacitance, max slew and max fanout at the 2.000 ns constraint to enter the **legal** Pareto comparison. A successful `make` or zero DRC alone is insufficient.
- All six attempts, failed cases, tool versions, source SHA, logs, reports and extracted RC are preserved, without deleting non-winning seeds. Compare best legal source against best legal pairwise *across all seeds*, not only matched-seed cherry-picks. Also show all three paired-seed differences.

## Prospective falsifiable predictions
P1: At least two of three pairwise held-out seeds will remain legal at 2 ns. Failure falsifies placement robustness.
P2: Pairwise will have lower routed standard-cell area than source in each completed matched-seed pair. Failure falsifies area robustness.
P3: At least one held-out source seed may close the 13.550-ps setup deficit; **this is an adversarial possibility, not a guaranteed positive prediction**. Record source legality rather than interpreting failure as proof of global optimality.
P4: No seed can establish intrinsic same-clock IPC gain because grants and RF port counts are identical. If a source seed becomes legal at the same clock, retract any claim that pairwise is uniquely necessary to meet 2 ns.

## Hard decision
If a legal source has equal or better area, power proxy and timing under the same physical constraints, retire the pairwise implementation advantage. If source closes timing but remains larger, retain only a measured control-area/power benefit, not an architectural throughput claim. If source does not close, the result is limited to these three seeds and this corner. A GPU-level claim still requires actual SRAM, RF ports, critical paths, bandwidth, activity-derived power and PVT/RC transfer. No RTX 5090 equivalence is implied.

## Positive boundary and independent checks
At fixed same-clock resources, `G_intrinsic(p, overlap, port_pressure, occupancy, overhead) = 1` for any input trace satisfying the common grant contract. Tile-level `G = min(L,C,N_p*r/T_p) / min(L,C,N_s*r/T_s)`, with `N_x=floor(B/(A_other+A_issue,x))`, remains conditional on a real tile clock, area and bandwidth. Use the previously committed independent route-audit approach on all six raw reports; no success claim before audit.
