# V297 matched physical kill protocol (frozen before mapped/placed outcomes; 2026-10-29)

## Sole candidate and controls
Candidate V297 bounded bank-rescue, current RTL `research/v297/rtl/v297_bank_rescue_core.v`. Control A is the existing rotating-serial module with exactly the same 3 request slots, 16 banks, two reads per bank, two issue slots, input/output register boundary and clock. Control B is a maximum-cardinality compatible-pair selector with age-based tie-breaking; its RTL must be implemented **before** mapped/physical comparison. An oracle implemented only in JS is not a physically matched control.

## Frozen physical constraints
Use the pinned Nangate45 typical liberty/LEF and OpenROAD/OpenRCX technology provenance already used for V296, but run a **fresh matched V297 physical experiment**. Equal input arrival constraints, output load, clock uncertainty, placement density, routing layers, CTS policy, 2x wire RC and tool timeout for all three contestants. Target 3.5 ns clock and +50 ps setup margin, hold slack >=0, zero final max-capacitance and max-slew violations, no unreported DRC. Preserve raw synthesis, STA, DEF, SPEF, tool version, logs and exit status for each contestant. Do not compare unmatched synthesis-only cell counts as routed area or energy.

## Predicted regimes and no-go
- **Predicted conditional win:** frozen two-arrivals/cycle three-job blocker motif, including all cyclic phase/offset adversaries. This is synthetic and may not survive physical/scoreboard effects.
- **Predicted no-win:** uniform 16-bank two-arrivals/cycle; only +0.0513% completion difference in the queue model, which even tiny clock overhead can erase.
- **Hard kill:** V297 fails any physical feasibility gate; or a feasible, same-resource max-pair controller matches or improves throughput at no worse physical cost; or realistic occupancy/memory traffic erases the benefit. Timeout is censored, not proof of infeasibility; one bounded rerun allowed only for diagnosed infrastructure failure, not indefinite constraint relaxation.
- **Claim boundary:** generic Yosys topological levels 24 vs 30 are not clock timing, PPA, or evidence of an RTX-5090-class GPU. Preserve all negative results.
