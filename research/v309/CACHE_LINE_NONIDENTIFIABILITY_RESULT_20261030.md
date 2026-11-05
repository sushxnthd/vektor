# V309: sector-count-only throughput inference falsified (2026-10-30)

**Decision:** do not promote a hardware mechanism from the aggregate 32-byte sector counts or the prior synthetic +33.33% conditional roofline. The roofline's arithmetic remains valid under its *assumed* service bytes; the inference from observed sector counts to actual traffic/throughput is not identifiable.

## Prospective test and verification

- [Protocol](CACHE_LINE_NONIDENTIFIABILITY_PROTOCOL_20261030.md) committed first at `9a33dab`, before the executable experiment.
- [Executable experiment](cache_line_nonidentifiability.py), on the same persistent V309 branch and draft PR #26.
- [Hosted independent LRU oracle and sign test #41021234282](https://github.com/sushxnthd/vektor/actions/runs/41021234282): **PASS**, 3,120 independent list-vs-OrderedDict LRU comparisons, seven invalid-input refusals, and ten cache-capacity sensitivity checks.
- An initial hosted run #41021189449 failed solely because the JSON formatter wrote integer zero as `0/1` while the selftest expected `0`; the rational formatter was corrected at `0680950` and the full hosted test passed. No trace construction, frozen prediction or numerical result was changed.

## Identical sector evidence, opposite modeled speedup signs

Both 64-instruction synthetic families have **256 baseline sectors** and **192 changed sectors**, a 25% sector reduction, under the same hypothetical B=8 bytes/cycle, P=1 instruction/cycle and 5% issue-time penalty. The only difference is address topology and reuse. A cold, demand-only, fully associative 4-line LRU with hypothetical 128-byte line fills was modeled.

| Preregistered family | Baseline line fills | Changed line fills | Sector-only predicted gain | Line-fill-model gain |
|---|---:|---:|---:|---:|
| Same 128-byte line, repeatedly accessed | 1 | 1 | +33.333% | **-4.7619%** |
| Four distinct 128-byte lines per instruction, streaming | 256 | 192 | +33.333% | **+33.333%** |

The sign reversal survives cache capacities of 1, 2, 4, 8 and 256 lines. In the same-line family, the 25% reduction in sector count eliminates **no** line fills, and issue overhead causes a regression. In the streaming family, line fills decrease by 25% and memory service dominates. An unchanged-address ideal coalescer reduces **zero** line fills in both cases.

### Compact identifiability statement

Let `S` count per-instruction unique 32-byte sectors and `L(T,C)` count hypothetical cache-line fills of address trace `T` at capacity `C`. The construction gives two pairs of traces with identical `(I,S_before,S_after)=(64,256,192)`, but

`L_before/L_after = 1/1` in one family and `256/192` in the other.

Therefore there is **no universal function of instruction count and sector counts alone** that recovers line-fill demand, or even the sign of the issue-penalized throughput change under this cache model. Any positive boundary law must additionally incorporate reuse/address topology, fill granularity, cache policy, occupancy/MLP and relevant bandwidth/port constraints, with independent calibration.

## Evidence boundaries and next gate

This is a **synthetic falsification**, not V100 cache modeling, not a functionally equivalent address-changing GPU mechanism, not a measured hardware result, and not an unseen Rodinia workload. Real GPUs may fetch sectors and cache lines differently, and memory service is not equivalent to DRAM traffic. The prior V309 aggregate sector interval [1,586,194,1,595,385] remains valid **only conditional on the unverified historical trace producer**; this experiment does not change those counts.

**Kill:** claims that the aggregate sector-only +33.33% sensitivity is predictive of GPU speedup. **Keep:** the sector counts as conditional trace descriptors and the explicit ideal fixed-address coalescer NO-WIN result.

**Next:** obtain source-authenticated memory addresses and matched per-workload cache/DRAM counters or validated cycle simulation. Freeze a new predicted-win and no-win regime before independent workloads. No V287 revival, no RTX-5090-equivalence claim, and no new hardware mechanism promoted. Kernellum PR #119 remains separate.
