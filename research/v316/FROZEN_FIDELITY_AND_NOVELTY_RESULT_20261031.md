# V316 frozen modern-RF fidelity and novelty falsification (2026-10-31)

**Decision: KILL V316 as an incremental architecture mechanism.** Do not build RTL or promote a GPU speedup. Frozen preregistration: [`06093ca`](https://github.com/sushxnthd/vektor/commit/06093ca029b2065492f1f1ea118135a753332725), before executable checks. Independent source-pinned hosted [run #41198764743](https://github.com/sushxnthd/vektor/actions/runs/41198764743) **PASSED**, [raw artifact #13041019419](https://github.com/sushxnthd/vektor/actions/runs/41198764743/artifacts/13041019419). Code: [`fixed_window_falsifier.py`](fixed_window_falsifier.py).

## Results: synthetic opportunity-level admissions, not GPU IPC

| Frozen regime | Analytical predicted candidate/head-only | Hosted observed | Candidate / equal-information greedy |
|---|---:|---:|---:|
| Hot-bank predicted win | 1.882178x | **1.884631x** (95,008 / 50,412) | **1.000000x** |
| No contention / no-win | 1.000000x | **1.000000x** (100,000 / 100,000) | **1.000000x** |
| Prospective perturbed transfer | 1.159091x | **1.160385x** (95,625 / 82,408) | **1.000000x** |

Each frozen regime used 100,000 opportunities. The checker exhaustively compared **20,736** reduced-domain cases: 64 three-cycle/two-bank port-reservation states, 81 two-request source combinations, and four ready-mask states. Candidate and equal-information all-warp scan matched on **every case**.

Exact boundary for this *opportunity model*: if primary is blocked with probability `p`, and backup can issue with conditional probability `q`, `G_vs_head = 1 + p*q/(1-p)`. This law is not a throughput guarantee; no queueing, clock penalty, occupancy, register allocation, memory traffic or real compiler scheduling is included. For equal-information greedy that already checks both warps, `G_incremental = 1` identically.

## Architectural fidelity counterexample

With bank 0's read port already reserved in all three future cycles, a request for bank 0 **cannot** reserve within the frozen three-cycle window. The same request **can** be scheduled in a four-cycle variable-latency service horizon. This proves the two abstract acceptance models are not equivalent; it does not demonstrate either on actual silicon.

Huerta et al., *Dissecting and Modeling the Architecture of Modern GPU Cores*, MICRO 2025, [DOI 10.1145/3725843.3756041](https://doi.org/10.1145/3725843.3756041), reverse engineer modern NVIDIA cores and report compiler-guided dependence, a small RF cache, and no classical variable-latency operand collector. Their modeled hardware and experimental evidence are a stronger comparator for modern NVIDIA-class claims than the old GPGPU-Sim collector abstraction. **This is a model of studied GPUs, not proof of exact RTX 5090/Blackwell internals or a prohibition on custom Vektor collectors.** Blackwell-specific reference: [Jarmusch et al., 2025](https://arxiv.org/abs/2507.10789).

## Consequence and next falsifiable gate

V312-V315 synthetic admission/capacity results cannot be extrapolated to an RTX-5090-class core until a compiler-guided fixed-latency model, physical bank mapping, reuse-bit behavior and measured SASS/hardware counters are accounted for. The immediate next research task is to build an **independent SASS trace schema and compiler-control decoder** with explicit unknown fields and measured provenance; do not pretend PTX virtual registers are physical register-bank addresses. Compare fixed-window scheduler, modern RFC-aware same-information baseline, and candidate under the *same* traces and ports before selecting any new hardware mechanism.

**Evidence ceiling:** source-pinned synthetic model and independent exhaustive checker only. No measured GPU IPC, RTL, Nangate45, OpenROAD placement, routing, electrical, power or tile-level speedup. Retired historical PRs remain unchanged.
