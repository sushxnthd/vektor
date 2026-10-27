# V296 routed critical-path reconstruction: frozen protocol (2026-10-27)

## Scientific question

The decoded density-0.35 implementation is already **rejected**: V296 has -220.829 ps extracted setup slack, -10.023 ps hold slack and three cap violations at 3.5 ns and 2x RC; optimized serial has -711.405 ps setup and -13.032 ps hold. Existing logs contain pre-CTS path details but do not identify the post-route extracted critical paths. This experiment attempts a **read-only reconstruction** from the original routed DEF and extracted SPEF without rerouting or altering the rejected implementation.

## Precommitted input provenance

Source run: https://github.com/sushxnthd/vektor/actions/runs/40427986118

- V296 artifact ID 12703514184; original ZIP SHA-256 `c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7`.
- Fifth-stage-optimized serial artifact ID 12703682763; original ZIP SHA-256 `928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4`.
- Same pinned OpenROAD `2.0-17598-ga008522d8`, same Nangate45 platform revision `eda8e552974d47a12616294dddf4012d892548d3`, same 3.5 ns clock, 0.15 ns IO delays, 0.04 ns input transitions, 0.005 output loads, 0.25 maximum transition, 16 maximum fanout, reset false path, propagated clock and already-scaled extracted SPEF. **Do not apply 2x RC again.**

## Frozen falsification and acceptance

1. Each original artifact ZIP must match its pinned SHA-256, and both routed DEF and extracted SPEF must exist. Missing or expired artifacts are an external blocker, not a physical result.
2. Replay OpenROAD loads the DEF, liberty and extracted SPEF, reconstructs original constraints and prints 10 setup and 10 hold paths. No synthesis, routing, resizing, or parasitic re-extraction is allowed.
3. The replay's maximum and minimum worst slacks must each reproduce the original physical run to **within 0.001 ns** (1 ps), and the first named path slack must match its corresponding worst slack to within 1 ps. If any condition fails, the verdict is `INCOMPLETE_NO_EXTRACTED_PATH_CLAIM`, and no critical-path attribution is made.
4. On success, identify the extracted startpoint and endpoint for both contestants. Compare with the prior scheduler-to-operand-capture hypothesis, without assuming it survived routing. Full raw paths, including slew, capacitance, fanout and incremental timing, must be retained.
5. Regardless of success, the density-0.35 decoded repair remains rejected. The experiment is diagnostic only and cannot establish feasible GPU speedup, power improvement, or RTX-5090 equivalence. Sealed workload holdouts stay unopened.

The read-only reconstruction may fail if the exported DEF cannot reproduce OpenROAD's internal post-route timing network, propagated clock, or timing constraints. Such failure is **not** evidence that the original routed results are wrong. Preserve both failed logs and do not relax the 1 ps threshold post hoc.
