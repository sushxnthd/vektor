# V317 frozen two-write-port completeness gate (2026-11-01)

**Pre-implementation protocol.** This extends the existing V317 correctness/falsification instrument on draft PR #34. It does not promote a new GPU architecture, revive V287/V296, or claim throughput improvement. The one-write-port stateful wrapper is explicitly scoped to a complete single write stream; a GPU tile with two simultaneous physical write sources violates that interface contract unless the streams are merged losslessly.

## Frozen tests and predicted outcomes

1. **Adversarial hidden second write:** capture lane 0 at value 0; a second, unobserved physical port writes value 1 to the same warp/register/bank/lane while the first port is idle. The one-port wrapper grants stale value 0. A dual-port observer must reject both combinationally in the write cycle and after the clock. This is an *integration counterexample*, not a defect under the documented one-port contract.
2. **Simultaneous distinct-lane writes:** both ports hit the same cached identity, but different lane masks. Sticky dirty bits must equal the union of the two masks, and the live hazard must reject any requested lane intersecting either mask.
3. **Namespace isolation:** writes to a different warp/register/bank must not dirty or block the cached entry. Each port is compared independently; merging only lane masks while discarding identity is prohibited.
4. **Concurrent capture:** if either port hits the captured identity in the capture cycle, the overlapping captured lanes must be dirty on the next cycle. A clean coherent recapture must restore eligible forwarding.
5. **Coverage:** a trusted coverage_ok=0 suppresses forwarding immediately and poisons the snapshot until recapture. A missed physical write while coverage_ok remains 1 is **not** solved and remains an explicit kill-level integration assumption.
6. **Matched physical proxy:** compare one-port and two-port wrappers at identical lane/data/identity widths (4x8, 8x16, 32x32), same Yosys version and synth -flatten. Report cells, state bits, generic path depth and fanout, never routed timing or silicon area. Do not interpret the one-port design as a functionally adequate baseline for two write ports.
7. **Independent checker:** exhaustive small-domain software oracle over both write masks, identities, requested masks, and capture hazards; independent RTL simulation with directed and exhaustive mask cases.

## Precommitted decision

Any stale grant on a fully observed second-port write is an immediate RTL correctness failure. Any design that requires missing write-event visibility or falsely asserts coverage_ok remains **not physically integrated**. A same-information reuse-aware baseline has access to both write ports and can implement the same safe predicate; incremental modeled read savings remain **zero**. No GPU performance claim can follow from a passing RTL correctness or generic synthesis test. Preserve all prior negative results and keep Kernellum PR #119 unchanged.
