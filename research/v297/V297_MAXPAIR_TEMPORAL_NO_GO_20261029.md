# V297 cooldown loses to an equal-port maximum-pair control: independent temporal falsification (2026-10-29)

**Status:** Negative result. Local Python run completed against the prospectively frozen protocol at `V297_MAXPAIR_TEMPORAL_BOUNDARY_PREREG_20261029.md`. Machine-readable summary and runnable independent script are committed. Hosted reproduction is not yet confirmed. **Synthetic fixed-input admission only; no physical or GPU-performance claim.**

## Mechanistic result
Both controllers have three request candidates, two issue slots, and two register-file read ports per bank. The blocker motif has request bank pairs `[0,0], [0,1], [0,2]`: greedy age priority can issue only the oldest, while maximum-pair issues both younger requests. Nonmotif all-hot `[0,0], [0,0], [0,0]` admits only one request. All selected bank accesses are checked for <=2 reads/bank.

Let `p` be the stationary blocker probability and `a` the Markov probability that a blocker follows a blocker. For V297, rescue triggers a one-cycle cooldown, so the exact stationary rescue rate under first-order Markov motifs is `r=p/(1+a)`. The unrestricted maximum-pair control rescues every motif, at rate `p`. Therefore the **predictive strong-control deficit** is `p*a/(1+a)` admissions/cycle, and V297/maxpair admissions ratio is `(1+p/(1+a))/(1+p)`. This is not a universal law for periodic/higher-order motifs or dynamic queue feedback.

## Frozen holdouts (four independent seeds, 200,000 measured cycles each)

| p | a | Predicted V297/maxpair | Observed | Absolute error |
|---:|---:|---:|---:|---:|
| 0.40 | 0.90 | 0.864662 | 0.865066 | 0.000405 |
| 0.40 | 0.20 | 0.952381 | 0.952583 | 0.000202 |
| 0.25 | 0.85 | 0.908108 | 0.908275 | 0.000167 |
| 0.70 | 0.80 | 0.816993 | 0.817191 | 0.000198 |
| 0.00 | 0.00 | 1.000000 | 1.000000 | 0 |
| 1.00 | 1.00 | 0.750000 | 0.750000 | 0 |

No modeled read-port violation. The frozen two-on/one-off periodic negative control has actual rescues 0.333333/cycle against the Markov prediction 0.444444/cycle, absolute error 0.111111. The Markov law is **falsified outside its declared assumptions**.

## Decision boundary
The stronger unrestricted max-pair control can issue more than V297 even before accounting for clock, area or power. In these fixed-input regimes, V297 has no positive admission claim against max-pair. This **does not prove dynamic-queue dominance** because selection changes future requests; and it does not establish physical timing, hold, DRC, energy or integrated GPU throughput.

If the ongoing five-way pinned Nangate45 comparison confirms unrestricted max-pair is no worse in mapped area and a matched physical test confirms feasibility at equal or higher clock, retire V297. Do not replace the max-pair baseline with a weak dynamically indexed rotating controller. Preserve V287 and V296 as retired.

Reproduce locally with `python3 research/v297/v297_maxpair_temporal_boundary.py`; compare to `V297_MAXPAIR_TEMPORAL_BOUNDARY_SUMMARY_20261029.json`. This study used no paid compute. Kernellum PR #119 and prospective holdouts were not touched.
