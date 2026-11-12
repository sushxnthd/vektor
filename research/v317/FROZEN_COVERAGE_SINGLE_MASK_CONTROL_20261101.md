# V317 frozen single-mask coverage factorization control (2026-11-01)

**Status: prospective optimization-control protocol.** The already hosted unoptimized coverage wrapper passed 24,583 RTL checks and generic synthesis, but added 1,029 generic cells at 32x32 (4,674 vs 3,645) by gating an already-masked 1,024-bit output a second time. This could be an avoidable implementation artifact rather than a physical lower bound.

## Frozen hypothesis

Factor the coverage condition into the existing stateful grant before the data-output mask, instead of placing a second per-bit mask outside the snapshot module. Predict fewer generic cells at 32x32 than the naive wrapper; do not predict a specific count. Keep both implementations and the base stateful design as equal-function, same-tool controls. Default-off coverage parameter must leave the old baseline behavior unchanged.

## Frozen tests and falsifiers

1. Keep the original naive wrapper under a distinct module name. A parameterized guarded stateful module must implement the *same* sticky coverage contract without changing the old default path.
2. Compare optimized and naive grants and forwarded data across all 4,096 four-lane captured/requested/written triples and directed reset, coverage, namespace and recapture cases. Zero mismatches required.
3. Synthesize the three designs at 4x8, 8x16, 32x32 in one hosted Yosys workflow with the same parameters and flattening. Record cell, flop, depth and fanout proxies. If the optimized 32x32 implementation is not smaller, reject the factorization hypothesis and preserve the result.
4. Do not equate a smaller generic netlist with placed area, routed timing, power or GPU throughput. The independent coverage detector, event network, metastability protection and cache-coherence interface remain unimplemented.

## Decision

This is a physical-cost *control* on a previously rejected forwarding idea, not a promoted architecture mechanism. An equal-information reuse-aware baseline can perform all safe forwards. The incremental modeled throughput advantage remains zero regardless of synthesis outcome. Preserve one branch and draft PR #34, and leave Kernellum PR #119 untouched.
