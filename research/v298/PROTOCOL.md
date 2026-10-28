# V298 prospective protocol (2026-10-29)

## Candidate and scientific status

V298 is **dependent-miss credit guarding**, a *provisional* MSHR admission mechanism, not a demonstrated GPU improvement. It is the sole new active Vektor mechanism after V287/V296/V297 were retired. The hardware concept is one credit-hold bit: when a scoreboard-visible critical miss returns and its dependent miss is expected after a known compute interval D, do not refill the last available MSHR with background traffic before the dependent miss becomes ready. The next dependent miss uses the held credit. **Do not predict future burst arrivals or use unknown future memory return times.** If an MSHR is already full at the beginning of a burst, the first critical miss may stall.

This is a synthetic MSHR experiment, not integrated GPU IPC. Four MSHRs, one miss admission per cycle, critical-first issue, serial critical load chain, finite background arrival queue, no eviction or response-port contention. All policies see identical arrival traces. Existing work on MSHR-aware scheduling and warp prefetch/throttling is strong prior art; algorithmic novelty is **unestablished**.

## Pre-existing exploratory pilot (NOT prospective evidence)

Before this protocol was committed, a 30,000-cycle deterministic pilot compared four policies on five hand-picked workloads. The full pilot must be labeled exploratory, even if results are reproduced. The policy can improve critical-burst completion under saturated long-latency background traffic, at the cost of some background completions; the deadline-aware oracle sometimes dominates it. Seeds with background arrival probability 1.0 do not constitute independent stochastic replicates.

## Strong controls

1. **Work-conserving critical-first:** priority to ready critical miss, otherwise fill any MSHR with background.
2. **Fixed one-credit reserve:** background cannot use the last MSHR, even outside critical phases.
3. **Deadline-aware oracle upper bound:** knows background service latency and next critical ready time. Not an implementable equal-cost control when DRAM service time is unknown. Must not be used to claim an unfair candidate win.
4. **Independent reference checker:** must validate MSHR conservation, no duplicate critical issue, finite chain dependencies, and that the oracle is not mistaken for a feasible GPU baseline.

## Frozen holdouts, before execution

Four unseen seeds per regime: 211, 223, 227, 229. Each run: 30,000 cycles; M=4; critical miss latency 8. Holdout parameters (background latency Lb, background arrival probability q, burst gap G, chain length C, compute delay D):

- H1, predicted win: (32, 0.30, 240, 8, 4)
- H2, predicted win under lower pressure: (24, 0.18, 180, 8, 3)
- H3, predicted no-win: (8, 0.50, 240, 8, 4)
- H4, predicted no-win: (32, 0.025, 240, 8, 4)
- H5, predicted fragile/short-chain: (32, 0.30, 240, 2, 4)
- H6, predicted oracle advantage: (32, 0.50, 240, 8, 40)

These are **holdouts of parameters/seeds, not holdouts of a real GPU benchmark**. H1 and H2 are predicted to pass a *conditional* joint-objective gate; H3/H4 are predicted not to improve critical completion materially. H5/H6 stress tradeoffs. All predictions are frozen before reading holdout outcomes.

## Quantitative conditional gate (not sufficient for world-class completion)

A win regime requires guard mean critical-burst latency <= 0.90 x work-conserving, guard background completions >= 0.90 x work-conserving, guard background completions >= 1.10 x fixed-reserve, and guard critical-burst latency <= 1.05 x fixed-reserve. Use paired seed means, report individual seeds and p95 as well. If neither H1 nor H2 passes, retire V298. Even if one passes, V298 must be compared against an implementable predictor-aware controller with the same state, and matched RTL timing/area/electrical evidence. If an equal-cost controller dominates it, retire.

## Candidate boundary law to falsify

For a **single isolated freed MSHR credit**, a background request of known fixed latency Lb admitted at a critical return and a dependent critical miss ready D cycles later, a work-conserving refill can delay the dependent issue by max(0, Lb-D) cycles. A held credit eliminates this particular delay, costing D idle-credit cycles. This is a **one-credit counterfactual**, not a claim that the formula predicts multi-MSHR queue completion. The physical value requires an observed critical-path sensitivity to this delay, enough background saturation, no other free credit, and sufficiently small area/timing/power penalty. The unseen multi-MSHR results must be checked against this qualitative boundary; a general predictive law remains unproved.

## Physicality and novelty kill gates

Must add clocked RTL, independent equivalence checks, matched synthesis with strongest implementable predictor-aware comparator, CTS/routing/extracted-RC electrical checks, MSHR occupancy and background bandwidth accounting, workload-level latency/throughput, sensitivity to load/wires and power proxies. All failures preserved. No GPU speedup, 5090-equivalence or world-class result may be claimed from this synthetic simulator.

## Prior-art constraints

- Jog et al., *Orchestrated Scheduling and Prefetching for GPGPUs*, ISCA 2013, DOI 10.1145/2508148.2485951.
- Joseph et al., *WaSP: Warp Scheduling to Mimic Prefetching in Graphics Workloads*, arXiv:2404.06156 (2024).
- RPAWS, *A Resource-Pressure Aware Warp Scheduler for GPGPU*, IEICE Electronics Express (2026), https://globals.ieice.org/en_publications/elex/10.1587/elex.23.20260028/_f.
- Jeong et al., *Warped-Compaction*, HPCA 2025, DOI 10.1109/HPCA61900.2025.00106, constrains any RF-collector claims.

No novelty beyond those mechanisms has been demonstrated. V287/V296/V297 evidence remains preserved on their closed PRs; Kernellum PR #119 and holdouts are separate and untouched.
