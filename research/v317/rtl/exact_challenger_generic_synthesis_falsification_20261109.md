# V317 exact challenger: matched generic-synthesis falsification (2026-11-08 UTC)

## Frozen evidence provenance

- GitHub Actions run 42530571288, job 128883642048, source commit `0cd941e43cb9ad19b77fbf0cb636998393a6555d` (run log and artifact `v317-rf-exact-matched-rtl`).
- Yosys 0.52 generic logic synthesis, not Nangate45 mapped area, routed delay, electrical signoff, or workload throughput.
- Fixed-priority source arbiter: 1,321 generic cells, zero FF, maximum generic net sink fanout 49.
- Exact challenger: 6,339 generic cells, zero FF, maximum generic net sink fanout 32.
- Ratio: 6,339 / 1,321 = 4.7986373959; excess 5,018 cells, +379.86% relative to source.

## Decision / falsification

The exact challenger is **not** an equal-area alternative at the measured generic-netlist tier. Do not use it to claim a throughput win at equal hardware resources. A fair comparison requires area normalization (including the strongest compact pairwise/rotating alternatives), identical offered demand, operand storage and port inventories, and mapped/routed clock constraints. Lower fanout in the challenger does not erase the generic-cell penalty and is not evidence of electrical closure.

The separate pairwise comparison in run 42530571290, job 128883642007, reports fixed-priority pairwise 272 cells / 22 generic levels versus source fixed 1,321 cells / 49 levels; rotating pairwise 558 cells / 31 levels versus source rotating 1,614 cells / 58 levels. These are *generic synthesis* advantages only; they do not establish a GPU performance win or complete matched-resource physicality. The strongest compact control must be included as a baseline in any future positive claim.

## Necessary physical and workload experiment

1. Run the existing registered source and pairwise wrappers through the same mapped and routed flow, report area, worst-path slack, setup/hold, max transition/capacitance/fanout, clock constraints and wire/load sensitivity. Include failed attempts.
2. Add/verify actual operand-storage and RF service hardware at identical port, bank and retained-word budgets. A combinational arbiter with 0 FF is not a complete tile or storage implementation.
3. Replay one frozen immutable arrival manifest for baseline and candidate; record completions, unfinished requests, measured periods, offered load, occupancy, bank/return saturation and control costs. Include strongest equal-resource baseline.
4. Evaluate the previously frozen predicted-win and predicted-no-win regimes without tuning on holdouts. Kill the candidate if routed clock/area/port costs erase benefit.

**Evidence tier:** executed hosted generic synthesis and negative equal-resource feasibility finding. **Not:** mapped PPA, electrical signoff, measured workload IPC, or RTX 5090 equivalence.

Source links: https://github.com/sushxnthd/vektor/actions/runs/42530571288 and https://github.com/sushxnthd/vektor/actions/runs/42530571290 .
