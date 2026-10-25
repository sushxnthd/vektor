# V296 integrated RF-return balanced-tree repair: prospective protocol (2026-10-26)

**Pre-evaluation registration.** This protocol is committed before the new RTL/synthesis/physical workflow is run. The prior original paired physical result and negative evidence are immutable. This is a **shared datapath implementation repair**, not a replacement of V296 bank-admission semantics, issue resources or the retired V287 mechanism.

## Exact intervention and controls

- The original integrated slice `v296_tile_slice.sv` remains untouched. Create `v296_tile_slice_return_tree.sv` by changing ONLY the eight-operand RF return mux: the existing 16-bank priority-if chain becomes 16 bank-masked 8-bit words and a balanced 4-level OR reduction per operand.
- Preserve the original 32-wave scheduler, 4 issue slots, 16 physical RF banks, 2 read ports/bank, 1 global write port, two 8-bit words/bank, output registers, arbitration RTL, RF address-port assignment, physical constraints, and operating clock.
- Compare **four** implementations at RTL and mapped synthesis: original pairwise, original serial one-hot, balanced-return pairwise, balanced-return serial one-hot. The return-tree optimization is given to **both** competitors. The serial baseline must not be intentionally disadvantaged.
- Compare the two balanced-return contestants using the **same frozen** integrated post-CTS detailed-route OpenRCX flow as the original paired slice, including 3.5 ns clock, +50 ps setup guard, zero negative hold, zero slew/cap violations, identical 2x RC and floorplan/placement/repair rules. Preserve failed logs and artifacts.
- Keep strict equal-consumed-area Pareto claims **disabled** until physical equal-area allocation is independently enforced. Do not infer measured GPU power from capacitance proxies.

## Frozen predictions, falsifiers, and workload regimes

- **Topology hypothesis:** replacing a serial-looking priority bank-data return mux with balanced OR-of-one-hot selects may reduce the scheduler-to-executed-data combinational depth. The direction and magnitude of mapped and extracted changes are **unknown** and must be measured. A mapped logic-depth regression or area blowup is a valid negative result.
- **Predicted-win workload regime (conditional):** high-bandwidth, non-saturated RF traffic with enough occupancy to exercise issue slots. A positive throughput difference is allowed **only if** physically feasible clocks differ after matched repair and equal resource accounting. For any fixed equal feasible clock, predict exactly **zero V296-versus-serial admissions/second gain**.
- **Predicted-no-win workload regime:** memory bandwidth saturated (e.g. the previously modeled 1 GB/s cap); even a faster clock should not improve useful throughput once that external bandwidth cap binds. Predict zero useful-throughput gain, subject to the specified finite queue/transient tolerance.
- **Immediate kill:** If either contestant fails the frozen electrical/setup/hold gate, no feasible integrated speedup or Pareto claim; if both close but matched equal-resource serial erases the frequency/area gain, reject V296 performance superiority. If return-tree RTL differs from original for any valid initialized two-state test, reject the topology before physical interpretation.
- Positive-law form for any surviving **clock-derived** result: useful throughput is bounded by `min(eligible_admissions_per_cycle * f_clock, bandwidth_bytes_per_second / bytes_per_admission)`, further reduced by occupancy, port contention and control overhead. The candidate and control have the same admission function; any gain must arise from independently measured feasible `f_clock`, energy, or area packing, not a changed compatibility probability. Correlation-aware admission rates must be estimated on prospective unseen workloads.

## Evidence tiers and reporting

1. An independent Python randomized exact-bank-select oracle (100,000 samples) already passed before preregistration; this is not RTL equivalence.
2. Require four-way cycle-level SystemVerilog equivalence against the independent RF read oracle and nontrivial contention/hold/write patterns.
3. Require same-library four-way mapped synthesis with area and longest graph path, without confusing graph depth with extracted STA.
4. Require paired routed SPEF/DEF, setup/hold, slew/cap and source hashes. The physical audit must fail closed on incomplete artifacts and report both contestants even when one fails.
5. Only then evaluate matched-area feasibility, energy proxies, sensitivity and frozen win/no-win workloads. Holdouts remain sealed until the physical gate.

**No claimed result yet:** this document predicts a testable topology change, not physical closure, throughput improvement, measured power or RTX-5090 equivalence. Preserve the existing draft PR and branch; V296 is the sole provisional mechanism; Kernellum PR #119 is unaffected.
