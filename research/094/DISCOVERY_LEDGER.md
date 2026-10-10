# Vektor-094 Discovery Protocol V2 ledger
Date 2026-10-11. Evidence types explicitly separated: Python/C++ software simulation, Icarus RTL smoke tests, generic Yosys synthesis. No physical PPA, GPU throughput or unbounded formal proof.

## World model
- **KNOWN (software model):** final-only retirement, conditional on exactly one FINAL per transaction and no replayed FINAL, had zero false completions in 416 discovery/holdout configurations and 80 new preregistered holdouts; 8,192 bounded software traces passed.
- **KNOWN (software model):** first-beat retirement caused false completions in 313/320 discovery and 90/96 holdout configurations with synthetic extra return beats. Not a real GPU failure rate.
- **KNOWN (software model):** final-only reduced admissions versus the unsafe first-beat baseline in 308/320 discovery and 91/96 holdout cases; mean paired ratios 0.530 and 0.541.
- **KNOWN (software model):** source-side filtering of nonfinal beats improved admissions in 111/320 discovery, 38/96 holdout, and 31/80 fresh preregistered cases; regressions 16/320, 1/96, and 3/80, respectively. Fresh holdout mean paired ratio 1.04079. These are synthetic admissions, not instruction throughput.
- **KNOWN (RTL):** packetizer, coalescer, and final consumer smoke tests passed in GitHub Actions. Generic Yosys cell counts (default configs) 51, 67, and 348. No ASIC area/timing result.
- **BELIEVED:** source-side quiescence plus final-only return is a better starting protocol than fixed callback-time leases when finality can be enforced.
- **CONFLICTING:** reducing return traffic can reduce finite-window admissions in 20 total paired cases. Possible causes include altered allocation phase, cancellation and finite horizons; not resolved.
- **FALSIFIED:** first callback ACK is safe in the presence of delayed duplicate return beats; final-only is safe against duplicated FINAL (64/64 negative-control configurations unsafe).
- **ANOMALOUS:** 16/320 + 1/96 + 3/80 filtering regressions despite reduced return traffic.
- **UNTESTED:** source quiescence proof, cold-reset return flush, multi-producer out-of-order fabric, full RTL formal proof, coherent V-Tile integration, KPX workloads, physical PPA, RTX 5090-class gates.

## 094A: DISCRIMINATION
Mechanism: retire only on unique FINAL. Preregistered prediction: zero false under contract, unsafe first-beat in >=20% pressured configs, one-beat identity, duplicated FINAL counterexample.
Outcome: 0/416 final false, 403/416 first-beat unsafe, 32/32 one-beat identical, 64/64 duplicate-FINAL controls unsafe.
Residual: zero safety residual; throughput/admission cost substantial (mean final/first 0.53/0.54).
Competing explanations: model enforces producer final uniqueness; not proof of real protocol.
Uncertainty: no unbounded RTL safety proof.
Cheapest test: composed RTL bounded formal proof with producer quiescence and reset assumptions.

## 094B: SURPRISE / exploratory, not preregistered
Mechanism: suppress nonfinal beats before return network. Observed 111/320 and 38/96 admission improvements; 16/320 and 1/96 regressions.
Residual: monotonic admissions expectation fails on 17 cases.
Competing explanations: endogenous grants, queueing, cancellation, finite horizon.
Cheapest test: preregister independent holdout.

## 094C: DISCRIMINATION / preregistered independent holdout
Prediction: zero false, >=16/80 filtering improvements, <4/80 regressions; 10/80 minimally guided probes.
Outcome: zero false, 31 improved, 46 ties, 3 regressions; mean ratio 1.04079. Directional thresholds met.
Uncertainty: synthetic workload; source state and NoC costs not included.
Cheapest test: use compiler-derived return traces with explicit finite queue, compare physical source-state cost.

## Bottleneck clustering (087–094)
087 cross-latency starvation; 088 fairness/admissions; 089–091 cancellation/ABA/reset; 092 finite-return callback age; 093 duplicate replay; 094 finality and source coalescing. Promote return-path quiescence, tag ownership and fairness to a shared architectural research target rather than repeatedly optimizing isolated arbiters.

## Adversarial roles
Explorer: final-only plus source coalescing. Skeptic: duplicate FINAL, reset/flush, no source quiescence. Experimentalist: bounded enumeration and independent holdout. Analyst: preserve large admission penalty versus unsafe baseline. Anomaly Hunter: filtering regressions. Prior-Art Auditor: final marking, ready/valid and duplicate suppression are established concepts, no novelty claim. Replicator: independent C++ model 128 seeds/1,152 metrics. Theorist: a finite reused tag is safe only if no older transaction can emit a future retiring FINAL with that tag.

**Single next decisive action:** formally prove the composed source + finite FIFO + consumer under explicit quiescence/reset contracts, then synthesize equal-resource alternatives and test KPX-derived workloads.
