# V297 temporal strong-control kill: preregistration (2026-10-29)

This protocol is frozen before executing the new independent checker. The sole mechanism remains V297 cooldown-constrained max-pair; max-pair without cooldown is a **strong baseline**, not a second active architecture. This is a **synthetic admission** experiment, not GPU throughput or physical PPA.

## Exact hypothesis and derivation
For each cycle choose one of two three-request patterns, both with three valid requests and exactly two read ports per bank:
- M=1: older request [0,0], younger requests [0,1] and [0,2]. The oldest request is incompatible with either younger request, but the two younger requests fit together. Fixed serial admits 1, unrestricted max-pair admits 2.
- M=0: all three requests [0,0]. Every feasible controller admits exactly 1.

V297 admits 2 on M=1 iff the preceding cycle was **not a rescue**. Its cooldown bit is the preceding rescue indicator, not the preceding motif indicator.

For a stationary first-order two-state Markov motif process with p=P(M=1), a=P(M_t=1 | M_(t-1)=1), stationary rescue probability r solves r=p-a*r, hence r=p/(1+a). Unrestricted max-pair's excess over serial is p, so the **predicted V297 deficit** is p*a/(1+a) admissions/cycle. Expected V297/maxpair ratio is (1+p/(1+a))/(1+p), before clock, area or power. For p=1,a=1 the exact ratio is 0.75. At p=0 both are identical. This law is **not claimed for higher-order processes**.

## Frozen experiments and acceptance criteria
- Seeded Markov regimes: (p,a)=(0.4,0.9), (0.4,0.2), (0.25,0.85), (0.7,0.8), plus p=0 and p=1 absorbing extremes. Generate stationary transitions b=p*(1-a)/(1-p), with b in [0,1].
- Independent deterministic PRNG seeds: 101, 103, 107, 109. Burn-in 10,000, evaluate 200,000 cycles per seed; compare observed candidate, serial and unrestricted maxpair admissions. Acceptance: mean candidate/maxpair ratio within 0.003 absolute of prediction for all nondegenerate Markov regimes; no port violations; deterministic exact p=0 and p=1 checks.
- Negative control: deterministic 2 motif / 1 nonmotif repeating pattern. The Markov formula need not hold; report the error, not just passing cases.
- Strong-control falsification: any predicted advantage over maxpair in this restricted regime is a bug. If mapped maxpair area and feasible timing are no worse than V297, the positive GPU-performance hypothesis is rejected; do not infer physical feasibility from this simulator.
- Preserve code, machine-readable outputs, independent analytic checks and all failed regimes on this branch/PR.

This test isolates the cost of V297's cooldown from unrelated arrival, queue and bank-map effects. It does not generalize to arbitrary dynamic queues.