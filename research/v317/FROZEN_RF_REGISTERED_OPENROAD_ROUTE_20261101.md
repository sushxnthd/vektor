# V317 frozen matched placed/routed bank-credit experiment (2026-11-01)

## Identity and precedence
The only active Vektor implementation mechanism remains the grant-equivalent **fixed-priority pairwise bank-credit** arbiter, on `research/v317-sass-provenance-gate`, draft PR #34. V287/V296 are historical. Do not create another research branch or change scheduling policy. Kernellum PR #119 remains read-only during this urgent primary gate.

## Critical correction to prior evidence
The 5.636x *uniform per-net added capacitance* margin is not a routed-wire prediction. It ignores placement, fanout geometry, pin access, layer assignment, coupling, buffer insertion, timing constraints and upstream driving cells. A net with +0.681 fF ideal-wire headroom can be legal after repair, and a net with +3.838 fF headroom can fail after routing. Neither outcome implies a GPU throughput gain.

## Physical experiment frozen before evaluation
Use the same registered 36-bit input/4-bit output wrapper around each original/pairwise arbiter, with the same 2.0 ns target clock, 0.20 ns external input/output delays, input drive BUF_X2, 10-fF external output load, Nangate45 process library, 35% and 65% requested core utilization, and identical ORFS scripts. The source and pairwise wrappers differ *only* in the combinational arbiter instantiated. Include all 40 register bits in both. Clock-to-clock input-to-output logic is the relevant critical path; an isolated combinational-cell path is not tile clock closure. Use same die/core and pin constraints where practical; if ORFS autogenerates different floorplans, report the mismatch and downgrade to unmatched floorplan evidence.

### Frozen predictions / kill criteria
1. **Predicted implementation win (35% utilization):** pairwise has fewer final placed standard-cell area units than original; this is falsified if equal or greater after all inserted repair cells. This is not a predicted GPU throughput gain.
2. **Predicted architectural no-win (fixed 2.0 ns, identical grants and RF ports):** if both meet electrical and setup/hold requirements, completed grants per cycle and equal-frequency service throughput are **identical**, 1.000x, regardless of routed area. If either fails timing, do not claim either physical configuration meets the regime.
3. **Stress transfer (65% utilization):** test the same prediction without refitting parameters. A failure or no-route is a recorded negative result, not a reason to retune placement parameters.
4. **Timing kill:** if final routed critical paths or max-transition/max-cap violations erase pairwise's timing/area improvement, reject physical superiority. If 2.0 ns fails for either design, report failure rather than treating the raw critical delay as a frequency gain.
5. **Physical fairness:** report actual die/core dimensions, routed wirelength/RC, cell area, inserted buffers, clock tree, setup/hold, max cap/transition, routing DRC and actual output loads. Missing reports are **UNVERIFIED**, not PASS.
6. **Reproducibility:** pin the ORFS source commit, container digest, Nangate45 source, complete SDC/config and workflow SHA. Preserve failure logs and artifacts even if the flow stops.

## Limits
This small registered arbiter wrapper is a physical *control-block* experiment, not a GPU tile, register-file SRAM, full issue pipeline, power signoff or 5090-equivalent design. No extrapolation to GPU IPC or wattage is authorized. Actual routed RC must replace the previous uniform-wire proxy before electrical claims.
