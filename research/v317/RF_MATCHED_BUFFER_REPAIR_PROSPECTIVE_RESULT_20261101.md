# V317 matched electrical output-buffer repair: both frozen predictions pass (2026-11-01)

## Source-pinned experiment
The [frozen protocol](FROZEN_RF_MATCHED_BUFFER_REPAIR_20261101.md) was committed at `11e49c9` **before** any buffered STA run. The implementation, tests, and workflow were committed through `a87fca6`. [GitHub Actions #41316524960](https://github.com/sushxnthd/vektor/actions/runs/41316524960) **PASSED** all steps: pinned Nangate45 Liberty, independent unit tests, two matched Yosys-mapped cores, 60 OpenSTA timing/electrical runs (2 cores x 6 drive configurations x 5 loads), independent parser and frozen-prediction audit. The [raw source-pinned artifact #13087327160](https://github.com/sushxnthd/vektor/actions/runs/41316524960/artifacts/13087327160) contains mapped netlists, synthesis logs, generated wrappers, 60 raw STA reports, independent JSON and source SHA. No RTL grant policy or bank-port capacity was changed.

## Frozen predictions: BOTH survived
1. **24-fF repaired-win**: the unbuffered pairwise implementation violates max-transition (0.21 ns against 0.20 ns), but adding identical four-output BUF_X1 stages to both designs restores reported max-transition legality. Pairwise worst output arrival **0.59 ns** vs source **1.26 ns**, a **0.67 ns pre-route cell-delay margin**; pairwise mapped core+buffer area **260.414 um^2** vs source **785.498 um^2** (66.85% less). Both have reported worst max-transition slack >=0.04 ns. BUF_X1 is the *minimum sampled common legal repair* at 24 fF. At BUF_X2, delay is 0.57 vs 1.24 ns and areas 261.478 vs 786.562 um^2.
2. **10-fF no-win for oversizing**: pairwise BUF_X16 delay **0.64 ns** is slower than pairwise unbuffered **0.58 ns** (by 0.06 ns). Larger drivers are not universally faster. Both are reported max-transition legal at 10 fF.

## Matched load/drive sensitivity

| Output load | Unbuffered legality (source/pairwise) | Minimum sampled common legal buffer | Source delay at that drive | Pairwise delay at that drive |
|---:|---|---|---:|---:|
| 10 fF | pass/pass | none | 1.23 ns | 0.58 ns |
| 24 fF | pass/**fail** | BUF_X1 | 1.26 ns | **0.59 ns** |
| 30 fF | fail/fail | BUF_X1 | 1.28 ns | **0.61 ns** |
| 60 fF | fail/fail | BUF_X1 | 1.35 ns | **0.68 ns** |
| 100 fF | fail/fail | BUF_X2 | 1.33 ns | **0.66 ns** |

At 100 fF, BUF_X1 still violates max-transition for **both** implementations (0.24 ns vs 0.20 ns); BUF_X2 passes for both (source 0.16 ns, pairwise 0.12 ns). BUF_X8 at 100 fF improves pairwise delay to 0.61 ns and source to 1.26 ns but increases buffer area. This is a measured **pre-route** drive/area/timing frontier, not routed closure.

## Area accounting caveat
This run independently summed the Nangate45 Liberty areas of instantiated cells in its mapped netlists: **782.306 um^2 source** (731 cells), **257.222 um^2 pairwise** (200 cells), before buffers. Four BUF_X1 instances add **3.192 um^2** to each; BUF_X2 adds **4.256 um^2**. The base areas differ from an *earlier* mapped-area snapshot (798.798/259.616 um^2); the cross-run discrepancy is **not yet reconciled** against the corresponding Yosys `stat` logs and mapping versions. Use the within-run, identically mapped source/pairwise comparison for this experiment, and do not silently combine absolute areas across runs. No placed area, wire area, or power is claimed.

## Predictive electrical boundary (bounded)
For each core `k`, drive `b`, external load `L`, the matched experiment measures
`D_k(b,L) = D_core,k(C_in(b)) + D_BUF,b(L)` under ideal wires, with an independently checked max-transition admissibility condition `S_k(b,L) >= 0`. Because the *same* buffer is applied to each core, their area difference remains the measured mapped-core difference of **525.084 um^2** at every matched drive in this run. The minimum sampled legal buffer is a load-dependent step function over these five loads, **not** a continuous or routed law. An additional differential wire/placement penalty greater than the observed **0.67 ns** at 24 fF would erase the isolated delay ordering, even if electrical constraints remain legal. This is a conditional budget, not evidence of actual routed delay.

## Scientific decision and hard limits
**Retain** pairwise bank-credit as a functionally equivalent, electrically repairable, lower-cell-area fixed-priority implementation with a substantial *isolated pre-route* timing advantage under the sampled matched loads. **Reject** any inference of higher GPU completed-service throughput: grants and physical bank ports are identical, so intrinsic scheduling service at equal clock remains **1.000x**. The strongest fairness controls (rotating priority and oldest-first) remain necessary in any throughput claim; this experiment does not establish novelty.

The following are **UNVERIFIED**: max-capacitance signoff, internal/IO wire parasitics, place-and-route, electrical repair under extracted RC, actual setup/hold timing closure, power, RF integration, tile critical-path relevance, matched tile-area throughput, real workloads, and any RTX 5090 equivalence. The next decisive experiment must run actual placement and routed RC with a matched tile-level budget and independently compare clock-limiting paths; if savings do not affect tile timing/resource replication, kill any performance claim and retain only the implementation-area result. Preserve one branch, draft PR #34, and Kernellum PR #119 without interference.
