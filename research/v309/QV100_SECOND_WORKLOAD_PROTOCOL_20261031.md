# V309: second original QV100-SASS workload, prospective selection (2026-10-31)

## Status and question
Protocol frozen **before** second-workload simulation. The prior authenticated Pathfinder workload yielded 28,717 QV100 simulated cycles and 3,534/129 L1D/L2 misses, with zero benefit from doubling the simulated DRAM bus. This result cannot be generalized from one workload. We will test an independently selected second complete workload without choosing on observed simulator cycles or cache counters.

## Source-locked selection
Use the same SHA-256-pinned original Rodinia 2.0-ft Tesla V100 SASS trace archive as the Pathfinder experiment. Rank **all complete command-list workloads** by the sum of uncompressed command-list and referenced trace member sizes, breaking ties by exact archive path. Choose rank **two**, not the already studied rank one. Reject missing, duplicate, unsafe, ambiguous or unlinked archive entries; preserve original kernel order and all Memcpy commands. Do not reselect if the runtime fails. Record the exact archive SHA-256, every selected member digest and original command-list identity.

## Prospective measurement
Build exactly the already pinned QV100-SASS Accel-Sim/GPGPU-Sim revision, configuration and container. Execute **two** unmodified complete simulations of the second workload. Require exit marker, kernel completion, positive cycles/instructions, and independent reconstruction of per-kernel cycles and L1D/L2 misses from both raw logs. Do not change simulator parameters or architecture resources for this comparison. Record raw evidence and any failures, including timeouts.

## Frozen tests and stop conditions
1. Source-integrity PASS: selection rank is 2, distinct from rank 1; all selected members and command-list launches resolve uniquely.
2. Runtime PASS: both runs complete within the fixed per-run timeout, with the original kernel count and identical instruction counts; otherwise report FAIL_CLOSED, not zero cycles.
3. Independent-counter PASS: the separate checker agrees on both complete per-kernel sequences and totals; otherwise do not use cycles.
4. Distinct-behavior hypothesis (not a gate): at least one of cycles, instructions, L1D misses, L2 misses differs from Pathfinder. A failure is an honest negative observation.
5. No hypothesis of architectural improvement is registered: this is a **baseline transfer / simulator-input qualification experiment**, not an equal-resource architecture test.

## Research consequence
Only after this second workload is independently verified may the team freeze a single implementable equal-resource issue/occupancy/port mechanism and an a priori predicted-win and predicted-no-win regime, then test RTL equivalence, synthesis, matched area/timing, electrical and workload cycles. The zero-gain Pathfinder bus-width result is a negative control, not a candidate GPU architecture. V287/V296 are historical and are not reactivated. No RTX 5090-equivalence claim.

The existing V309 draft PR, branch, original evidence and Kernellum PR #119 remain unchanged except for additive second-workload evidence.
