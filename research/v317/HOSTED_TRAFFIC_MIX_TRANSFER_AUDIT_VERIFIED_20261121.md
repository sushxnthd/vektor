# Hosted workload-mix transfer falsification: verified (2026-11-21 UTC)

## Source and execution provenance
- Research branch: `research/v317-sass-provenance-gate`; existing draft PR #34.
- Workflow: `.github/workflows/v317-periodic-conservation.yml` at blob `4e6c51a1f1f15367b3c16c04aa611c2a73e7cd93`.
- Triggering commit: `1f805838c76144b1c21c4a57f48544d84ca63a02`.
- Hosted GitHub Actions run: https://github.com/sushxnthd/vektor/actions/runs/44855058611 ; conclusion `success`.
- Job `independent-periodic-audit` (ID `136695192683`) completed successfully. Step 18, `Independent workload-mix transfer falsification (development only)`, and step 19, source digest, both succeeded. Steps 14–17, the physical-headroom and dimensional work-byte checkers and their digests, also succeeded.
- Checker: `research/v317/rtl/independent_traffic_mix_transfer_audit_20261121.py`. This is a hosted execution verification, not a newly measured GPU performance result.

## Interpretation and decision
The exact-rational constructed counterexamples falsify unconditional transfer of a traffic-per-completed-work floor across workload mixtures. A capacity ceiling requires a justified candidate-specific traffic floor, consistent work/time units, and a specified class/mix envelope. Passing the checker establishes that the repository's assertions executed successfully; it does not measure baseline issue utilization, candidate bandwidth, physical wire load, or unseen-workload throughput.

The alternating-middle-slot priority candidate remains **NO-GO**: historical development throughput 0.999935x versus equal-resource compact greedy, before physical overhead. Preserve V296/V317 as the current research lineage, V287 as historical, and the prospective workload holdouts unopened. No new mechanism is activated. Prior compact-greedy RF-proxy routes remain electrically illegal; no legal integrated tile, SRAM macro, calibrated power, or RTX 5090 equivalence is claimed.

## Next discriminating gate
Measure baseline completed work/cycle, issued operations/cycle, bytes/completed work by class, FIFO occupancy and stall attribution on identical frozen traces. Independently verify traffic counters and units. Only then preregister a candidate-specific capacity/occupancy boundary and matched equal-resource RTL/physical test. Kill any candidate if clock, bandwidth, control, occupancy, or electrical legality removes its gain.
