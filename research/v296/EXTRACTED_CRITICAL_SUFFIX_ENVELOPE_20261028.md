# V296: extracted critical-path suffix falsification (2026-10-28)

**Result: final RF-return-mux-only repair is insufficient for either completed routed design.** This is a necessary fixed-path counterfactual, not a physical repair or GPU advantage.

The independent SHA-pinned checker uses the original read-only OpenSTA replay ZIPs from [Actions #40597982594](https://github.com/sushxnthd/vektor/actions/runs/40597982594): D8 pairwise artifact 12776073774 (SHA-256 9ec4107e2d7c3ea1362f0c304280dcc771a738a60e6a5d67fae2118d2ccafbda) and D4 optimized serial artifact 12776328412 (SHA-256 1ae842da60de4d7a38507188b3e7830ffba57a9fd06881860d9a3eab633a9955). Original replay ZIP hashes, path identity, slack, pin counts and timing increments are checked. Local self-test, both original replays and deliberate corrupted-ZIP rejection passed.

For extracted setup slack L and frozen guard g=+50 ps, the required recovery is R=g-L. An ideal uniform speedup s of only a path suffix S can recover at most S(1-1/s) in the fixed-path model. Therefore a **necessary** condition for closure is S >= R/(1-1/s). This is not a sufficient physical condition; OpenSTA increments include interconnect effects and redesign changes the path.

| Routed extracted metric | D8 V296 | D4 optimized serial |
|---|---:|---:|
| Setup slack | -684.592 ps | -1316.510 ps |
| Recovery to +50 ps | 734.592 ps | 1366.510 ps |
| Launch-Q to capture-D delay | 3993.668 ps | 4632.721 ps |
| Final mux and downstream tail | 497.762 ps | 433.772 ps |
| **Deficit even if that entire tail were zero-delay** | **236.830 ps** | **932.738 ps** |
| Last possible cut for 2x suffix acceleration | wire202/Z, arrival 2.963817 ns | _10999_/ZN, arrival 2.259538 ns |
| Minimum affected suffix for 2x acceleration | 1469.184 ps | 2733.020 ps |
| Remaining area to 30,000 um2 | 1015.843 um2 | 6734.310 um2 |
| Capacitance violations | 1 | 6 |

The D8 2x repair would need to affect at least 31 following path-pin rows, and the D4 serial at least 45. Even an ideal **3x** suffix speedup needs 1101.888 ps and 2049.765 ps of affected path respectively. The final operand-return mux tail is far too short for either. Netlist pin names are specific to these immutable routed snapshots, not portable RTL design targets.

**Decision:** kill local late-return-mux tuning as a standalone physical repair. A next candidate must affect the upstream scheduler-to-operand logic/interconnect and be applied symmetrically to V296 and the strongest serial control before matched routing. Preserve the original 3.5 ns, 2x extracted RC, +50 ps setup, nonnegative hold, zero DRC/cap/slew, 30,000 um2 budget, two RF reads per bank and unchanged issue resources. Do not reroute merely with longer timeouts.

**Limitations:** D8 pairwise and D4 serial have different RF depths; their counterparts timed out. No equal-depth matched feasibility, throughput, power or RTX-5090-equivalence claim. This is exploratory post-outcome diagnosis, not prospective workload validation. Existing workload holdouts remain sealed. V296 is the sole provisional mechanism; V287 retired.

Reproduce: run 'python3 research/v296/v296_suffix_envelope.py --self-test' and then 'python3 research/v296/v296_suffix_envelope.py --d8 github-actions-artifact-12776073774.zip --d4 github-actions-artifact-12776328412.zip --output suffix.json'. The script imports the existing SHA-pinned extracted-path verifier.

**World-class completion gate: not reached.**
