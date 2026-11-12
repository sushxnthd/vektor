# V317 frozen parameterized RTL formal-equivalence challenge (2026-11-01)

Committed **before** executing the new formal job. This follows the successful seven-point unseen generic-cell law test; it does not retroactively convert those sampled RTL checks into a proof.

## Frozen test
Run Yosys `equiv_make; equiv_simple; equiv_status -assert` after specializing **both** source modules at these three configurations, with no environmental assumptions beyond binary input bits:

- S=2, B=8: prove both grant bits identical for all valid masks and all bank-identity combinations.
- S=3, B=8: prove all three grant bits identical; this slot count was held out of the initial cost-law fit.
- S=4, B=16: prove all four grant bits identical for the newly parameterized bank-mask and pairwise sources, independently of the prior proof using the original fixed arbiter RTL.

Each proof must include the complete input space, all bank operands, all request-valid patterns, and all output grant bits. Treat a timeout, tool error, or unproven equivalence cell as **inconclusive or failure**, never as PASS. Preserve complete logs and source SHA. The earlier randomized Icarus oracle is a separate evidence tier.

## Frozen decision boundary
- 3/3 full proofs: upgrade only the *parameterized implementation's functional-equivalence* evidence. No workload speedup follows.
- Any inequivalence: preserve a counterexample, fail the equivalence gate and stop interpreting the two implementations as grant-identical.
- Any timeout: report the proof as incomplete and retain the previous sampled evidence tier; do not weaken the claim or alter the frozen configuration list.

No RTL optimization or prediction refit is authorized by this protocol. Mapped timing, wire loads, electrical signoff, power and real GPU IPC remain untested.
