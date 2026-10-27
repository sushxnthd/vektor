# V296 fixed-word RF transfer: preregistered depth falsification (2026-10-27)

**Status before validation:** analytical predictions and acceptance tests frozen. This is a subordinate test of the *existing* V296 pairwise-bank admission mechanism, not a new architecture. The current fixed-word routed result uses **two words per bank** and is not a production SRAM/register-file implementation. V287 remains retired. No changes to physical constraints, RTL, branch, PR, or sealed real-workload holdouts.

## Question and proof obligation
The existing fixed-word RF fabric exposes two *static* words (0,1) from each bank and broadcasts them to at most two accepted reads. A production-depth bank with D>2 distinct addressable words and arbitrary read addresses cannot be functionally equivalent to this fabric: choose an address outside the fixed set and a stored data value distinct from the fixed words. A dynamic two-port reference reads it; the static fabric cannot. This is an adversarial functional counterexample, regardless of area, clock, or traffic.

For a *non-correctness* statistical eligibility sensitivity only, assume two operand word addresses are sampled from a fixed categorical distribution p on D words: sample A~p; with probability rho set B=A, otherwise sample B~p independently. A fixed set S of two static output words covers both requests with exact probability

P_covered(S) = rho * m + (1-rho) * m^2, m = sum_{i in S} p_i.

Because this expression is monotone in m for 0<=rho<=1, the optimal static two-word set contains the two largest p_i. For uniform D, m=2/D. A fully addressable *dynamic* two-port bank covers all valid pairs; this does not assert it has equal physical cost. P_covered is **not** throughput, accuracy, energy, or performance. Even 99.9% coverage does not establish functional equivalence.

## Frozen exact predictions
Use two requests, 2 static outputs, no read-capacity overcommit, D in {2,4,8,16,32}, and these cases (D, rho, mass of two largest words, predicted coverage):
- (2, 0.2, 1.0, 1.0), uniform.
- (4, 0.2, 0.5, 0.3), uniform.
- (8, 0.2, 0.25, 0.1), uniform.
- (16, 0.2, 0.125, 0.0375), uniform.
- (32, 0.2, 0.0625, 0.015625), uniform.
- (16, 0.2, 0.8, 0.672), p0=.55, p1=.25, remaining 14 equally share .20.
- (16, 0.8, 0.95, 0.9405), p0=.90, p1=.05, remaining 14 equally share .05.
- (16, 0.8, 0.75, 0.7125), p0=.50, p1=.25, remaining 14 equally share .25.

## Frozen validation and kill criteria
1. Independently enumerate all ordered pairs for D=2,3,4,8,16,32, verify that any D>2 has an adversarial pair not covered by a two-word static set; demonstrate explicit distinct stored values. D=2 must have complete coverage.
2. Independently enumerate exact weighted ordered pairs for each frozen regime, compare to the formula to 1e-12.
3. On prospective deterministic seeds **927611**, **927613**, **927617**, sample **100,000** address pairs per regime with a separate event-level sampler. Each empirical coverage fraction must lie within **0.012** absolute of the frozen prediction. All failures retained; no seed replacement or threshold tuning.
4. Include a deliberately false baseline that assumes two fixed outputs cover every pair for D>2, and reject it.
5. No full GPU-workload holdouts opened. No routed timing, power, silicon, tile throughput, or 5090-equivalence claims.

**Interpretation gate:** If any D>2 has uncovered valid addresses, kill *fixed-word static readout as a general deep-bank transfer implementation*, not the parent V296 arbitration mechanism. A deep-bank dynamic two-port implementation must independently pass matched RTL, synthesis, extracted timing/electrical checks and equal-resource baseline before any architecture-level claim.
