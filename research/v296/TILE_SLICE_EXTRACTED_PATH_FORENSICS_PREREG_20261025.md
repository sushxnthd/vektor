# V296 integrated-slice extracted path forensics (prospectively frozen, 2026-10-25)

## Scientific question and evidence
The original paired run 40156470550 failed timing and electrical checks for **both** contestants at 3.5 ns. Its pre-CTS report_checks path is NOT an extracted critical path. Diagnose, rather than retune, the **original routed and extracted** implementation. Do not change either RTL, synthesis, clock, RF resources, load, repair policy, die/core, route, or original physical artifact. Use only the original run's pairwise and serial_onehot netlist, post-route DEF, extracted SPEF, physical logs and matching pinned Nangate45/OpenROAD tools. V296 remains the sole mechanism under falsification; V287 is retired.

## Frozen procedure
1. Download the two original artifacts from run 40156470550, never regenerate placement or routing. Preserve original artifact IDs 12585654946 and 12586607915, source provenance, original numerical measurements and file hashes.
2. Rebuild a **read-only** OpenROAD STA design for each contestant from the exact mapped Verilog, detailed-route DEF, and extracted SPEF. Recreate the frozen 3.5 ns clock, 150 ps I/O delays, 40 ps input transition, 5 fF output loads, 250 ps transition limit, false reset path and propagated clock. Do **not** apply RC scaling again: original SPEF already comes from the 2x OpenRCX extraction.
3. Report the worst five extracted setup and hold paths with endpoints, arcs, slew, capacitance and fanout; list maximum-capacitance violators and reconstruct setup/hold slack, cap/slew counts and area. No repair commands or optimizer may be run.
4. An independent parser cross-checks original evidence against the immutable observed pairwise (17857.644252 um2, -1.047895 ns setup, -0.036622 ns hold, 3 cap) and serial (18953.830505 um2, -1.859922 ns setup, -0.019796 ns hold, 3 cap). Reconstruction must agree within 0.005 ns for each slack and 0.01 um2 area, with exact cap/slew counts. If it does not, classify RECONSTRUCTION_MISMATCH and **do not attribute any critical path**.
5. Freeze extracted-path classification as diagnostic evidence only. Do not interpret a negative slack as a measured GPU Fmax, and do not count a hypothetical repair as a physical win. A future repair requires its own preregistered matched experiment and preserved failure.

## Decision
Either `EXTRACTED_PATHS_RECONSTRUCTED_BOTH_INFEASIBLE` with path/violation evidence, or `RECONSTRUCTION_MISMATCH_NO_PATH_CLAIM` / `INCOMPLETE` with the precise blocker. Neither changes the original failed physical gate. Same-clock arbitration throughput remains equal, power and equal-consumed-area GPU tile effects unmeasured. Keep prospective workload holdouts sealed.

## Tool-compatibility correction (before any successful reconstruction)
The initial diagnostic run 40168519865 preserved a 606-byte OpenROAD failure log: `ODB-0251 Chip already exists` from `read_verilog; link_design; read_def`. In pinned OpenROAD, the routed DEF is itself the authoritative complete logical/physical database. The read-only diagnostic now loads the DEF directly and retains the mapped Verilog for provenance checks. This is a reconstruction-loader correction, not a modification to physical evidence, constraints or the frozen acceptance thresholds. The workflow prints any subsequent tool failure verbatim.
