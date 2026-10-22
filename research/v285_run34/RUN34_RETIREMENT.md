# V285 retirement: matched Nangate45 synthesis (2026-10-22)

## Decision
RETIRED. Neither original full pressure-priority RTL nor the one allowed one-pick repair meets the predeclared equal-budget area gate (onepick <= 1.05 x fixed). Do not integrate into V-Tile. This is a mapped-area falsification of these implementations, **not** a complete post-layout timing/power result.

## Equal-resource setup
4 simultaneous two-source requests, 16 banks, 2 reads per bank per cycle, 4-bit bank IDs, no additional ports/queues/storage. Same 36 input bits and 4 grant outputs. Nangate45 typical liberty, Yosys 0.33, ABC mapping. Independent 10,000-case RTL oracles passed for both designs.

| Implementation | Nangate45 mapped area | Cells | Relative area |
|---|---:|---:|---:|
| Fixed priority (simpler control) | 793.212 | 740 | 1.000 |
| Full pressure-priority V285 | 1950.844 | 1690 | 2.459 |
| One-pick repair | 1681.918 | 1493 | 2.120 |

Mapped cell area is library-unit area, not full placed tile area. Longest combinational topological path in mapped full pressure control: 69 cells versus 19 in fixed. This is not STA or an electrical slew/capacitance measurement.

## Frozen one-pick unseen model check (E0, no throughput claim)
- Two-bank: 19267/17150 grants, 1.12344x vs fixed, prediction passed.
- Hot bank: 28128/27622, 1.01832x, prediction passed.
- Independent: 38237/38236, 1.000026x, prediction passed.
- No conflict: 40000/40000, 1.000x, prediction passed.

Those figures are independent one-cycle grant counts. They do not model queueing, starvation, dependency, RF access energy or actual GPU throughput.

## Physicality gate
Functional model PASS; RTL simulation PASS; characterized generic cell mapping PASS; electrical max-cap/slew NOT RUN; STA NOT RUN (OpenSTA/OpenROAD unavailable in public runner); matched area FAIL; dynamic power and wire/load sensitivity NOT RUN. The full and repaired implementations fail the area gate before claims can advance.

## Evidence links
- Full physical workflow: https://github.com/sushxnthd/vektor/actions/runs/39802191054 (raw logs/artifact).
- One-pick repair: https://github.com/sushxnthd/vektor/actions/runs/39802670733 (raw logs/artifact).
- Original FP32 V153/V156 cutset remains electrically disqualified. No change to integrated tile.
- Prior art: https://doi.org/10.1007/s10766-012-0201-1 ; https://arxiv.org/abs/2010.09330

## Architecture consequence
Do not replace the V-Tile's fixed-priority RF arbiter with V285. A new kernel must seek a positive mechanism with much lower control overhead and verify both workload boundary and physical mapping.
