# V296 phase-synchronized warp admission: prospective falsification and corrected positive law (2026-10-27)

## Verdict
**The IID four-request admission law fails to transfer under cross-warp phase synchronization, even when each request's bank marginals and within-warp operand correlation are unchanged.** A precommitted three-parameter mixture law predicts the generated regimes accurately, but is exact only for the explicitly defined mixture. This is a synthetic predictive sub-law, not a novel hardware mechanism, a V296-vs-serial speedup, or physical signoff.

[Prospective protocol](CROSS_WARP_PHASE_CORRELATION_PREREG_20261027.md) was committed at `0b0f51a7260d91e8c60b16172c19d02716714a3b` **before** any holdout simulation. [Source and two explicit-port accounting implementations](cross_warp_phase_law.py) and [per-seed results](CROSS_WARP_PHASE_HELDOUT_20261027.csv) are committed separately. Local Python self-tests and the independent second event-accounting path passed. Hosted CI of this new script has not yet been verified.

## Mechanistic positive law

For 16 banks, two read ports/bank, four ready requests, a bank-0 hotspot mixture `h`, within-request operand-copy probability `rho`, and batch phase-synchronization probability `s`:

```
p_0 = h + (1-h)/16, p_i = (1-h)/16 (i=1..15)
P_same = rho + (1-rho) sum_i p_i^2
Q_sync = 2 - P_same
Q(h,rho,s) = (1-s) Q_IID(h,rho) + s Q_sync
```

`Q_IID` is the existing exact four-request dynamic program. The synchronized branch repeats one sampled ordered bank pair across all four requests. A same-bank pair consumes both ports and admits one; a distinct-bank pair admits two. The mixture expectation follows by total expectation, with **no fitted parameters**. For any regime with `Q_IID > Q_sync`, `dQ/ds = Q_sync - Q_IID < 0`.

Importantly, changing `s` **does not change any individual request's bank marginal distribution or within-request rho**. Thus `h` and `rho` alone do not identify admission throughput; phase correlation is a necessary extra workload descriptor for this model. It is not assumed that real traces follow this two-mode mixture.

## Frozen holdout results

Each cell uses 30,000 four-request batches; three frozen unseen seeds per regime; 450,000 batches total. All 15 cells passed the preregistered absolute error <=0.035 admissions/batch. The largest error was **0.0064221**. Two distinct explicit-bank event-accounting implementations returned identical admissions for every cell.

| Regime (h, rho, s) | Predicted Q | Mean observed Q | IID-only Q | Interpretation |
|---|---:|---:|---:|---|
| Uniform control (0,0,0) | 3.82272 | 3.82222 | 3.82272 | Negative control: IID recovered |
| Uniform partial sync (0,0,0.25) | 3.35142 | 3.35276 | 3.82272 | IID overpredicts |
| Uniform strong sync (0,0,0.8) | 2.31454 | 2.31592 | 3.82272 | IID overpredicts by ~1.51 |
| Moderate hotspot sync (0.45,0.2,0.65) | 1.94639 | 1.94382 | 2.59316 | IID overpredicts by ~0.65 |
| Heavy hotspot sync (0.8,0.2,0.95) | 1.27661 | 1.27544 | 1.40228 | Correlation effect smaller at saturation |

The preregistered IID falsification threshold of >=0.25 admissions/batch error passed in all six strong-sync/moderate-hotspot cells. The positive-law accuracy gate and exact `s=0` negative control passed.

## Implications for V296's architecture claim

A bank-admission probability is **not** a V296 speedup. The matched serial control can see the same bank pressure, and a scheduler's queues, dependence chains, occupancy, arbitration, physical frequency, register-file traffic, and shared bandwidth still determine throughput. The existing physical-time roofline boundary `G = min(q_candidate/r,M)/min(q_serial,M)-1` remains conditional on separately measured architecture-specific admissions and feasible clock ratio `r`. This test does **not** substitute `Q` for either architecture's measured `q`.

The current physical priority is unchanged: [matched extended density-0.35 experiment #40427986118](https://github.com/sushxnthd/vektor/actions/runs/40427986118) must resolve the optimized serial-control censoring and then achieve zero DRC and extracted timing/electrical closure. This new law cannot rescue a routed failure. Do not open real-workload holdouts or claim RTX-5090 equivalence.

## Reproduction
From repository root:

```bash
python3 research/v296/cross_warp_phase_law.py --self-test
python3 research/v296/cross_warp_phase_law.py --evaluate --output research/v296/CROSS_WARP_PHASE_REPLAY.json
```

The checked-in CSV preserves all 15 observed integer admission totals and the two independent accounting verdicts. This result is an exact statement about a controlled generator, not a proof of novelty in probability theory or a general transfer law for actual GPU warp traces. V296 remains the sole provisional architecture mechanism; V287 retired; Kernellum PR #119 and sealed holdouts unchanged.

## Independent fail-closed CSV replay audit

A separately committed [independent auditor](audit_cross_warp_phase_holdout.py) does **not** import the phase-mixture implementation. It reconstructs every batch from the frozen seed using a distinct cumulative-distribution bank sampler and demand-counter admission oracle, checks all 15 exact integer admission totals in the committed CSV, independently recomputes the frozen formula from the preexisting IID dynamic program, and rejects missing/duplicate cells, changed regimes, altered sample counts, bad pass flags, or threshold failures. Local audit output: `V296_PHASE_INDEPENDENT_CSV_AUDIT_PASS cells=15 max_error=0.00642203`.

```bash
python3 research/v296/audit_cross_warp_phase_holdout.py --self-test
python3 research/v296/audit_cross_warp_phase_holdout.py --csv research/v296/CROSS_WARP_PHASE_HELDOUT_20261027.csv
```

This provides independent event replay, **not** independent physical validation or proof of transfer to real GPU traces.
