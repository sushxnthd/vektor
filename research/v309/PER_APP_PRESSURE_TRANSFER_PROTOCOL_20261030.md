# V309 per-application sector-pressure transfer and cache-attenuation falsification protocol (2026-10-30)

**Pre-analysis freeze.** This is a workload-level sensitivity / falsification, not a promoted GPU hardware mechanism. Preserve the sole V309 branch and draft PR #26; do not revive V287/V296. Archive producer remains unverified. The 11 Rodinia workloads have been explored already and are **not prospective holdouts**.

## Immutable evidence and extraction

Use only SHA-256 `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1` V100 Rodinia trace archive. Get each application's active dynamic instruction count from `v100_sass_profile.profile` and its source-conditional sector lower/upper envelope from unchanged `sector_antichain_full_audit.scan`. The previous targeted branch-bound refinement affects one BFS row by eight sectors; for this experiment use the unchanged, slightly wider per-app antichain envelopes to avoid undocumented per-app correction. Fail closed unless all 11 names match, global active rows equal 3,937,565, sector interval equals [1,586,186, 1,595,385], and per-app counts sum to global totals.

## Model, analytic prediction, and frozen regimes

For application j, I_j active instructions, S_j sectors, P=1 assumed issue instruction/cycle, B assumed service bytes/cycle, a in [0,1] fraction of sectors actually reaching a hypothetical limiting service resource, r hypothetical fraction of *those* sectors removed by an unimplemented layout transformation, h=1/20 issue-time penalty:

C_j = min(P/(1+h), B I_j / [32 a S_j (1-r)]), with zero-memory-pressure limit defined as P/(1+h).

Baseline sets r=h=0. For a>0, x_j=32 a S_j P/(B I_j). Strict positive gain is possible if and only if r>0 and x_j>1+h. This predicts a cache/traffic attenuation break-even a_crit=(1+h) B I_j/(32 S_j P). For a<=a_crit, even a perfect reduction cannot win against the issue ceiling. This law is conditional on the simple two-resource service model, not a GPU law.

Freeze r=1/4, h=1/20, P=1. Evaluate B=8 and B=32 service bytes/cycle at a=1, 1/2, 1/4, 1/8. Strongest ideal equal-resource fixed-address coalescer has r=0, h=0, hence zero gain. Costly coalescer r=0, h=1/20 cannot win. Report per-app sector envelopes, exact-rational gain intervals, robust WIN / robust NO_WIN / AMBIGUOUS classifications, cache-attenuation thresholds, and pooled-versus-application disagreements. Do not hide no-win cases.

## Independent falsification and stop criteria

Independently compute total service time T=max[I(1+h)/P, 32 a S(1-r)/B] and IPC=I/T. Verify both envelope endpoints, all parameter cases, and analytic sign against time oracle; test monotonicity, edge cases, invalid fractions, and sum conservation. Do not call a synthetic sign test an unseen workload validation. If the model suggests a fixed-address coalescer can win, fail the experiment. No new hardware mechanism qualifies without validated counters or cycle simulation, matched resource/area/timing and real transformation semantics.
