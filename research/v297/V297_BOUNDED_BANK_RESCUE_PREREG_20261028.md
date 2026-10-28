# V297 bounded bank-rescue: prospective falsification protocol (2026-10-28)

## Decision and lineage
V296 is retired as an integrated GPU-performance candidate following the censored symmetric physical-repair experiment (V296 PR #13, Actions 40718719600). V287 remains retired. This document freezes the **sole new active candidate**, V297, before implementing its evaluation. Do not reopen V296 physical sweeps or claim its historical area estimates as V297 evidence.

## Mechanism, resources, semantics
Exactly three ready-request positions, each with two read-bank operands. Each bank permits two reads per cycle. Shared issue limit B=2 (or B=1 negative control). Baseline is the strongest priority-preserving greedy serial admission with the same slots, banks, ports, and clock assumption. V297 first computes exactly the baseline grants. Only if baseline grants exactly one and requests 1 and 2 are both valid and jointly bank-port feasible, it substitutes grants [0,1,1]. To prevent perpetual bypass of the oldest request, a single cooldown bit prohibits rescue in the cycle immediately after a rescue. No additional read port, issue slot, operand replication, or write port is permitted. In a true implementation the bypass must also preserve scoreboard, dependencies, ordering, and fairness; those remain unproven.

## Frozen law and oracle
Let M_t indicate the three-request **blocker motif**: baseline admits exactly one and the two younger requests are jointly feasible. With B=2, an exhaustive 3-request subset oracle can issue at most two; rescue improves admission by exactly one when M_t and cooldown=0, otherwise zero. On iid requests with P(M_t)=p and cooldown one cycle, the stationary rescued fraction is r=p/(1+p). Thus E[admissions_V297]=E[admissions_greedy]+p/(1+p). If the candidate clock is slower by factor k=f_candidate/f_baseline and there are no new latency or occupancy effects, predicted throughput ratio is k*(1+r/E[admissions_greedy]); break-even k>Eg/(Eg+r). This is an **analytical conditional law**, not measured GPU speedup, power, or timing.

For B=1, for fewer than two ready requests, or for a bank pattern with no jointly feasible younger pair, predict r=0. For temporally correlated blocker motifs, the iid r law is not guaranteed and must be tested as an out-of-distribution falsifier.

## Frozen prospective evaluation
1. Independently enumerate all 3^6 bank assignments and 2^3 validity patterns (5,832 canonical cases). Verify baseline priority, bank-port safety, rescue optimality when enabled, no issue over-cap, and cooldown behavior. A mutant that rescues a port-conflicting pair must be caught.
2. Use deterministic counter-hash exogenous workloads, 100,000 cycles per seed, seeds 1701/1709/1723/1741 for development; **sealed holdout seeds 2027/2039/2053/2063**. The experiment script must not tune parameters from holdout outcomes.
3. Regimes: (A) iid 40% blocker motif and 60% independent uniform-16 bank requests, all valid, B=2: predicted win; (B) uniform-16 all-valid, B=2: near-zero benefit; (C) all requests (0,0), B=2: exact no-win; (D) motif only, B=1: exact no-win; (E) only first request valid: exact no-win; (F) 37-cycle alternating motif-rich/zero-motif bursts: **iid-law stress test**, no presumption of fit.
4. Estimate p and Eg on development seeds only. Predict heldout admissions using r=p/(1+p), with absolute tolerance 0.005 waves/cycle for A-E; report failures without retuning. Compare actual gains with independent exhaustive oracle, and record per-cycle port violations and starvation/cooldown events.
5. Positive claim is **synthetic per-cycle bank-admission only**. A surviving candidate must next pass independent synthesizable RTL oracle, matched logic synthesis, electrical checks, routed area/timing under identical constraints, workload throughput/traffic with realistic occupancy, clock, wire/load and energy sensitivity. If area, timing, bandwidth, or control overhead destroys the advantage, retire V297.

## Prior-art caution
Bank-aware warp scheduling is established: Gou & Gaydadjiev, *Addressing GPU On-Chip Shared Memory Bank Conflicts Using Elastic Pipeline* (2013), DOI 10.1007/s10766-012-0201-1. Register-bank-conflict mitigation via renumbering is established: *Enabling High-Capacity, Latency-Tolerant, and Highly-Concurrent GPU Register Files via Software/Hardware Cooperation* (2020), arXiv:2010.09330. V297 does **not** claim novelty of bank-aware scheduling; only the specific bounded rescue boundary is under test. Prior-art audit incomplete.

## Noninterference
One V297 research branch and one draft PR. V296 PR #13 remains preserved as negative evidence; close it unmerged when the V297 draft PR is established. Kernellum PR #119 and prospective holdouts are read-only; no concurrent writes. No RTX-5090-equivalence claims.
