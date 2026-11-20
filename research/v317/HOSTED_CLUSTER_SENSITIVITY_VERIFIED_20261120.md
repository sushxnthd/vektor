# Hosted V317 development cluster sensitivity verification — 2026-11-20

## Provenance
- Branch: `research/v317-sass-provenance-gate`; existing draft PR #34.
- GitHub Actions: https://github.com/sushxnthd/vektor/actions/runs/44759235696
- Head SHA tested: `9ead5a0b5f6cb95f00a0ebc2dfe75ca8f6c97503`.
- Job ID: `136367023379`; completed successfully at approximately 15:03 UTC.
- Checked-out-source sensitivity step and source-digest step both succeeded. Source SHA-256 for `rotating_scan_cluster_sensitivity_20261120.py`: `f6a26658cf1dd778fd9f309914a9ff14134a0896a7fb505292448da13f06a37f`.

## Development-only results (four independent seed clusters, 60 correlated cells)
- Full development replay: geometric-mean throughput ratio `0.999934767939798`; minimum `0.998367968664998`; maximum `1.001493103284827`.
- Seed-level geometric means: `20261121: 1.000009115360`, `20261122: 0.999919909597`, `20261123: 0.999751245871`, `20261124: 1.000058828344`.
- Leave-one-seed-out geometric means: `0.999909986695`, `0.999939720770`, `0.999995949449`, `0.999893417892` respectively.
- Regime geometric means: hot65 `0.999662234099`; hot85 `0.999992553204`.
- Arrival examples: 1.5 `0.999912274051`; 2.0 `0.999821259560`; burst `0.999800584715`.
- Exhaustive four-cluster bootstrap descriptive 2.5/97.5 percentiles: `[0.9998157070086642, 1.0000339715432807]`. This is a descriptive resampling range with only four seed clusters, **not** a calibrated population confidence interval.
- Maximum seed geometric mean `1.0000588283442255`, far below the preregistered `1.02` materiality threshold.

## Interpretation and limits
The checked-out simulator and independent accounting regressions passed in the same hosted job: 12 periodic comparisons, 8 paired-trace checks, structural classification, and 60-cell numerical replay. The tested policy is an alternating middle-slot priority policy, **not** a full rotating-priority arbiter. This is a durable negative development result for that policy, not evidence against every scheduler. Reserved prospective holdout seeds remain unopened.

**NO-GO:** No development headroom to justify physical implementation. No new RTL synthesis, electrically legal route, matched PPA, SRAM integration, power measurement, or GPU IPC claim is supported by this audit. V296/V317 remain current; V287 remains historical. Preserve the single-mechanism gate; require a separately justified, preregistered candidate and equal-resource finite-buffer headroom before physical escalation.
