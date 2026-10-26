# V296 decoded RF-slice post-CTS extracted-RC falsification (frozen 2026-10-26)

## Sole mechanism and evidence boundary

V296 pairwise RF-bank arbitration remains the sole provisional architecture mechanism; V287 remains retired. This experiment tests the **same symmetric bank-index decoder and operand-capture RTL** already verified at the matched pre-CTS checkpoint. It introduces no new arbitration mechanism, additional bank port, or additional issue slot. The previous decoded RTL oracle passed 4,096 checks, and the four-way Nangate45 synthesis and matched pre-CTS reports are preserved without alteration. The 0.206 ps pre-CTS guard margin is not routed signoff.

## Fixed matched physical experiment

Synthesize `v296_tile_slice_bank_decode.sv` with `PAIRWISE=1` (V296) and `PAIRWISE=0` (serial one-hot) using the **same** pinned Yosys, Nangate45 library, OpenROAD, 260 x 260 um die / 240 x 240 um core, 45% placement density, 3.5 ns clock, 150 ps I/O delay, 5 fF output load, 250 ps maximum slew, fanout 16, propagated-clock CTS, +250 ps post-CTS setup repair, detailed route, and 2x extracted OpenRCX parasitics as the existing integrated tile-slice experiment. Preserve the serial control's **independently optimized fifth pre-CTS repair** (`V296_CONTROL_EXTRA=1`); V296 gets `0`. The generated physical Tcl must remain byte-for-byte identical to the existing frozen integrated-slice Tcl. Both contestants receive the identical RTL decode/operand-capture intervention.

Derive the new runner by fail-closed, exact-match substitution of only the RTL source and top module from `run_tile_slice_cts.sh`. Do not change clock, floorplan, density, RC, CTS, routing, repair policy, or the original physical scripts. Require source hashes, generated-runner/Tcl hashes, original independent integrated-slice audit, and a second provenance/feasibility audit. Keep separate artifact names per contestant; preserve artifacts even on physical failure.

## Prospective decision gates (before post-CTS outcomes)

1. **Functional:** the already-passed delayed RTL oracle must remain green. No same-clock, same-resource admission gain is predicted.
2. **Feasibility:** each routed implementation must independently satisfy setup slack >= +0.050 ns, hold slack >= 0, zero capacitance/slew/DRC violations, full route, and final cell area <= 30,000 um2. If either fails, no Pareto or GPU-performance claim. In particular, V296 failing kills the decoder as a viable 3.5 ns physical repair.
3. **Matched physical Pareto:** only if both pass feasibility, evaluate V296 final routed cell area at least 1% below optimized serial and extracted setup slack at least 50 ps better, under identical constraints. Preserve negative results.
4. **No extrapolation:** neither a single-slice area saving nor a feasible 3.5 ns period establishes a GPU speedup. No full GPU tile, SRAM macro, realistic power, thermal, physical replication, or RTX-5090 equivalence is measured.
5. **Frozen conditional workload prediction:** independent, bank-distributed, occupancy-rich and bandwidth-unsaturated operations can win **only** if a physically feasible clock/area-reinvestment advantage exceeds the latency penalty; dependent low-occupancy or bandwidth-saturated workloads do not win. Existing prospective real-workload holdouts remain sealed until hardware gate closure. Re-evaluate the previously frozen synthetic boundary using physically supported period and final area only.

A routing timeout, missing artifact, absent serial fifth-stage marker, mismatched source/Tcl hash, or unsupported timing tier is **INCOMPLETE**, never a PASS. Do not adapt constraints after observing outcomes or rerun until a lucky seed wins. The workflow remains an explicit falsification attempt. Preserve PR #13 and all Kernellum PR #119 evidence without force-push or merge.
