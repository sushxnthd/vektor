# V298: Frozen MSHR-credit holdouts, positive conditional gate and hard limits

Date: 2026-10-29. Candidate: **dependent-miss credit guard**, distinct from retired RF arbiters V287/V296/V297. **Evidence tier: synthetic discrete-event MSHR simulator only.** Not a GPU throughput result.

## Reproduction and provenance

Protocol was committed at `cfcbbc6436492afe67e514d1874b083786080ee6` **before** the frozen holdout cases were executed. Run from the repository root:

```sh
python research/v298/v298_holdout.py > /tmp/v298_holdout.json
python research/v298/v298_independent_checker.py
```

30,000 cycles per seed, four frozen seeds (211/223/227/229), six regimes, four policies. The holdout script emits per-seed traces and machine-readable summaries. The committed JSON is a compact summary, not a substitute for raw execution. A separate isolated-credit checker passed 4,160 exhaustive (background latency, compute delay) cases; the negative-control and oracle-overreservation checks passed locally. These checks do **not** independently reimplement the full queue simulator.

The earlier exploratory pilot was observed **before** protocol commit and is not prospective evidence. Pilot seeds with background probability 1.0 are effectively one deterministic demand pattern, not four independent stochastic replications.

## Frozen results

Each cell is the **four-seed mean**. Critical metric is time from critical-burst start to final dependent-load return (lower better); background metric is completed background misses per 30,000 cycles (higher better).

| Regime | Work-conserving burst | Guard burst | Guard vs work-conserving critical latency | Guard / work-conserving background | Guard vs fixed-reserve background | Frozen joint gate |
|---|---:|---:|---:|---:|---:|---|
| H1 long background | 253.717 | 93.956 | -62.97% | 96.25% | +28.82% | **PASS** |
| H2 moderate background | 134.940 | 87.516 | -35.14% | 96.98% | +26.97% | **PASS** |
| H3 short background | 99.001 | 92.008 | -7.06% | 97.68% | +32.58% | FAIL, predicted no-win |
| H4 sparse background | 92.379 | 92.066 | -0.34% | 100.00% | 0.00% | FAIL, predicted no-win |
| H5 short chain | 44.799 | 22.659 | -49.42% | 99.49% | +32.83% | FAIL, +13.29% critical latency vs fixed reserve |
| H6 long compute gap | 453.793 | 347.353 | -23.46% | 87.38% | +15.39% | FAIL, background-retention threshold |

**H1/H2 pass all four preregistered joint criteria.** The guard's burst time is 2.13% and 2.96% worse than fixed-reserve, respectively, while retaining much more background work. H3/H4 correctly fail the no-win gate. H5/H6 reveal that a nominal critical-latency win against a weak baseline can still fail the *strong-control* joint objective.

## Mechanistic boundary, not a universal law

For one isolated freed MSHR credit, fixed background service latency `Lb` and dependent-miss compute delay `D`, the maximum *particular refill-induced issue delay* prevented by holding the credit is:

```
delta_issue = max(0, Lb - D)
cost = D credit-idle cycles
```

The exhaustive checker verifies this **isolated two-event schedule identity** for 4,160 combinations. It does not prove a multi-MSHR queue law: alternative free credits, return ordering, request arrival pressure, miss/hit prediction, occupancy and burst length change the outcome. The H3/H4 no-win behavior is consistent with low residual latency/pressure. A predictive multi-MSHR boundary must still be derived and validated prospectively.

## Stronger controller falsification

The deadline-aware controller, which is given the **true future background service latency** in this fixed-latency model, equals the guard on H1/H2 but **dominates it on H6**: 3,334.75 versus 3,198.50 background completions, and 344 versus 347.353 mean critical-burst cycles. This is an *oracle upper bound*, not a physically implementable equal-cost baseline. The guard cannot claim optimality. A real same-information, same-state predictive throttler must be built and compared before a novelty or performance claim.

## Physicality and prior-art stop rules

No RTL, synthesized cell area, CTS, extracted-RC setup/hold, DRC, switching power, energy, cache model, variable DRAM latency, memory return-port contention, occupancy coupling, warp IPC or real GPU traces exist for V298. A scoreboard-visible dependency does not guarantee that its next load misses; false reservations must be modeled. Future work must include false-positive prediction, unknown latency, bandwidth pressure, finite background queues, independent queue checker, strong implementable throttling controls and matched physical synthesis. **If the equal-cost control dominates, or timing/area/traffic erases the joint benefit, retire V298.**

Prior art constrains novelty: Jog et al. ISCA 2013 (DOI 10.1145/2508148.2485951), WaSP 2024 (arXiv:2404.06156), RPAWS 2026 (IEICE), and related GPU resource-pressure scheduling. V298 is **a bounded engineering hypothesis**, not a claimed original scheduling principle.

V287/V296/V297 remain retired; their negative evidence is not rewritten. Kernellum PR #119 and its holdouts are untouched. No RTX-5090 equivalence is implied.
