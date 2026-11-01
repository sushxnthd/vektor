# Frozen V317 pre-route electrical-constraint audit (2026-11-01)

The six-load 2/20/40/60/80/100-fF timing outcomes were already observed in source-pinned run #41304674526. This is a **post-result diagnostic**, not a prospective timing prediction. It must not be used to retrospectively relabel the previous holdouts.

**Question:** does the high-output-capacitance delay reversal occur inside or outside the characterized Nangate45 cell max-capacitance and max-slew electrical limits? A large numerical STA arrival time does not certify that a driver is legal. Use the *same four mapped RTL netlists* and *same six output loads* and OpenSTA `report_check_types` for max capacitance, max slew and max fanout, archiving all 24 raw reports. Report any violations without suppressing them, even if they invalidate the attractive timing or load-crossover interpretation.

**Frozen hypothesis:** the 100-fF pairwise-fixed grant output is likely to exceed a cell max-capacitance constraint; low-load 2-fF is expected to have fewer violations. Both are predictions, not facts. If 100-fF violates max-cap or max-slew, classify the previously observed 100-fF timing reversal as **electrically inadmissible without output buffering/resizing**, and require a physically legal matched remap before making a silicon timing claim. If the tool cannot report electrical constraints, mark the gate **unverified** and do not silently infer legality.

The test is limited to cell electrical limits with ideal wires. It does not test IR drop, electromigration, physical routing, actual wire capacitance, power, or integrated GPU timing. Keep the existing branch, draft PR and mechanism unchanged.
