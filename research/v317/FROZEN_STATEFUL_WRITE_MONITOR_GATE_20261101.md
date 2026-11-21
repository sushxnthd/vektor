# V317 frozen stateful forwarding and write-observation gate (2026-11-01)

**Status:** preregistered before implementing or simulating the stateful RTL. This is a *necessary correctness component*, not an active/promoted new GPU architecture mechanism.

## Prior failure and hypothesis
The combinational forwarding gate in `forwarding_gate.sv` assumes sticky per-lane dirty bits are supplied by a complete write monitor. Without that monitor, the previous zero-unsafe-admission proof is conditional. Implement a single-entry source snapshot and sticky lane-write observer with conservative same-cycle hazard rejection. The strongest equal-resource reuse-aware baseline receives the same snapshot, write events and grant logic; expected incremental transaction benefit is **exactly zero**.

## Frozen tests and falsifiers
1. Capture a warp/register/bank snapshot with a lane mask and immutable data. Request a captured clean subset: exact masked forwarding permitted. Uncaptured lanes: reject.
2. Same-namespace masked writes dirty only matching lanes, remain sticky across arbitrary further writes and do not revalidate after a value happens to return to its old value. Disjoint writes may preserve unaffected lanes.
3. A write concurrent with a request for its lane must block forwarding **combinationally before the clock edge**. A write concurrent with a new capture must dirty the intersecting captured lanes after the edge, even if capture data happened to equal the post-write value.
4. A capture concurrent with request must block forwarding from the old entry. Reset must invalidate admission.
5. Writes to another warp, register or bank must not dirty the entry.
6. Simulate the stateful module in Icarus and synthesize with Yosys using the same hosted workflow; preserve exact tool logs, SHA, and generic cell/logic-depth evidence. Do not label generic logic as placed area, electrical signoff or throughput.
7. Independently enumerate a two-lane software state machine and compare its admission with a reference history-based oracle; zero unsafe grants required. Require a separate same-information comparator with zero incremental predicted transaction benefit.

## Precommitted decision rule
Any unsafe admission kills this implementation immediately. Even if all correctness checks pass, do not promote forwarding: it has no incremental advantage against a reuse-aware equal-resource baseline. Report register storage, sticky-mask state, broadcast fanout and same-cycle timing as unclosed physical costs. No GPU performance or RTX 5090 claims.

## Scope and noninterference
Keep PR #34 and `research/v317-sass-provenance-gate`; no new architecture mechanism or branch. Leave Kernellum PR #119 unchanged while this urgent primary correctness/physical-cost experiment runs.
