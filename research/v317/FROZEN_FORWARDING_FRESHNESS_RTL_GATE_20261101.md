# V317 frozen forwarding freshness / physical gate (2026-11-01)

**Status: preregistered before new checker, RTL, simulation, or synthesis results.** Continue V317 draft PR #34; this is a **correctness and physical feasibility test of the already proposed same-register forwarding repair**, not promotion of a new architecture mechanism.

## Hypothesis and admission rule

The previous identity-sharing model matches textual register IDs, but equal names do not imply equal values across warps or across intervening writes. Model a buffered producer read with `valid`, physical bank, warp namespace, register index, captured lane mask, captured values, and a per-lane dirty bitmap set by intervening writes. A consumer supplies its warp, register, bank and requested lane mask. A forward is legal only when all identities match, every requested lane was captured, and **no requested lane was written since capture**. The producer must remain live. Dirty bits must be sticky over the producer lifetime or the entry invalidated; clearing them without refreshing data is illegal.

This is a conservative sufficient rule under the explicit assumption that the write monitor sees **every** write to that physical warp/register/lane, including writes from other pipeline paths. A partial write to an unrequested lane must not invalidate clean requested lanes. Masked lanes need not be forwarded. Zero-lane requests are not counted as a saved read.

## Predictions frozen before evaluation

1. **Valid-reuse control:** same warp/register/bank, captured requested lanes, no overlapping dirty lanes -> legal, bit-exact values on requested lanes. Strong equally informed baseline can use identical forwarding, hence **no unique candidate transaction advantage**.
2. **No-win / invalid-reuse control:** same textual register across different warps, or same warp/register with an intervening write to a requested lane -> must reject even when the naive name-only oracle accepts. No unaccounted read may be removed.
3. **Prospective masked transfer:** write to a different lane -> legal reuse of clean requested lanes; write to a requested lane -> reject.
4. **Finite-tag adversary:** a version tag of width `w` wraps after `2**w` writes; stale data can match its old tag. The dirty-bit rule must reject, or a real implementation must prove bounded lifetime/no wrap or full invalidation.

## Tests and physical evidence

- Independent exhaustive two-lane, two-bit-value semantic checker with changed values on dirty lanes and separate warp namespaces. Report false admissions for naive name-only reuse, and zero unsafe admissions for the conservative gate.
- Parameterized synthesizable SystemVerilog admission + forwarded-data mux, with directed and 4-lane mask-sweep simulation.
- Generic Yosys synthesis statistics and combinational longest-path proxy if available. **Generic cell counts are not placed area; a logic-depth proxy is not routed timing or electrical signoff.**
- Strong same-information baseline is entitled to the exact same forwarding predicate, metadata and data path. If the only purported advantage comes from denying it that reuse, kill the incremental novelty. Do not claim physical GPU throughput or RTX 5090 equivalence.

## Kill conditions

Any accepted stale value, unaccounted forwarding source, alias across warp or intervening write, unmonitored invalidation, or absence of incremental benefit over an equally informed reuse-aware baseline prevents promotion. Record negative results and CI status honestly. Do not alter historical V287/V296 evidence or Kernellum PR #119.
