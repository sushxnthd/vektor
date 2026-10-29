# V299 prospective holdout: phase-specific gain, robustness failure, retire (2026-10-29)

**Decision: RETIRE V299.** This is a reproducible synthetic TLB replacement falsification, not a GPU IPC, power, RTL, PPA, or novel algorithm result.

## Provenance

The frozen protocol was committed as [a2a22d0](https://github.com/sushxnthd/vektor/commit/a2a22d015e7e47647b9550255efc8d0dd464829c) before opening the holdout; the executable simulator was committed as [474b2f5](https://github.com/sushxnthd/vektor/commit/474b2f53fb150a738d8505170747fec6de43abd7) before running it. Pilot seeds 11, 17, 23, 31 were exploratory and excluded. The frozen evaluation uses seeds 503, 509, 521, 523, seven regimes, 20,000 references per seed, five policies and identical exogenous references. Total: **560,000 trace references and 2,800,000 policy-access evaluations**.

An independent reference checks **5,184 exhaustive two-entry victim states**; all matched, and the no-decay mutant disagreed in **1,687** states. The simulator's own deterministic selftest passed. The hosted workflow reproduces all seven regimes and uploads raw per-seed JSON. No physical synthesis was attempted because the candidate failed its predeclared robustness gate.

## Frozen holdout results

The strongest control is selected separately in each regime, minimizing the same non-overlapped weighted-miss proxy, `stall_work = sum(miss_fanout * 100)`. Positive advantage means V299 reduces this proxy.

| Regime | Best simple control | Control stall work | V299 stall work | V299 advantage |
|---|---|---:|---:|---:|
| phase (predicted win) | fanout_lru | 697,850 | 661,825 | **+5.162%** |
| uniform (predicted no win) | lfu | 997,550 | 997,700 | -0.015% |
| skew | fanout_lru | 634,900 | 637,500 | -0.410% |
| scan | fanout_lru | 1,309,500 | 1,404,100 | **-7.224%** |
| reverse fanout | lfu | 5,054,650 | 5,302,675 | -4.907% |
| bursty traffic | fanout_lru | 626,025 | 762,550 | **-21.808%** |
| ample capacity | lru | 4,200 | 4,200 | 0.000% |

The predeclared phase-win and uniform-no-win predictions **passed**, but robustness failed decisively in both `scan` and `burst` (predeclared kill if any negative-control regression exceeds 5%). Do not tune the age bucket or retest these holdouts as prospective evidence.

The four phase seed pairs (V299/control) were 659,400/694,000; 659,400/698,300; 658,200/693,200; 670,300/705,900. Bursty pairs were 716,700/580,600; 830,200/691,400; 762,900/623,100; 740,400/609,000. Thus the phase benefit and burst regression were not driven by a single seed.

## Mechanistic interpretation and bounded predictive law

For a one-victim choice between pages A and B, let `p_A` and `p_B` denote their probabilities of being needed again before the next replacement opportunity, and `F_A`, `F_B` their expected numbers of blocked warp consumers. Under a fixed walk latency `L` and **ignoring overlap**, the expected weighted-miss saving from retaining A rather than B is:

`E[delta stall_work] = L * (p_A * F_A - p_B * F_B)`.

The correct boundary is `p_A F_A > p_B F_B`. V299 uses quantized fanout, frequency and age as an *uncalibrated proxy* for this boundary. It succeeds when the workload's phase changes at a rate compatible with the decay window; it fails when burst autocorrelation makes the decay discard valuable translations, or scans overwhelm the retention decision. This equation is a two-page accounting identity, **not a validated general GPU positive law or a novelty claim**.

## Physical and scientific limitations

- No real GPU memory trace, virtual-address mapping, TLB associativity distribution, translation-cache hierarchy, or multi-level page walk.
- No concurrent page walks, coalesced miss tracking, queue backpressure, memory-level parallelism, or elapsed-time throughput. Summing `fanout * L` may overcount overlapping stalls.
- Metadata access and score computation require gates, wires and timing; no RTL or matched-resource area/clock closure.
- DEPOT (2026, https://arxiv.org/abs/2606.00486) already targets dead-entry GPU TLB misses and burst amplification. MeDiC (2018, https://arxiv.org/abs/1804.11038) addresses memory divergence. Cost-aware replacement is longstanding. Novelty remains unestablished.

## Research decision

**Kill V299 without physical implementation** because a simple same-metadata fanout-LRU control is materially stronger on bursty and streaming regimes. Preserve the frozen results and negative controls; close the draft PR unmerged. V287/V296/V297/V298 remain retired. The next active mechanism must be a different prior-art-audited hypothesis, not an after-the-fact retuning of V299.

Reproduce: `python3 research/v299/v299_independent_checker.py`; `python3 research/v299/v299_tlb_fanout.py --selftest --evaluate`.
