# V296 deep-bank extracted critical-path locality: decisive negative result (2026-10-28)

**Decision:** the prospectively frozen primary-input-to-register topology hypothesis is **FALSIFIED** for both completed designs. The actual extracted worst setup paths run from scheduler round-robin state registers to staged register-file operand-data registers. The full routed extracted 3.5 ns physical gate still fails. V296 remains provisional, not a feasible GPU mechanism.

## Original SHA-verified evidence

- Source: [full-route experiment #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436). Original completed D8 pairwise ZIP artifact 12769775926, SHA-256 92a84c3923eb62cd506241bcb1d8da06cfcfbd6a13328c8e050b14f301086f4b; completed D4 optimized serial ZIP artifact 12769708334, SHA-256 edeb136bc054eddf7434119115df198e7d4403c9bd01c0a726df7fb30519755b.
- New independent [read-only extracted OpenSTA replay #40597982594](https://github.com/sushxnthd/vektor/actions/runs/40597982594) **passed both jobs**. D8 replay artifact 12776073774, ZIP SHA-256 9ec4107e2d7c3ea1362f0c304280dcc771a738a60e6a5d67fae2118d2ccafbda; D4 replay artifact 12776328412, ZIP SHA-256 1ae842da60de4d7a38507188b3e7830ffba57a9fd06881860d9a3eab633a9955.
- The replay reproduced the original post-CTS detailed-route 2x-OpenRCX setup and hold slacks **exactly to 6 decimal places** for both designs. Independent source netlist and routed DEF mapping ties each STA endpoint to named RTL state. This is not foundry signoff.

| Metric | D8 V296 pairwise | D4 optimized serial |
|---|---:|---:|
| Extracted setup slack | -684.592 ps | -1316.510 ps |
| Extracted hold slack | +10.986 ps | +2.572 ps |
| Recovery required to final +50 ps gate | 734.592 ps | 1366.510 ps |
| Worst setup path, launch state | candidate.issue.scheduler.rr1[1] | strongest_serial.issue.scheduler.rr3[0] |
| Worst setup path, capture state | staged_operand_data[3][2] | staged_operand_data[7][6] |
| Reported path pin rows | 88 | 92 |
| BUF/CLKBUF rows on data path | 40 | 35 |
| Sum of buffer-attributed increments | 1372.418 ps | 1292.220 ps |
| Max saving under hypothetical 2x buffer-only acceleration | 686.209 ps | 646.110 ps |
| Buffer-only 2x deficit after that hypothetical | 48.383 ps | 720.400 ps |

**New falsification:** simply accelerating *all* existing buffer-attributed path increments by 2x cannot recover the frozen setup deficit for either completed design, even with no rerouting penalty. Under a fixed-path, uniformly scaled buffer-increment model, D8 V296 would require at least **2.151712x** acceleration across every one of its 40 buffer increments. D4 serial would remain **74.290 ps short even if every one of its 35 buffer increments were eliminated entirely**. These are conditional counterfactuals, not physical impossibility proofs for all repairs: OpenSTA increments include upstream wire effects, and retiming, logic restructuring, resizing or rerouting can change the critical path.

## Architecture consequence

The actual D8 worst path traverses scheduler RR control through the issue/operand-selection cone into staged operand data. A repair confined to external input conditioning or a single buffer chain is not justified. Both combinational logic and routing must be considered, while preserving identical register-file resources and a strong serial control. D8 V296 still has only **1015.843 um2** area headroom and one cap violation; D4 serial has six cap violations. Closing setup alone cannot pass the frozen gate.

**Crucial limitation:** D8 pairwise and D4 serial are at different depths. D4 pairwise and D8 serial remain routing-timeout censored. No matched timing, area, throughput or power advantage has been demonstrated. Do not compare the two measured slacks as a head-to-head speedup.

## Reproduction

Use research/v296/deep_bank_extracted_path_locality.py with --self-test and all four original/replay ZIP arguments. The independent checker pins all four SHA-256 digests, compares original STA numerical evidence, validates named endpoints against the original synthesized Verilog and routed DEF, recomputes every buffer increment and rejects altered source identities. Full machine-readable results are in DEEP_BANK_EXTRACTED_PATH_LOCALITY_20261028.json.

**Next kill test:** freeze a physically plausible *symmetric* intervention that can affect enough of the full 4+ ns reported data path while remaining within area, setup, hold, capacitance, slew and DRC gates. Do not spend another full-route run on buffer-only optimization or timeout increases. V296 is the only active architecture mechanism, V287 retired; Kernellum PR #119 and prospective holdouts untouched.
