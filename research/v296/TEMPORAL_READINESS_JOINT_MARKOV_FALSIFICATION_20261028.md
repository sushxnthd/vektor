# V296: temporal-readiness transfer failure of the iid admission law (2026-10-28)

**Evidence tier: exploratory synthetic exact Markov chain and independent direct-index Monte Carlo.** Not a preregistered prospective holdout, measured GPU trace, routed timing result, or V296-over-serial speedup. No parameter fitting was used. This extends, rather than invalidates within-domain, the earlier independent-ready-slot law in `MEMORY_TOKEN_BANK_STATIONARY_LAW_RESULT_20261028.md`.

## Problem and test

The previous exact finite-token law assumes each ready slot is independent with fixed probability `p`. GPU issue readiness can instead share an execution mode across slots and persist for many cycles. We hold the **marginal mean readiness at p=0.5** and vary only correlation.

Synthetic configuration: B=4 banks, S=3 priority slots, P=2 reads/bank, same-bank operand-copy probability rho=0.2, refill r=1 wave/cycle, token bucket K=2. A two-state ready mode has p_low=0.05 and p_high=0.95, equal stationary mode weights, and symmetric stay probability s in {0.5, 0.9, 0.98}. The mode is shared by all slots in a cycle and transitions after each cycle. This is a **small model test** rather than production-scale hardware.

## Exact positive boundary

Let x be post-cycle remaining tokens and m be the current readiness mode. Let Q_{m,t}(k) be the exact probability of k admitted waves in a cycle with mode m and t=min(K,x+r) tokens. Let T_{mn} be the two-state mode transition matrix. Then the joint state (x,m) has transition

```
P[(x,m),(t-k,n)] = Q[m,t](k) * T[m,n].
```

Solve pi P = pi and sum(pi)=1. The stationary admission law is

```
q = sum_(x,m) pi[x,m] * sum_k k * Q[m,min(K,x+r)](k).
```

This law includes within-cycle ready-slot correlation, across-cycle persistence, bank conflicts and finite bandwidth tokens. Replacing p by its mean **does not preserve throughput**, because the service process is nonlinear and tokens couple successive cycles. It reduces to the independent-mode law only under the appropriate independence assumptions; s=0.5 still has *within-cycle* shared-mode correlation.

## Computed falsification and independent check

| Mode stay probability | Incorrect independent-slot p=0.5 prediction | Exact joint-mode prediction | Independent Monte Carlo observations | Max absolute error |
|---|---:|---:|---|---:|
| 0.50 | 0.969303 | 0.788965 | 0.789729 / 0.787786 | 0.001179 |
| 0.90 | 0.969303 | 0.621878 | 0.616693 / 0.621979 | 0.005185 |
| 0.98 | 0.969303 | 0.583736 | 0.592364 / 0.582421 | 0.008628 |

Each Monte Carlo observation uses 150,000 cycles with 10,000 burn-in, seeds 90211 and 90217, independently sampling explicit bank addresses. All six tests meet a 0.025 absolute tolerance; exact joint-chain stationary residuals are <1e-11. At s=0.98, the naive independent-slot model overpredicts the exact rate by **0.385566 waves/cycle**, or **66.05% relative to the exact rate**. This is a model-assumption counterexample, not an architectural throughput advantage.

Reproduce with:

```bash
python3 research/v296/temporal_readiness_joint_markov.py --output /tmp/v296_temporal_readiness.json
```

Machine-readable output: `TEMPORAL_READINESS_JOINT_MARKOV_RESULT_20261028.json`.

## Hard falsification and next test

1. Reject extrapolating the iid-slot law to temporally bursty or shared-mode readiness solely from average occupancy. Do **not** discard the prior law within its stated iid domain.
2. Do not claim V296 outperforms the strongest serial control from this experiment: both have identical modeled admission semantics at equal clock/resources. A positive architectural consequence must come from independently feasible **clock, area reinvestment, energy, or integrated tile** differences, and must survive matched routing.
3. The matched dynamic-RF D4/D8 full-route experiment [#40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436) was in progress at inspection. Both RTL jobs passed, all four physical jobs remained running; no matched feasible result yet.
4. Freeze an external transfer test **before opening traces**: estimate transition persistence and per-mode slot readiness only on a training partition, then predict admissions on a held-out temporal segment. Compare with the iid-mean model and a strong empirical Markov/queue baseline. Do not call synthetic seeds prospective real-workload evidence.

**Architecture decision:** V296 remains sole provisional mechanism; V287 remains retired. No changes to physical constraints, prior holdouts, or Kernellum PR #119. World-class completion gate remains unmet.
