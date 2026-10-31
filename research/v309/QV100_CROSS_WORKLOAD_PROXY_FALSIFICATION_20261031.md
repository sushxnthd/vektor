# V309: Prospective rank-two QV100 counter-proxy falsification (2026-10-31)

> **Independent acceptance update, 2026-10-31.** The previously pending source-pinned replay has now passed the complete hosted audit: [GitHub Actions #41126948686](https://github.com/sushxnthd/vektor/actions/runs/41126948686), [raw archived evidence #13011207568](https://github.com/sushxnthd/vektor/actions/runs/41126948686/artifacts/13011207568). Both original workloads passed per-kernel replay conservation, semantic equality across two repeats, and the independent cross-workload falsification checker. The LUD-64 figures below are therefore **independently accepted simulator counters**, no longer provisional. This supersedes only the earlier pending-audit wording below, which is retained as historical provenance. No physical architecture, DRAM-byte or hardware-speedup claim follows. A separately preregistered LUD bus-width intervention is now running; its results are not included here.


## Decision and evidence tier

**Do not use L1D miss count as a stand-in for L2 miss count or off-chip memory demand.** The original rank-two Rodinia workload was frozen before the simulator was run. Its first hosted QV100-SASS replay completed twice, but the host-side independent audit failed on a filesystem ownership error, **not on a numerical disagreement**. This document preserves the negative result at the correct provisional evidence tier. A code fix and independent comparison have been committed; the result is not accepted until a new hosted run passes.

Original hosted attempt: https://github.com/sushxnthd/vektor/actions/runs/41122497673
Original raw artifact: https://github.com/sushxnthd/vektor/actions/runs/41122497673/artifacts/13010190211

## Prospectively selected workload comparison

The selection rule is rank two among complete original command lists, ordered by uncompressed bytes and lexical tie. Rank one remains Pathfinder; rank two is Rodinia LUD-64. No configuration change, performance-based cherry-picking, or new architecture mechanism is involved.

| Source-pinned QV100-SASS output | Pathfinder (rank one; previously independently audited) | LUD-64 (rank two; first replay provisional) |
| --- | ---: | ---: |
| Kernel launches | 4 | 10 |
| Simulated cycles | 28,717 | 127,309 |
| Simulated instructions | 1,059,640 | 418,884 |
| Reported L1D cache misses | 3,534 | 2,048 |
| Reported L2 cache misses | 129 | 0 |
| Reported global reads | 3,021 | 2,048 |
| Reported global writes | 625 | 1,780 |

Both LUD replays returned a completion marker and identical reported summary counters. The raw logs have different hashes; semantic identity requires independent per-kernel audit. The original independent audit failed with `PermissionError: [Errno 13] Permission denied: 'v309-second/evidence/independent-counter-audit.json'` because the Docker container wrote the directory as root. Commit `6c7e31c` restores runner ownership after Docker and before host-side audits.

The L2-to-L1D **reported counter ratio** is 129/3534 = 0.0365 for Pathfinder and 0/2048 = 0 for LUD. **This is not an L2 miss rate**: L1D misses and L2 misses need not count identical requests, and neither count establishes DRAM reads/writes or bytes. In particular, the zero L2 miss counter is not evidence of zero off-chip traffic, because writes and other traffic can exist.

## Independent falsification check

`python3 research/v309/qv100_cross_workload_counter_falsification.py --selftest`

Once both independent audit JSONs exist:

```sh
python3 research/v309/qv100_cross_workload_counter_falsification.py \
  --first v309-legacy/evidence/independent-counter-audit.json \
  --second v309-second/evidence/independent-counter-audit.json \
  --out v309-legacy/evidence/cross-workload-counter-falsification.json
```

The checker conserves cumulative counters across per-kernel increments, refuses duplicated workload identities and hardware claims, and includes eight negative controls. The CI workflow executes it only after both full per-kernel audits pass.

## Consequence for architecture research

An L1D-miss-only predictor cannot establish an L2-miss or off-chip bottleneck on these two source-pinned workloads. This is a **proxy falsification**, not a validated performance law or proof that a proposed architecture is ineffective. The next architectural gate is still a single implementable mechanism versus an equal-resource alternative, with matched RTL timing/area/electrical evidence, then workload-level cycle/traffic consequences and prospective unseen tests. No RTX 5090-equivalence or hardware speedup is claimed.

Do not promote V287 or V296 merely because this audit succeeds; preserve the currently active V309 branch/PR and all historical negative evidence.
