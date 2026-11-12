# V316 prospective architecture-fidelity / novelty gate (2026-10-31)

## Single mechanism under test
V316 tests **fixed-window register-bank reservation with backup-warp admission**: if the highest-priority ready warp cannot reserve all RF source reads in a fixed 3-cycle window, attempt the next ready warp. Reads are not buffered for variable-latency operand collection; issue waits until the complete fixed-window reservation can be made. This is a candidate *architecture scheduling policy*, not a claim about actual Blackwell hardware.

## Critical new external baseline
Huerta et al., *Dissecting and Modeling the Architecture of Modern GPU Cores*, MICRO 2025, DOI 10.1145/3725843.3756041, https://arxiv.org/abs/2503.20481. The authors' reverse-engineered modern NVIDIA model uses compiler-guided dependencies, register-file caching, and no traditional variable-latency operand collectors. Their conclusions are based on particular measured NVIDIA generations; they do **not** establish every GPU, Vektor, or RTX 5090 has identical microarchitecture. An independent Blackwell microbenchmark study: https://arxiv.org/abs/2507.10789.

This is a material fidelity challenge to V312-V315's older buffered-collector modeling assumptions. A custom Vektor design may deliberately use collectors, but RTX-5090-class comparisons cannot assume that design is the modern NVIDIA baseline.

## Frozen hypotheses before evaluating the new script
H1. Relative to a *head-only* fixed-window controller, backup selection can increase admitted opportunities in a synthetic hotspot regime. We predict >=1.10x for a regime with primary bank overload and a frequently feasible backup; a disjoint/no-contention regime predicts 1.000x.
H2. Relative to a **strong equal-resource, same-information scheduler that already scans all ready warps and performs the same fixed-window bank-reservation test**, the incremental admission ratio is exactly 1.000000x on every trace. If so, kill V316's novelty claim before RTL.
H3. Fixed-window and buffered-collector models are not interchangeable: an instruction that cannot reserve all reads within the fixed window must stall even when a variable-latency collector could enqueue and service its operands later. The script must exhibit at least one deterministic counterexample.

## Frozen model and controls
- Two banks, one read port per bank per cycle, three-cycle reservation window, up to three operand reads per instruction.
- A source is identified by bank and (optional) cache-hit flag; cached sources consume no RF read slot. The model does not implement real RFC replacement or SASS control-bit semantics.
- Strong comparator uses identical candidate list, ready flags, bank demand, port capacity, and reservation horizon, with identical deterministic priority.
- No hardware area, power, RTL, routing, real SASS, GPU IPC, or timing claims.
- Exact enumeration of small request combinations plus prospective deterministic-seed synthetic win/no-win/transfer regimes; report counts and counterexample.
- Kill if strong comparator parity holds, regardless of improvement over head-only.
- Do not retrofit thresholds or call this a positive architecture result if the strong control matches.

## Continuation after this gate
Acquire compiled SASS with physical register IDs, reuse bits, dependence controls and measured hardware counters; construct a fixed-latency, RFC-aware reference with validation before selecting a new novel mechanism. Do not treat PTX virtual register numbers as physical bank addresses.
