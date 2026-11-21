# V317 delayed-write visibility: temporal correctness falsification (2026-11-01)

**Decision: monitor-only forwarding FAILS under nonzero write-event delivery latency; source-authoritative gating is conditionally safe but unimplemented and has no incremental benefit over a same-information baseline.** This extends the existing V317 falsification instrument, not a new GPU mechanism.

## Prospective protocol and method

The frozen protocol [FROZEN_WRITE_VISIBILITY_LATENCY_20261101.md](FROZEN_WRITE_VISIBILITY_LATENCY_20261101.md) was committed at `a222933` before the temporal oracle or holdout enumeration. [write_visibility_latency.py](write_visibility_latency.py) models two independently committed physical write sources, two register lanes, identity matching, requested/captured masks, delivery latencies 0/1/2 cycles and query horizons 2/3/4 cycles. At most one event per port is enumerated, including absent events. A matching physical write can change the value. This is **exact finite semantic enumeration**, not a timing simulator, real GPU workload or power/area result.

The local observer rejects only writes delivered by the query cycle. The independent value oracle rejects all matching physical writes committed by that cycle. A hypothetical **source-authoritative pending barrier** rejects requests while *any* physical write notification is in flight, including unrelated writes. That pending knowledge is not available to the existing V317 RTL and is **not implemented**. A same-information baseline with identical source authority admits the same safe forwards.

## Reproducible exhaustive results

| Query horizon | Delivery lag | Worlds | Unsafe naive grants | Unsafe barrier grants | Safe opportunities blocked by barrier |
|---:|---:|---:|---:|---:|---:|
| 2 | 0 | 5,184 | 0 | 0 | 0 |
| 2 | 1 | 5,184 | 453 | 0 | 675 |
| 2 | 2 | 5,184 | 956 | 0 | 1,204 |
| 3 | 0 | 9,216 | 0 | 0 | 0 |
| 3 | 1 | 9,216 | 579 | 0 | 897 |
| 3 | 2 | 9,216 | 1,208 | 0 | 1,648 |
| 4 | 0 | 14,400 | 0 | 0 | 0 |
| 4 | 1 | 14,400 | 705 | 0 | 1,119 |
| 4 | 2 | 14,400 | 1,460 | 0 | 2,092 |

**86,400 total enumerated worlds.** At horizon 4, lag 1 makes 705 of 5,585 naive grants unsafe (12.62%); lag 2 makes 1,460 of 6,340 unsafe (23.03%). The global source barrier loses 22.93% and 42.87% of otherwise safe opportunities, respectively. These are uniform-enumeration fractions over an intentionally synthetic state space, **not hardware error probabilities or GPU performance estimates**.

Minimal counterexample: capture and request lane 0; port 1 writes lane 0 at the query cycle; notification arrives one cycle later. The observer grants stale data. The source-level barrier rejects it. A dual-port observer alone is insufficient when delivery is delayed without authoritative pending information.

## Predeclared sensitivity law

For a conservative global pending window of `d` cycles and independent per-cycle write-event probabilities `p` on each of two ports:

`P(quiet) = (1-p)^(2d)`.

| Per-port write probability | d=1 | d=2 | d=4 |
|---:|---:|---:|---:|
| 0.05 | 0.9025 | 0.8145 | 0.6634 |
| 0.10 | 0.8100 | 0.6561 | 0.4305 |
| 0.25 | 0.5625 | 0.3164 | 0.1001 |

This is an **availability proxy for a global blackout policy**, not a register-forwarding speedup law. Real traffic has correlations, identity-specific filtering, outstanding queues and capture/recapture costs. Neither write delay nor port-write probability has been measured. The same-information reuse-aware baseline can use the identical barrier, so incremental modeled register-read savings remain **zero**.

## Verification and decision

Six local unit tests passed, including independent exhaustive zero-lag comparison, late-write counterexample, unrelated-lane/namespace opportunity-loss controls, delivered-write rejection and the frozen sweep. The exhaustive barrier result is checked against a separately computed physical-event oracle. The existing V317 audit workflow now runs these tests and generates a source-pinned JSON artifact; hosted success must be checked separately.

```bash
python -m unittest research.v317.test_write_visibility_latency -v
python -m research.v317.write_visibility_latency
```

**Kill:** Do not promote monitor-only V317 forwarding to an integrated GPU design. A trusted, physically delivered write-event watermark or equivalent source-side stall/invalidating protocol is required even for semantic safety. No incremental transaction advantage survives the strongest equally informed baseline, so further RTL cost optimization is not justified without a distinct differential mechanism. Historical V296 physical no-go and V287 retirement are unchanged. No routed electrical signoff, GPU IPC gain, new architecture or RTX-5090 equivalence is claimed. Kernellum PR #119 remains unchanged.
