# Frozen V317 bank-scaling / physical-clock break-even test (2026-11-03)

## Purpose and evidence tier
Evaluate whether the existing exact two-cycle, four-request, two-read-per-request **clairvoyant ceiling** can survive even a small controller clock penalty as bank count grows. This is a synthetic finite-batch upper bound, **not** a sustained queue, GPU workload, routed timing result, or proposed new architecture. The existing V317 electrical/area falsifications remain binding. Do not promote tail selection or revive V287/V296.

## Freeze before evaluating new seeds
- Ports per bank = 2; issue cap = 2; four valid ordered requests; two cycles; no arrivals; head-preserving first and second cycle.
- Independent uniform bank draws for all eight operand positions. Bank counts B=8,16,24,32. Fixed previously unused seeds 1103, 2113, 3119; 8,000 batches per seed per B. Preserve duplicate operands as legitimate draws.
- Compare oldest-first greedy, conflict-degree heuristic, and exact two-cycle oracle. Exact oracle is an **optimistic nonimplementable upper bound**.
- Evaluate relative oracle gain R=O/G, event probability p=(O-G)/N, average greedy completions g=G/N; verify R=1+p/g.
- Physical sensitivity is conditional: if each isolated two-cycle batch is repeated at the same clock and resources, and the oracle requires fractional clock-period overhead d, the optimistic rate ratio is R/(1+d). This is *not* an RTL delay measurement. Bandwidth cap beta relative to greedy's compute rate yields min(beta,R/(1+d))/min(beta,1); occupancy factor q multiplies numerator's compute term.

## Frozen predictions and falsification
1. B=8 has larger oracle opportunity than B=16, which exceeds B=24, which exceeds B=32. B=32 R-1 < 0.0025.
2. A 0.5% clock penalty (d=0.005) erases the oracle advantage at B=16,24,32. At B=8 and d=0.005, optimistic R/(1+d) > 1 (predicted-win regime). These are *new seeded synthetic regimes*, not new GPU performance.
3. A shared bandwidth ceiling beta=0.95 eliminates any positive oracle throughput gain for all B at zero clock penalty.
4. Test a *candidate asymptotic law* p(B)=k/B^2, fitting k using B=8 and 16 (mean of p(B)*B^2); predict B=24 and B=32 without refitting. Relative prediction error <=25% is a hypothesis, not a guaranteed theorem. Preserve failures.
5. Independently replay the complete frozen sample with a separate oracle implementation; refuse any result with conservation or identity failure.

## Physical decision
Report per-B maximum allowable relative delay overhead d*=R-1 and equivalent picoseconds at an illustrative 2 ns period. Do not treat generic Yosys cell counts (734 versus 260 for degree vs compact greedy) as routed area. Even passing this synthetic ceiling cannot override the prior physical/electrical kill; demand workload-derived bank traces, matched-resource RTL, routed timing, wire/load, power and bandwidth evidence before any architecture promotion.
