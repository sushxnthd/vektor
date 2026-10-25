# V296 integrated banked-RF execution slice: prospective physical falsification (2026-10-25)

**Preregistered before the integrated RTL and physical outcomes.** Sole active mechanism remains V296 pairwise bank arbitration. V287 is retired. This is a bounded, small **register-file execution slice**, not a complete GPU tile, tapeout, or RTX 5090 comparison. Preserve previous physical evidence and sealed workload holdouts.

## Fixed hardware and matched contestants

Implement exactly the same 32-wave steal scheduler, four issue slots, 16 RF banks, two read ports per bank, one global write port, two 8-bit words per bank, 8-bit execution results per slot, 3.5 ns nominal clock, wave-bank input mappings, and deterministic slot/operand priority in **both** contestants. Only replace the combinational arbiter: `v296_issue_core` (pairwise) versus `v295_issue_core #(.PREDECODE(0))` (strong serial one-hot). A single parameterized wrapper must instantiate both. The shared RF fabric routes **at most two accepted reads per bank per cycle**, selecting the first and second read requests by fixed slot/operand order. Do not implement eight independent read ports per bank.

Compare cycle-by-cycle issued wave IDs, grants and registered execution results under a matched write stream and adversarial bank-conflict patterns. Include a checker for bank read-port capacity, no phantom issued operands and RF write/read consistency. Count same-clock admissions: predicted **exact equality**. In particular, do not count a controller slack improvement as a throughput gain.

## Frozen physical protocol

Both variants use the pinned Nangate45 library, pinned OpenROAD and Yosys workflow, identical synthesis, floorplan **260 x 260 um die, 240 x 240 um core**, 45% placement target, 3.5 ns clock, 150 ps input/output delays, 5 fF output load, 250 ps maximum slew, fanout-16, propagated-clock CTS, detailed routing and **2x OpenRCX extracted RC**. Retain the prior control-advantaged fifth repair round and symmetric 250 ps post-CTS setup repair, applied by the same script generator. Changing the floorplan is permitted **only** by an exact-match, fail-closed transformation of the frozen controller Tcl, identical for both. Do not modify the original controller flow or select physical parameters based on outcomes.

Preserve synthesis logs, DEF/SPEF/DRC, extracted worst setup/hold slack, slew/cap counts, cell area, clock-buffer increments, and source hashes for **both** variants. Fail closed if either is incomplete. The original 7400 um2 **controller** ceiling is not a valid integrated-slice ceiling. Instead preregister **30000 um2** per contestant as an exploratory upper limit and +50 ps setup, nonnegative hold, zero slew/cap/DRC as feasibility gates; exceeding the area limit is a negative outcome, not a reason to retune the floorplan.

## Predictions and falsifiers

1. **Functional prediction:** identical grant, wave IDs and execution results for every checked cycle; zero extra admitted work at fixed clock. Any mismatch kills V296 as an interchangeable arbiter.
2. **Physical hypothesis:** candidate integrated-slice cell area at least **1%** smaller and extracted setup slack at least **50 ps** better, with **both** contestants physically feasible. These are preregistered exploratory thresholds, not previous results. If the result fails, preserve the negative finding and reject an integrated-slice timing/area victory. Do not retry by adapting constraints.
3. **Throughput hypothesis:** no GPU performance gain is claimed from this test alone. Positive throughput would require **measured** integrated tile Fmax and non-bandwidth-limited unseen workloads. In the no-win regime where another tile path dominates or memory is saturated, predict exactly zero gain. The existing held-out workload families remain sealed.
4. **Power and scale:** equal RTL-level useful-output activity is expected; this is **not** energy equivalence. Cell area and clock-buffer counts are area/power proxies only. Measured switching power, leakage, macro RF integration, full memory hierarchy and physical replication remain future gates.

**Decision policy:** report FAIL / INCOMPLETE explicitly. No selective wins, no seed selection, no new architecture mechanism, no merger of draft PR #13. The independent audit must not use the controller's 7400 um2 gate or infer tile frequency from setup slack alone.
