# Frozen four-slot bank-service headroom audit (2026-11-02)

## Motivation and status
The V317 pairwise-versus-compact same-policy comparison failed its frozen physical/materiality gate. **Do not revive V317**. Before implementing any new bank-scheduler architecture, measure the *best possible* same-port combinational grant-count headroom over the compact greedy baseline. The oracle is a **research upper bound, not a proposed mechanism or a GPU throughput result**. Preserve PR #34 and all negative evidence.

## Precommitted design
Four issue candidates, two source-bank operands each, 16 logical banks, two read ports per bank. Every operand consumes one port even if both source indices coincide. All four requests valid for the primary study. Compact greedy admits requests in priority order 0,1,2,3 if adding both operands stays within two ports per bank. The oracle enumerates all 16 subsets and chooses maximum cardinality under exactly the same bank-port constraints; it may drop the head, so it has no implicit age-fairness guarantee.

Measure mean admitted requests per cycle, oracle/greedy ratio, event probability of an oracle improvement, and gain conditional on improvement. Output caps of 2 and 4 are applied **after** bank admission, as optimistic work-conserving service bounds. No finite queues, memory latency, clock degradation, SRAM macros, wiring, fairness, or power are included. Thus even the oracle gain is **not** a guaranteed achievable speedup.

## Frozen predicted-win and predicted-no-win regimes
* WIN: repeat the four requests [(0,1),(0,0),(1,1),(2,2)] with output cap 4. Greedy is predicted to admit 2; oracle 3; gain 1.500000x. This is an adversarial constructed case, not representative workload evidence.
* NO-WIN-A: repeat [(0,0),(1,1),(2,2),(3,3)] with cap 4; both admit 4; gain 1.000000x.
* NO-WIN-B: repeat WIN pattern with shared output cap 2; both admit 2; gain 1.000000x.
* NO-WIN-C: all eight operands use bank 0; both admit 1; gain 1.000000x.

## Unseen and sensitivity regimes, frozen before executing the evaluator
Run deterministic Monte Carlo with 20,000 independent four-request batches per regime and seeds 1103, 2207, 3301 (60,000 batches each), using a separate pseudorandom stream for each regime:
1. Uniform independent operand banks, B=16, cap 4.
2. Uniform independent operand banks, B=4, cap 4.
3. Hot-bank mixture, B=16, bank 0 with probability 0.65 and each other bank with probability 0.35/15, cap 4.
4. The same hot-bank mixture with cap 2.
5. Correlated same-bank operands: with probability 0.70 source1=source0, otherwise source1 is sampled uniformly, B=16, cap 4.
6. Uniform B=16, each request independently valid with probability 0.60, cap 4.

For each scenario report raw counts, mean service, improvement frequency and oracle gain. Holdout audit: independent exact enumerator checks 1,000 separately seeded four-request batches per scenario, and exhaustive enumeration for B=2 with all four requests valid. **Do not change scenarios after observing results**.

## Interpretation and hard gate
If uniform-B16 gain is <1.02x, do not present a generic bank-scheduler throughput advantage. If hot-bank cap2 gain is <1.02x, mark shared-port/output saturation as a predicted no-win regime. Even a large constructed win cannot establish practical value without matched legal RTL synthesis/route, no starvation, fair equal-resource baseline and realistic workload transfer. If oracle gain is small, no implementation can exceed its instantaneous admitted-request count at equal bank ports; a real scheduler may be worse due to area, delay and fairness. The only exact algebraic boundary is E[min(K,M)]/E[min(K,G)] with oracle M, greedy G, output cap K, under the stated independent backlogged batch assumptions. Do not extrapolate this identity to finite-buffer GPU IPC.
