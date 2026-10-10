# Vektor-089 — Cancellation ABA, tag quarantine, and a reclamation boundary

2026-10-10 | **DISCRIMINATION / CAPABILITY-BUILDING**, with a follow-up **EXPLOITATION** experiment. Synthetic software models only; **no GPU throughput, RTL, PPA, or silicon evidence**. Parent: Vektor-088 (2cfbd3cd7e750305771f7f7e6f44cc3c73a4f422).

## Preregistered hypotheses and assumptions
Mechanism: cancellation releases a writeback reservation while its completion callback remains in flight. A finite generation tag can wrap and alias a newer transaction. Compare immediate wrapping reuse, quarantine through the maximum callback-delay horizon D, boundary-cycle reclamation, and a unique-ID oracle. Callback delivery occurs **before** cancellation/admission at each integer cycle; at most one new transaction per cycle. Callback latency is 1..D unless explicitly testing a bound violation.

P1: immediate tag reuse can falsely retire a newer operation after wrapping. P2: quarantine prevents false acceptance under the bounded-callback contract but can stall. P3: violating the contract invalidates that guarantee. P4 (follow-up): if callbacks arrive before same-cycle admissions, a tag can be reclaimed at t = issued + D rather than t > issued + D, without introducing false accepts. For one admission per cycle, N >= D distinct tags suffices to avoid quarantine stalls (conditional on the ordering and bound).

## Claim -> implementation -> experiment -> measurement
A deterministic 2-bit/D=6 trace issues at t=0,1,2,3,4, cancels the previous live operation at t=1..4, and leaves the fifth operation live. The old t=0 callback returns at t=6. Immediate wrapping reuse falsely retires operation 4; quarantine rejects it.

486 seeded configurations (432 grid + 54 minimally guided probes, **11.11%** of total) ran for 2,000 cycles each. Equal offered input streams across policies, but policy-dependent admissions/completions. The primary conservative quarantine and follow-up boundary policy results:

| Policy | False accepts | Correct completions | Tag stalls | Admissions |
|---|---:|---:|---:|---:|
| Immediate wrapping reuse | 26,432 | 250,041 | 0 | 487,199 |
| Conservative quarantine | 0 | 234,992 | 96,106 | 421,996 |
| Boundary-cycle reclamation | 0 | 241,726 | 73,683 | 435,360 |
| Unique-ID oracle | 0 | 255,584 | 0 | 477,604 |

Boundary reclamation increased simulated admissions by **13,364 / 421,996 = 3.17%** and reduced tag stalls by **22,423 / 96,106 = 23.33%** versus conservative quarantine. These are **synthetic token admissions**, not execution throughput.

A bounded exhaustive test of **262,144 action traces**, horizon 6, 1-bit tags, D=3, found 14,976 traces with false acceptance under immediate reuse and **zero** under either quarantine policy. Independent C++17/Python event-model comparison: **524,288 per-cycle metric checks matched** across four deterministic traces (65,536 policy-cycle rows). Seven local Python regression tests passed.

Follow-up boundary sweep: 190 configurations, zero false accepts under the bound; all 41 tested N>=D configurations had zero tag stalls. A deliberate callback-delay violation (delay up to 2D) produced 2,895 false accepts for conservative quarantine in one 20,000-cycle test, **falsifying any unconditional safety claim**.

## Mechanism and residuals
The basic ABA prediction was confirmed; the residual false-accept count for both bounded quarantine policies is 0. The bound-violation negative control rejects an unconditional guarantee. The boundary policy exploits a strict ordering fact: all callbacks due at cycle t are processed before new tags are allocated at cycle t. Thus N>=D is a sufficient no-stall condition at maximum one allocation/cycle. This is not a claim of novel ABA theory.

Alternative explanations/uncertainty: artificial cancellation frequency; single live slot; simplified callback behavior; ideal tag comparisons; no writeback values, WAW/RAW, clock-domain crossings, reset, replay, or real execution backpressure. Quarantine requires a trustworthy maximum stale-callback lifetime. If that lifetime cannot be bounded, finite wrapping tags cannot guarantee unlimited reuse without explicit quiescence or a larger nonwrapping identity.

## Discovery Protocol V2 world model
- **KNOWN (software-model scope):** bounded trace counterexample; 262,144-trace bounded enumeration; independent C++ agreement; measured simulation admission/stall tradeoff.
- **BELIEVED:** finite tag quarantine can be implemented cheaply when the maximum callback lifetime is known; N>=D sufficient for one-admission/cycle protocol.
- **CONFLICTING:** prior Vektor-088's no-cancellation fairness results cannot establish cancellation correctness.
- **FALSIFIED:** wrapping generation tags alone guarantee correctness; bounded quarantine remains safe when callbacks exceed the bound; conservative one-cycle extra quarantine is necessary with callback-first ordering.
- **ANOMALOUS:** boundary policy shows a sharp capacity transition at N=D; the relative admission gain is workload-dependent.
- **UNTESTED:** synthesizable RTL equivalence, bounded/unbounded formal safety, reset and generation wrap across clock domains, physical PPA, multi-bank writeback integration, compiler-generated workloads, and GPU performance.

## Adversarial review and next decisive action
Explorer: reclaim the exact boundary cycle. Skeptic: callbacks can arrive after arbitration or be delayed indefinitely. Experimentalist: vary ordering and maximum delay while holding tag count fixed. Analyst: only conditional model correctness is supported. Anomaly Hunter: map stalls near N=D and high cancellation. Prior-Art Auditor: ABA prevention and tagged transactions are established prior art. Replicator: independent C++ event model, 524,288 comparisons. Theorist: with callback-first ordering, bounded delay D and at most A allocations/cycle, **N >= A*D** is a sufficient tag-space bound (not yet tested for A>1).

**Single next decisive action:** implement a cancelable, generation-tagged writeback token allocator in synthesizable RTL, then use Icarus/Verilator plus bounded formal checking to verify cancellation, wrap, reset, and callback ordering. Integrate with Vektor-088 age guard only after that proof.

## 5090-class gate
FP32, matrix by datatype/sparsity, VRAM capacity/bandwidth, L2, texture/raster, ray tracing, area, clock, power, compiler/ISA and full workload reproducibility: **INCONCLUSIVE**. No gate advanced in Vektor-089. Vektor-1A 2.56 GHz, <=575 W, <=750 mm2 and 104.86 TFLOPS are unvalidated targets/projections, not measured performance.

Official external RTX 5090 source rechecked 2026-10-10: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ (21,760 CUDA cores, 2.41 GHz boost, 32 GB GDDR7, 512-bit, 575 W; vendor's 3,352 AI TOPS and 318 RT TFLOPS are not datatype-normalized benchmarks). Do not equate these vendor figures to Vektor capabilities.

Repository hygiene: branch-only, no force push; main remains unchanged. Cost: $0.
