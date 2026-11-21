# V317 frozen write-visibility-latency falsification (2026-11-01)

**Prospective protocol, before implementing the temporal oracle.** This extends the *existing* V317 correctness instrument on draft PR #34. It does not promote a mechanism, revive historical V287/V296, or claim GPU throughput.

## Hypothesis and independent variables

A physically committed register-file write may arrive at a snapshot monitor only after a nonzero delivery latency. A monitor that treats `coverage_ok=1` as proof of contemporaneous completeness can grant a stale snapshot between the physical write and its delayed notification. Test two independent write ports, two lanes, per-port write masks and namespace hits, requested masks, delivery delays d=0,1,2 and horizons H=2,3,4. A write at integer cycle t is visible to the monitor at query cycle H only if t+d<=H. Physical correctness instead depends on **all** writes committed through H. The snapshot precedes all test writes. Assume a write to a requested lane can change its value.

## Predictions frozen before opening the sweep

1. At d=0 the complete two-port predicate must have **zero** unsafe admissions.
2. For d>=1, at least one nonempty requested mask and a physical write in the final d cycles will produce an unsafe admission if `coverage_ok` remains high. A minimal witness must be emitted.
3. A source-authoritative outstanding-event barrier that suppresses forwarding whenever *any* committed event is still in flight must have **zero** unsafe admissions, but this barrier is an **external unimplemented input**. A local monitor cannot infer a missing event from its own history.
4. Compare the barrier's exact eligible grant set to a strongest same-information reuse-aware baseline with the same committed-event authority. Incremental forwarding benefit is predicted to be **zero**.
5. Report both false admissions and conservative lost grant opportunities, not only correctness. Derive a bounded independent-port Bernoulli blackout sensitivity `(1-p)^(2*d)` for a hypothetical d-cycle global pending window; this is an *availability proxy*, not measured GPU IPC.
6. Independently recompute small exhaustive worlds without calling the candidate grant function. Use deterministic tests for late event, other namespace, nonoverlapping lanes, both ports, and no-write controls.

## Stop/kill rule

Any unsafe grant under a supposedly complete, source-authoritative barrier is a correctness failure. A monitor-only gate that is unsafe under nonzero latency cannot be considered physically integrated. Even if the barrier is correct, **no new GPU architecture mechanism** survives without incremental matched-resource performance versus a same-information baseline. Generic RTL, fanout and synthetic availability must never be reported as routed timing or measured throughput.

All code and evidence remain on `research/v317-sass-provenance-gate`; keep Kernellum PR #119 untouched during this primary falsification.
