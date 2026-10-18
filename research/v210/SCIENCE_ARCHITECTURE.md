# V210 science ledger — decisive stronger-control audit

Date: 2026-10-18. **Evidence class: synthetic software simulation only.** The predeclared V209 dynamic unseen seed was 271828; 10,000 cycles per workload. Same four issue slots, sixteen banks, two reads/bank, and zero added RF ports/buffers. A simpler immediate-backup control was compared with V209's deferred two-pass fallback and the existing greedy control.

| Synthetic class | Greedy grants | Deferred grants | Immediate-backup grants | Deferred vs immediate |
|---|---:|---:|---:|---:|
| Compute, hot banks | 21,288 | 24,400 | 24,554 | -0.62719% |
| Compute, uniform | 37,809 | 39,655 | 39,706 | -0.12844% |
| Memory, sparse | 23,563 | 23,563 | 23,563 | 0% |
| Divergent, hot banks | 24,829 | 27,336 | 27,488 | -0.55297% |
| Divergent, uniform | 37,422 | 38,706 | 38,727 | -0.05423% |

The simpler one-pass immediate-backup control beat or tied the two-pass deferred candidate in every frozen synthetic class. Although immediate backup can lose to greedy in particular same-state counterexamples, this did not translate into an aggregate loss in the tested dynamic distributions. Deferred fallback retains the exact per-state grant-preservation property against greedy; that property alone is not a throughput/area/timing Pareto advantage against a stronger control.

**Frequency boundary:** For deferred to beat immediate in issued waves per second, it would require f_deferred/f_immediate > 1.006311 in compute-hot, >1.001286 in compute-uniform, >1.005560 in divergent-hot, and >1.000543 in divergent-uniform. In memory-sparse it has zero issue advantage. No frequency or timing measurements exist; these ratios are necessary thresholds derived from the modeled grant counts, not measured feasibility.

**Physical gate failed to execute:** The available local environment lacks Icarus, Yosys and OpenSTA; attempts to commit executable RTL were rejected by repository safety checks. Existing Actions on the inherited branch do not exercise V209/V210. No RTL simulation, mapped synthesis, clean cap/slew, matched STA, wire/load sensitivity or power measurements were produced.

**SCIENCE decision:** Retire V209/V210 as the active kernel. This is an architecture-selection rejection under a stronger equal-resource control, **not** a proof of electrical failure or a scientific claim that all deferred schedulers are inferior. The former V153/V156 FP32 cutset remains retired and electrically unqualified.

**ARCHITECTURE decision:** Retain the current Vektor issue controller on main. Do not integrate two-pass fallback. Next active research must test a distinct, positive, architecture-relevant bottleneck law with a credible physical discriminator; do not resume this kernel merely to refine modeled gains. The hourly automation remains enabled.
