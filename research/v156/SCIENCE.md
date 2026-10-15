# V156 SCIENCE ledger — frozen before STA

**One active question:** Does V153's accumulation-to-rounding cutset yield a robust *mapped timing and area-normalized throughput* improvement over a genuinely equal-latency V151 buffer, not merely lower generic logic depth?

- **Frontier / best-known:** V155's one-lane Nangate45 mapping reports 8,043.574 vs 8,029.210 library area units, 161 DFFR_X1 each, and 24,220/24,220 oracle comparisons for both. No STA yet. Conventional arithmetic pipelining is prior art; CVFPU/HardFloat remain external controls.
- **Measurable objective:** same one-lane two-stage ready/valid interface, same reset, tags, masks, library blob, mapping commands and 10 ns OpenSTA constraints. Report worst constrained path slack, 10 ns minus slack, whole-module area, and oracle correctness. This first STA is unplaced; physical PPA and system throughput are future gates.
- **Strongest equal-resource internal baseline:** buffered V151 at equal latency and capacity. Strongest external matched public baseline remains outstanding; do not claim global superiority.
- **Mechanism and prediction:** cutting the accumulation-to-rounding cone changes which logic is between registers. Prediction: lower mapped critical-path delay for V153 even though both consume two cycles; no equal-clock cycle-throughput improvement is expected from latency alone.
- **Decisive falsification:** no timing gain, any oracle mismatch, or mapped delay-area product worse by more than noise; report even if hypothesis loses.
- **Publishable threshold:** novelty audit excluding ordinary pipelining, >=5% repeated area-normalized real-workload advantage versus a strongest matched open baseline, boundary prediction, unseen workload and independent checker.
- **Architecture-relevance threshold:** >=10% mapped constrained-delay reduction with <=10% mapped area cost, plus <=5% loss on dependent/divergent/memory-stalled kernels after scoreboard integration.
- **Kill condition:** after three substantive attempts without better evidence or a useful crossover, reformulate. Infrastructure errors do not count as scientific falsification.
- **Wildcard (~10% cheap effort):** investigate dependence-latency reversal once scoreboard/writeback exists; do not promote an unrelated theorem.
- **Prior art:** conventional pipeline cuts and retiming; OpenHW CVFPU, Berkeley HardFloat, ARCH HDL bounded-FMA. A better result alone is not novelty.
- **Evidence class:** V156 uses open standard-cell Liberty timing before placement, not physical routed silicon.

**Decision remains pending until V156 CI results are inspected.** No RTX 5090-class claim.

## V156 follow-up: measurement validity (2026-10-16)

The original OpenSTA script failed due unsupported Tcl options. On the corrected-Tcl rerun, the buffered control netlist parsed and yielded -2.93 ns worst slack at a 10 ns constraint; the cutset netlist produced a Verilog parser error on line 40278 (`assign { ... } = ...`), so its displayed +1.65 ns slack is **not valid evidence**. The subsequent `-simple-lhs` workaround failed because Yosys 0.9 does not recognize that option. The next discriminating run must normalize the cutset mapped Verilog using Yosys `splitnets` and require both logs to parse without errors before comparing delay. These are infrastructure failures, not hypothesis falsification. The V155 mapped-area ranking reversed across Yosys versions, so a single-toolchain area result is insufficient for a robust claim. The original mechanism prediction remains open; the scientific novelty threshold remains unmet.
