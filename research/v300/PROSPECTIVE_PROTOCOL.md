# V300 prospective protocol — release-aware sector-fill scheduling

Frozen before the first scored run: 2026-10-29. No result-dependent tuning is allowed.

## Mechanism
A single pending cache line has four outstanding 32-byte sectors and eight resident warps, each waiting for a nonempty subset of those sectors. One sector can be returned per cycle; all sectors are eventually returned. A wakeup occurs when all sectors requested by a warp have arrived. V300 evaluates all ordered first-two-sector choices (12 possibilities), then greedily orders the remaining sectors by *current immediate wakeups*, followed by *remaining waiting fanout* and ascending sector ID. It chooses the complete candidate with minimum sum of warp wakeup cycles, tie-breaking lexicographically. The two-step enumeration is a bounded, potentially costly hardware hypothesis, **not** an offline omniscient full-permutation scheduler.

## Comparators
1. Fixed ascending sector order (weak diagnostic).
2. Fanout-first greedy (strong simple baseline).
3. Shortest-remaining-weighted greedy (strong simple baseline): maximize sum of 1/(number of outstanding sectors) for each waiting warp touching the sector; exact rational comparisons.
4. Immediate-unlock-first greedy (strong simple baseline).
5. Full 24-permutation oracle (upper bound; not a deployable equal-resource comparator).

All comparators receive identical demand masks, ports, and sector data. No future arrivals are used. At this stage all eight warp requests are simultaneously visible; variable arrivals and fairness are out of scope.

## Prospective populations
Use Python random.Random seeds 300101, 300103, 300107, 300109, and 300113, with 1,000 independent line-fill episodes per regime per seed.
- H1 predicted win: mixture of two-sector common dependencies and singleton waiters, 8 warps, 4 sectors; construct three pair-demand warps, three singleton warps, and two uniformly sampled nonempty demand masks, then uniformly permute sector labels.
- H2 predicted no-win: eight independently uniformly sampled singleton sector requests.
- H3 independent random masks: each warp draws a uniformly random nonempty 4-bit mask.
- H4 high overlap: each warp requests a common randomly selected two-sector mask with probability 0.75, otherwise a singleton.
- H5 sparse active warps: two random nonempty masks and six zero/inactive masks.

## Metrics and hard kill criteria
Compute wakeup cycle for each active warp, total wakeup cycles, mean, maximum and sector service count. Compare V300 against the **best baseline chosen per regime from the three strong greedy controls**, not just fixed order. Primary survival requires >=5% reduction in mean wakeup latency on H1, <=2% regression on H2, and no >5% mean regression in H3/H4/H5. No use of opened holdout to change thresholds. Even if this passes, the mechanism is NOT physically credible until equivalent RTL, matched Nangate45 synthesis, placement/routing, timing/electrical, equal-state cost and tile-level validation pass.

## Positive-law hypothesis
For the simple four-sector motif with m warps waiting on one singleton A and n warps waiting on two common sectors B,C, with one unused sector D, A-first completion cost is m+3n, while B,C-first cost is 3m+2n. The A-first benefit is 2m-n cycles; thus its sign changes at n=2m. This is an *exact motif identity*, not a general performance law. V300 must independently predict a boundary on unseen mixtures before a positive research claim.

## Novelty boundary
Critical-word-first, early restart, sector caches, dependency-aware scheduling, and shortest-remaining-first are prior art. The proposed bounded two-step release objective is not claimed novel without a complete literature and patent audit. Any advantage against a weak full-line baseline is inadmissible.

Prior-art starting points:
- WaSP (2024), https://arxiv.org/abs/2404.06156
- Blackwell microbenchmark characterization (2025), https://arxiv.org/abs/2507.10789
- Gou and Gaydadjiev, elastic GPU bank-conflict pipeline (2013), https://doi.org/10.1007/s10766-012-0201-1

Evidence tiers: exact small-graph model -> prospective synthetic holdout -> independent checker -> RTL -> mapped synthesis -> extracted-RC physical -> workload integration. No GPU speedup or energy claim at synthetic tiers.
