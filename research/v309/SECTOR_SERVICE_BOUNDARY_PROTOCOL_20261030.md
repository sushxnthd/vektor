# V309 sector-service pressure boundary: prospective protocol (2026-10-30)

**Evidence tier:** model sensitivity only. This does not authenticate the 2020 trace producer, measure DRAM traffic, validate a GPU cycle model, or promote a hardware mechanism. Continue the sole V309 qualification branch and draft PR #26.

## Fixed inputs, before implementation and evaluation

- Previously audited 11 Rodinia applications, 3,937,565 active dynamic SASS rows.
- Historical-tracer-source-conditional aggregate 32-byte sector envelope: [1,586,194, 1,595,385], from independent branch-bound audit #41010015909.
- Ideal equal-resource **fixed-address** coalescer: cannot reduce the set of sectors covering unchanged addresses. Its reduction is exactly zero.
- The 11 applications are already explored, **not unseen holdouts**.
- No clock frequency, GPU occupancy, cache miss rate, DRAM throughput or physical power number is inferred.

## Predictive boundary law

Define I dynamic instruction rows, S conditional 32-byte sector count, B *hypothetical sector-service* bytes/cycle, P hypothetical issue instructions/cycle, r fraction of sectors removed by an otherwise unimplemented layout-changing transformation, and h fractional issue-service time penalty.

Conditional ceiling C = min(P/(1+h), B I/[32 S (1-r)]). Baseline C0 = min(P, B I/(32 S)). Relative ceiling change G=C/C0-1. **This is not an achieved speedup**, because actual caches, interleaving, latency, and transactions are unmodeled.

## Frozen win/no-win regimes

- Synthetic predicted win: B=8 bytes/cycle, P=1 instruction/cycle, r=1/4, h=1/20. Predict G=+1/3 for both sector endpoints.
- Synthetic predicted no-win: B=32 bytes/cycle, P=1, r=1/4, h=1/20. Predict G=-1/21 for both endpoints.
- Equal-resource ideal fixed-address coalescer: r=0, h=0, predicts G=0 in both regimes.
- Fixed-address coalescer with control cost: r=0, h=1/20, predicts G<=0 for all positive B and P (may be tied while memory-limited).

## Independent audit and kill criteria

Implement an exact-rational analytic calculator and independent **total service time** oracle: total issue service time = I(1+h)/P; sector service time = 32S(1-r)/B; implied ceiling I/max(times). Cross-check all cases on a finite grid, check interval monotonicity, and fail closed on negative or >=100% reduction.

If the equal-resource coalescer is predicted to win, the model is invalid. If the hypothetical layout transform wins only with unverified 25% traffic reduction, **do not promote it**. This experiment cannot validate physicality; the next decisive gate remains producer provenance and independent hardware-counter/cycle-simulation evidence. No further decoder micro-optimization.
