# V309: prospective equality-partition predictive boundary law (2026-10-31)

**Evidence tier: prospective protocol; no unseen outcome examined.** Same active four-slot maximum-cardinality bank-admission mechanism, no additional hardware architecture. This law is an exact mathematical prediction **conditional on eight iid operand-bank draws**; it is not a general GPU performance model. This is classical occupancy combinatorics applied to the V309 arbitration contract, not a novelty claim for partition Möbius inversion.

## Before-outcome mechanism

Four ordered valid requests each make two bank reads, 16 possible banks, two ports per bank. The incumbent grants greedily in slot order; the candidate grants a maximum-cardinality feasible subset with smallest numeric mask tie-break. Let `G` and `M` be grant counts and `p=Pr(M>G)`. Under this restricted contract `M-G in {0,1}`, so `E[M]=E[G]+p`. That identity alone is not predictive.

For iid operand banks with known marginal probabilities `q_b`, define power sums `S_r=sum_b q_b^r` for `r=1..8`. Enumerate all 4,140 equality partitions `pi` of the eight operand positions. For a partition with block sizes `s_1..s_k`, the probability of its **exact** equality pattern is

`P(pi)=sum_{sigma in Partitions({1..k})} prod_{C in sigma} [(-1)^(|C|-1) (|C|-1)! S_{sum_{i in C}s_i}]`.

This is the inclusion-exclusion / Möbius formula for distinct bank labels assigned to the blocks. Evaluate the original greedy and independent exact-max subset oracle once on each canonical partition, then compute `g(q)=sum_pi P(pi)*G(pi)`, `p(q)=sum_pi P(pi)*1[M(pi)>G(pi)]`, and **pre-outcome** `R_issue(q)=1+p(q)/g(q)`. Check `sum_pi P(pi)=1` and `E[M]-E[G]-p=0` numerically. No fitted coefficients, no observed holdout outcomes, no post-hoc bank frequencies.

## Predictions frozen before Monte Carlo outcomes

The model was evaluated analytically on the following **previously unopened** regimes; numerical predictions are disclosed before running their Monte Carlo holdouts:

| Regime | Operand distribution q | Seed | Frozen predicted ratio | Direction gate |
| --- | --- | --- | --- | --- |
| `uniform8` | iid uniform over banks 0..7 | `0x309E` | `1.007648758273677` | <1.01 |
| `hot2` | 95% iid uniform banks 0..1; 5% iid uniform all 16 | `0x309F` | `1.0973483338585934` | >1.07 |

Run 100,000 opportunities per regime using `random.Random(seed)`, all four requests valid. For uniform8 draw eight `randrange(8)` bank IDs per opportunity in slot order (source0 then source1). For hot2 draw one `random()` per operand and then `randrange(2)` if <0.95, else `randrange(16)`. Report sample SHA-256, full (greedy,max) histogram, exact law prediction, observed ratio, absolute error, and both directional gates. Freeze maximum allowed absolute ratio prediction error **0.015** for each regime. These gates are engineering checks, not statistical confidence bounds. Report independent standard error or bootstrap CI in follow-up before claiming transfer precision.

## Workload and physicality boundary

These are synthetic iid bank-address workloads, **not** trace-derived operand distributions. Correlation, source aliasing, bank remapping, invalid slots, scoreboard dependencies, occupancy, queuing, register-file timing, fairness, power and physical routing can invalidate throughput extrapolation. The candidate's optimistic issue-stage gain requires `f_candidate/f_greedy > 1/R_issue` even without downstream issue caps or control overhead; with downstream acceptance cap `B`, replace ratio by `min(B,g+p)/min(B,g)`. The thresholds above imply frequency-retention requirements about 0.99241 (uniform8) and 0.91129 (hot2), before any additional losses. If the compact-greedy matched RTL gate fails, these predictions do not rescue the mechanism.

## Required independent controls

Use a separately implemented per-bank counting greedy and subset oracle for Monte Carlo, not the partition-label evaluator; reject any case with >2 reads per bank, `M<G`, or `M-G>1`. Assert Bell(8)=4140, distribution normalization, and two frozen direction/error gates. Preserve failed controls and all evidence. This protocol is not a claim of architectural novelty, physical speedup or RTX 5090 equivalence.
