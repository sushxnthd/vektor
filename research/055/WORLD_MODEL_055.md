# Vektor-055 Discovery Protocol V2 — 2026-10-09

## World model
- **KNOWN:** Vektor-054 passed 24/24 RTL differential tests and generic synthesis (CI run 37880347241). Its fixed-three-source assumption is not a realistic universal ISA contract.
- **KNOWN (narrow static PTX sample):** Pinned 14-kernel BPF PTX + compiled vector-add fixture contain 10 repeated virtual-register uses among 577 eligible source uses (1.733%); none in 21 three-source instructions. This is neither dynamic frequency nor physical-register allocation.
- **BELIEVED:** Source-valid masks are required for two-source/immediate-bearing instructions and masked completion.
- **CONFLICTING:** 054's synthetic 25% alias benchmark suggested larger gains; audited PTX contains much less repeated-source traffic.
- **FALSIFIED:** All instructions require three register reads.
- **ANOMALOUS:** 19 of 64 PTX-static-uniform synthetic seeds regress under dedup despite lower aggregate read traffic.
- **KNOWN (bounded RTL):** Masked collector passed 40/40 Icarus differential tests (60,000 RTL cycles) and equal-budget generic Yosys synthesis, CI run 37887628553; 2,175 baseline vs 2,371 dedup generic cells (+9.01%).
- **UNTESTED:** Technology-mapped/physical PPA, 32-wave behavior, physical register traces, banked RF, real workload IPC, and all RTX 5090-class gates.

## E055-A — DISCRIMINATION: virtual-register alias audit
**Mechanism:** repeated source register identities can share a physical read if preserved through lowering. **Prediction:** fewer aliases than 25% synthetic stress (exploratory). **Outcome:** 10/577 eligible static source uses, 0/21 three-source instructions. **Residual:** large distribution mismatch; denominators differ from synthetic alias injection. **Weakened:** assuming synthetic 25% alias is typical. **Alternatives:** hand-written PTX style, static/dynamic skew, virtual-to-physical remapping. **Uncertainty:** high. **Next test:** dynamic physical-register traces across independent kernels.

## E055-B — CAPABILITY-BUILDING: masked tagged collector
**Mechanism:** mask-valid root selection, completion and fanout. **Prediction:** 40/40 RTL differential traces pass (frozen before CI). **Outcome:** 40 software-reference traces passed independent protocol checks; 40/40 RTL differential tests passed (60,000 RTL cycles); Yosys `check -assert` passed, 2,175 baseline vs 2,371 dedup generic cells (+9.01%). **Residual:** zero software/RTL mismatches; generic dedup cost +196 cells; physical PPA unknown. **Weakened:** fixed-three-source correctness assumption. **Alternatives:** shared software model assumptions; need RTL simulation. **Next:** banked multi-slot RTL and mapped synthesis with real source mix.

## E055-C — DISCRIMINATION / SURPRISE: static PTX-mix replay
**Mechanism:** less read traffic changes collector occupancy and return timing. **Prediction:** lower gains than high-alias stress (exploratory). **Outcome:** 64 held-out seeds: 27,464 -> 27,657 completions (+0.703%), 40 wins/19 losses/5 ties. Paired-seed bootstrap 95% interval +0.371% to +1.044%, synthetic seeds only. **Residual:** much smaller than +10.04% 25%-alias control. **Weakened:** monotonic throughput gain assumption. **Alternatives:** scheduling randomness, finite return capacity, static-uniform weighting. **Next:** dynamic instruction-weighted replay with common-random-service control.

## Failure clustering and single next decisive action
047–054 bottlenecks repeatedly involve RF read capacity, queue credits, collector occupancy, scheduler resonance, and unmeasured workload mix. Elevate **source-count realism + finite-collector backpressure** as a joint research target. Masked RTL differential and generic synthesis now PASS in free CI. Do not adopt the architecture until equal-port banked and mapped-PPA controls and dynamic physical-register traces exist. All 5090-class gates remain INCONCLUSIVE.
