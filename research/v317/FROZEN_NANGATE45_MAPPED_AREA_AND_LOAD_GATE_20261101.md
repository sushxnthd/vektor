# V317 frozen mapped-cell and fanout-sensitivity gate (2026-11-01)

## Pre-outcome hypotheses
Source: `abdbc0e61210afd14d4f8432813cda707cb856d3`. The three-point parameterized full-input equivalence job #41292817868 completed successfully. No mapped-cell outcome was inspected before freezing this protocol.

1. **Predicted implementation win:** with identical 4-slot, 16-bank ports, a pinned Nangate45 typical library, identical Yosys synthesis and ABC mapping, pairwise fixed priority will occupy less **mapped standard-cell area** than the source fixed-priority bank-mask implementation.
2. **Second predicted implementation win:** pairwise rotating priority will occupy less mapped area than the source rotating wrapper. Compare each against its *equally optimized* fixed-priority alternative, not against the unoptimized bank-mask implementation.
3. **Predicted throughput no-win:** because pairwise and bank-mask versions issue exactly the same grants, there is no intrinsic service-cycle throughput advantage at equal clock/ports. No IPC speedup may be inferred from mapped area.
4. **Wire/load uncertainty:** report worst net fanout, total input-pin sinks, and an explicit dimensionless depth/fanout stress sweep at alpha = 0, 0.05, 0.20, 0.50. These are sensitivity proxies, **not** RC extraction, cell timing, clock signoff, or GPU power.

## Frozen procedure
- Pin OpenROAD-flow-scripts Nangate45 typical Liberty at commit `202c7fccbce32e86db899c54b0a0f0484f869cc3`, Git blob `90e4afb274cfc6514c587c434c77903d554117d1`. Verify `git hash-object` before use.
- Map four implementations: source fixed, pairwise fixed, source rotating, pairwise rotating. Use identical Yosys `synth -noabc; dfflibmap; abc -liberty; stat -liberty; write_json` flow and one library.
- Independently parse Liberty cell areas and mapped JSON cell types. Fail if an unmapped logic cell, unrecognized cell, missing port direction, or cyclic combinational path is found. Preserve all logs and mapped JSON even on failure.
- Treat 0/2 implementation-win predictions passing as a negative result. No refitting after outcomes.
- Do not claim that a fanout penalty is a measured delay. Later use OpenSTA/OpenROAD with actual load, clock, placement, and routing to validate timing.

## Kill / continuation rules
If mapped area fails to improve or strong equal-resource alternatives dominate, reject the hardware-cost claim. If an improvement survives, retain only the *source-equivalent area optimization* until physical timing and wire checks. A world-class GPU throughput claim still requires real workload traces, matched timing/area/power and a distinct advantage over rotating and oldest-first scheduling.
