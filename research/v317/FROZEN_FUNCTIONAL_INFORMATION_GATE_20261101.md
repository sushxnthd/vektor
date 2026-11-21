# V317 functional-information gate (frozen before implementation, 2026-11-01)

## Purpose
The previous V317 candidate removes the B-register read from an AB instruction and reports up to 2x synthetic service-cycle improvement. It does not supply a functionally equivalent way to obtain B. Test whether any such gain can survive **program semantics** and an equally informed compiler/forwarding baseline, before another service-law sweep or RTL work.

## Frozen model and predictions
Use 4-bit unsigned values and two distinct operations:
- AB computes `(A + 3*B) mod 16`.
- BC computes `B xor C`.

All combinations of 4-bit inputs are exhaustive. A candidate that deletes B and has no other B-dependent input is deterministic in A alone. Test an explicit two-world counterexample with A=0, B=0 versus B=1. **Prediction:** unequal required outputs; no implementation of the proposed B-deletion interface can be equivalent over arbitrary B.

Check three proposed repairs:
1. Proven `B=A`: compute AB from A only. **Prediction:** equivalent; an equally informed compiler can do the same, so candidate-only read savings are zero.
2. Proven `B=A xor C`: compute AB from A and C with a recomputation XOR. **Prediction:** equivalent; requires C input/read and ALU work, and an equally informed compiler can choose the same transformation. Do not count the new C read as free.
3. Same-register B forwarding from an adjacent BC instruction: BC reads B once, and AB consumes that exact value. **Prediction:** equivalent only when identity and value agree; a reuse-aware baseline can also forward that B. Different register identities must fail an identity-aware admission check even if sample values happen to coincide.

For all repairs, compare resource transactions against the strongest *same-knowledge* baseline; do not treat weaker unoptimized AB as the matched comparator. Report exact exhaustive test counts and an independent two-world impossibility witness. No RTL/physical or measured GPU claim follows from this semantic gate.

## Decision rule
If unqualified B deletion fails equivalence and all explicitly modeled valid repairs are matched by an equally informed compiler/reuse baseline, retire the **current hypothetical B-deletion architecture candidate** as a novel mechanism. Preserve V317's provenance/evaluation instrumentation and draft PR #34. Do not create a new mechanism, branch or PR in this run. A future candidate requires a concrete dataflow path, measurable additional physical resource and strong baseline comparison before promotion.
