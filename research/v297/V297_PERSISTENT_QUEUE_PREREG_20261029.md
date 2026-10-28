# V297 persistent-queue falsification protocol (frozen before outcomes; 2026-10-29)

## Research question
Does V297's residual ~1% synthetic advantage against rotating serial survive a persistent finite queue with identical exogenous arrivals, issue slots, bank ports, and a common request stream? The prior open-loop study does not model backlog, fairness, or completed work. Do not tune V297 from results.

## Matched contestants
1. V297: greedy priority over the three oldest queued requests, substitute the two younger requests only when greedy admits exactly one, the younger pair fits two read ports per bank, and cooldown is clear; cooldown lasts exactly the next cycle after rescue.
2. Fair rotating serial: identical three-request window and bank/issue resources; cyclic priority 0/1/2 indexed by cycle number. No extra hardware bank port or issue slot.
3. Exhaustive maximal-admission oracle: inspect all eight subsets of the same three-request window, select maximum cardinality, with age-weighted deterministic tie-break. Oracle is an upper bound, not a matched physical implementation.

Each contestant gets a separate queue and consumes the *same* predetermined arrival stream. Jobs carry immutable IDs, arrival times, and two bank operands; bypassed jobs remain queued. Count only completed admissions, not open-loop offered-request acceptance. Capacity 64, arrivals occur before service, overflow drops newest arrivals; drain and delay are reported separately. Warmup 1000, measurement 20000 cycles, seeds 9209/9221/9239/9257; never use holdout seeds to change the policy. No cache/memory dependencies are modeled.

## Frozen regimes and hypotheses
- **uniform16, 2 arrivals/cycle**: V297 must not meaningfully outperform rotating; prediction |throughput ratio -1| < 0.01.
- **motif3, 2 arrivals/cycle**: consecutive jobs cycle through bank patterns (0,0), (0,1), (0,2). Candidate predicts positive advantage only if its rescue mechanism truly reduces head-of-line blocking in persistent queues; no quantitative claim frozen.
- **motif3_burst37, 2 arrivals/cycle**: 37-cycle motif bursts alternating with uniform; predicted no robust win because prior open-loop burst experiment reversed.
- **hot, 2 arrivals/cycle**: every job (0,0), no win predicted.
- **motif3, 1 arrival/cycle**: low demand, no material win predicted.
- **uniform16, 1 arrival/cycle**: low demand, no material win predicted.
- **motif3, 3 arrivals/cycle**: oversubscribed stress; any claimed win must reduce drops or queue delay, not merely grant count.

## Kill criteria
Retire V297 if no persistent-queue regime shows >1% completion advantage against rotating serial **without worse 99th-percentile latency or drops**, or if a claimed gain depends on changing fairness or request semantics. In any case, physical matched timing must preserve the gain; if candidate clock slowdown > the measured workload margin, retire. No GPU performance claim from this model.

## Integrity
Use independently implemented safety checks for all grants and per-bank read counts. Report all regimes, including losses. This is an intermediate synthetic queue model, not a GPU simulator or physical validation. Preserve V296/V287 negative records and Kernellum holdouts.