# V309 rank-two DRAM bus-width transfer: preregistration (2026-10-31)

## Decision question

Does a workload with materially more reported global writes per simulated instruction than Pathfinder obtain a meaningful cycle benefit from doubling the configured DRAM bus width? The selected original rank-two LUD-64 workload is already fixed by source bytes, not by performance outcomes. This is a **new parameter-sensitivity experiment**, not a physical GPU architecture mechanism or a new holdout workload.

## Frozen test, before LUD width outcomes

Use exactly the source-pinned QV100-SASS simulator, same ten original LUD launches, same original memory-copy commands, two independent replays per configuration, and identical configs except `-gpgpu_dram_buswidth` at 8, 16 and 32 bytes. Preserve existing Pathfinder data as the comparison, not as a prospectively unseen test. Source selection, launch count and baseline LUD counters were inspected before this prediction; LUD width-variant outcomes have not been inspected.

**Prediction P1 (no-win):** LUD's 32-byte setting improves cycles over its 16-byte baseline by less than 2%. The two-percent boundary is an explicit engineering materiality threshold, not a statistical confidence interval. **Prediction P2 (monotonic):** the 8-byte setting does not execute in fewer cycles than the 16-byte setting. **Prediction P3 (cross-workload no-win):** neither Pathfinder nor LUD obtains a >=2% benefit from doubling modeled width. Any prediction failure must be reported as a falsification, not repaired by post-hoc threshold changes.

A surprising LUD speedup would falsify the hypothesis that the prior Pathfinder no-win transfers to this original workload; it would not establish that real hardware bus widening is useful. Conversely, two nulls are insufficient to generalize across all GPU workloads.

## Independent acceptance and kill criteria

Only accept source-pinned runs with simulator completion markers, identical per-kernel counters across two repeats, preserved launch/instruction counts across variants, exact one-parameter config mutations, independent conservation of counters, and matching selected workload identities. Record cycles, L1D/L2 misses, global read/write instructions and log hashes. Reject hardware calibration, RTL speedup and RTX-5090-equivalence claims.

If P1 and P3 survive, retire the bus-width-widening direction for **these two tested workloads**. If P1 fails, require a physically implementable equal-resource comparison, including matched ports/area/timing/electrical checks, before considering promotion. In either case the existing V309 qualification branch and PR remain the sole active research surface; V287 remains retired and V296's earlier physical failures are not overwritten.

## Reproduction

The existing `qv100_dram_buswidth_sweep.py` prepares, executes and audits exact one-option mutations. The independent transfer checker `qv100_buswidth_transfer.py` checks both audit outputs and both original source-selection manifests; the workflow archives the raw logs and checker output.
