# V317 prospective legal-load electrical transfer: passed predictions, discovered asymmetric legality (2026-11-01)

## Source-pinned experiment and integrity
[Frozen protocol](FROZEN_RF_LEGAL_LOAD_TRANSFER_20261101.md) was committed at `2302a1f` **before** the 10-fF and 30-fF experiment. [GitHub Actions #41311785246](https://github.com/sushxnthd/vektor/actions/runs/41311785246) **PASSED** at `dc51d736f62afceb94419696d854a380ed98186d`, with matched Yosys/Nangate45 synthesis, eight OpenSTA load/variant checks, 14 independent synthetic parser/falsification tests, and a source-pinned [raw artifact #13085294419](https://github.com/sushxnthd/vektor/actions/runs/41311785246/artifacts/13085294419). The checker consumes the actual OpenSTA path and max-transition tables; missing or invalid electrical evidence fails closed.

## Frozen predictions: both survived
- **10 fF predicted legal win:** source fixed and pairwise fixed both meet the reported max-transition limit; source arrival **1.23 ns**, pairwise **0.58 ns**. Observed margin **0.65 ns**, exceeding the frozen >=0.40-ns threshold. Worst reported max-transition: source **0.16 ns**, pairwise **0.11 ns**, against 0.20-ns limit.
- **30 fF predicted electrically invalid no-win:** both violate max-transition. Source worst transition **0.24 ns**, pairwise **0.25 ns**, against 0.20-ns limit. Raw arrivals **1.33 ns** and **0.84 ns** respectively are **not legal physical speedups**.

## Exploratory electrical boundary, not a preregistered holdout

| External load | Source fixed arrival | Pairwise fixed arrival | Source max-transition | Pairwise max-transition | Legal comparison? |
|---:|---:|---:|---:|---:|---|
| 10 fF | 1.23 ns | 0.58 ns | 0.16 ns (MET) | 0.11 ns (MET) | Both pass reported slew gate |
| 24 fF | 1.30 ns | 0.75 ns | 0.20 ns (MET, zero reported slack) | 0.21 ns (VIOLATED) | **No: pairwise fails** |
| 26 fF | 1.31 ns | 0.78 ns | 0.21 ns (VIOLATED) | 0.23 ns (VIOLATED) | No |
| 30 fF | 1.33 ns | 0.84 ns | 0.24 ns (VIOLATED) | 0.25 ns (VIOLATED) | No |

**New falsification of unconditional dominance:** At 24 fF the cheaper, faster-cell pairwise implementation is *less electrically admissible* than the source implementation under the same unmended mapping and output load. The source's printed zero max-transition slack is marginal and does not establish robust closure. The earlier 20-fF source and pairwise checks passed, so the sampled pairwise transition boundary lies **between 20 and 24 fF**; the source passes 24 and fails 26 fF. These are discrete sampled statuses, not a proof of monotonicity or an exact continuous crossover.

## Conditional area/timing sensitivity and scope
The **previously** mapped Nangate45 cell areas remain source 798.798 um^2 and pairwise 259.616 um^2 (pairwise/source = 0.325008). At the **legal 10-fF max-transition point only**, the conditional arbiter-cell area-delay product ratio is **0.153256**, not a tile area-delay product. The measured cell-delay advantage of **0.65 ns** is the maximum *extra differential wire/placement penalty* pairwise could tolerate before its isolated grant-output delay ordering reverses, **provided** every electrical/setup constraint remains legal. This is a symbolic headroom inequality, not extracted wire RC.

Because grant decisions and RF port counts are identical, **intrinsic completed service/cycle = 1.000x** at equal clock. No throughput improvement follows from the area-delay ratio alone. A tile-level benefit would require demonstrating that this logic actually limits tile clock or that freed area can be reinvested in performance-critical resources. The rotating/oldest-first fairness alternatives remain necessary strong controls; no new scheduler is promoted.

## Research decision
Retain pairwise fixed as a functionally proven, lower-mapped-area implementation optimization with **limited electrically admissible low-load cell-delay superiority**. **Kill** unconditional delay superiority and all claims based on 24-fF-and-above raw delays. Max-capacitance is **UNVERIFIED** in the pinned legacy OpenSTA, and no placement, routed RC, repaired buffering, power, setup signoff, GPU IPC, or RTX 5090-equivalence evidence exists. The next decisive physical gate is **matched electrical repair** (buffering/resizing/remapping) with max-capacitance and full placed/routed timing checks, followed by integrated tile timing/area. Preserve the existing V317 branch and draft PR; Kernellum PR #119 remains untouched.
