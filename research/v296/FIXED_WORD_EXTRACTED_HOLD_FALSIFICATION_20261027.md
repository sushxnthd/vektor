# V296 fixed-word full-route candidate: extracted hold falsification (2026-10-27)

## Decision: REJECT the fixed-word two-word-RF implementation

This report applies the **already-frozen** protocol in `FIXED_WORD_POSTCTS_STRONG_CONTROL_PREREG_20261027.md`. The sole provisional architecture mechanism remains V296 pairwise bank admission. V287 stays retired. This is a negative result for one symmetric **implementation**, not a rejection of all V296 mechanisms.

Original hosted experiment: [Actions run #40469489684](https://github.com/sushxnthd/vektor/actions/runs/40469489684), candidate job `122089201452`, [candidate artifact #12721519936](https://github.com/sushxnthd/vektor/actions/runs/40469489684/artifacts/12721519936). The ZIP was downloaded and independently SHA-256 verified against GitHub's upload digest:

`7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b`

The archived runner, unchanged physical Tcl, and RTL synthesis-source hashes matched the archived frozen manifest. Original routed DEF and extracted SPEF are present, the physical runner exited 0, the DRC report is empty, and the physical log reports completed detailed routing, 2x RC, and propagated clocks. The independent checker re-parsed the extracted setup/hold/area/electrical metrics from the physical log and matched the archived physical audit.

| Frozen candidate gate | Original extracted result | Gate | Verdict |
| --- | ---: | ---: | --- |
| Setup slack | **+74.236 ps** | >= +50 ps | PASS |
| Hold slack | **-12.622 ps** | >= 0 ps | **FAIL** |
| Capacitance violations | 0 | 0 | PASS |
| Slew violations | 0 | 0 | PASS |
| DRC violations | 0 | 0 | PASS |
| Final cell area | 13,379.001906 um² | <= 30,000 um² | PASS |

The candidate has **24.236 ps** setup headroom above the frozen guard but violates hold by **12.622 ps**. Its pre-CTS setup slack (+230.183 ps) deteriorated by **155.947 ps** after CTS/routing/extraction; pre-CTS hold (+112.255 ps) deteriorated by **124.877 ps**. Final cell area is 572.431880 um² (4.46983%) above the original pre-CTS candidate area. These are stage comparisons within this implementation, not attribution to any single timing cone.

**Falsification is immediate and unconditional:** the frozen protocol requires nonnegative extracted hold. Zero DRC and positive setup do not override the hold failure. Do not retune the frozen gate or describe this candidate as physically feasible.

## Reproduction and evidence tiers

- Re-run `python3 research/v296/fixed_word_extracted_hold_falsification.py /path/to/v296-fixed-word-postcts-pairwise.zip --self-test` on the original ZIP from artifact #12721519936. The standard-library checker rejects modified ZIP bytes and mismatched manifest, physical Tcl, source RTL hash, extracted log, or audit metrics.
- The compact, reproducible verdict is in `FIXED_WORD_EXTRACTED_HOLD_FALSIFICATION_20261027.json`.
- Evidence tier: **SHA-verified completed post-CTS detailed-route and extracted OpenRCX candidate**, not production signoff or a matched Pareto result.
- At inspection, strongest fifth-stage optimized serial control job `122089201627` remained in progress. Its result is necessary for complete matched physical characterization but cannot rescue this candidate's failed hold gate. No serial area/timing numbers are imputed.
- No workload holdouts opened. No measured GPU throughput, power, or RTX-5090-equivalence claim. The two-word-per-bank fixed-word RF shortcut remains non-transferable to deeper SRAM banks without additional addressing or fallback hardware.

## Next falsifiable step

Preserve the pending serial artifact and independently audit both original contestants. For V296, identify the **extracted worst hold path and endpoint**, then preregister a materially distinct symmetric physical/RTL intervention. Apply it to the strongest serial control too; require cycle equivalence, matched resources, nonnegative extracted hold, +50 ps setup guard, zero DRC/cap/slew, and real workload/port/occupancy sensitivity. No threshold relaxation, force-push, merge, or second active architecture mechanism.
