# V296 warp-scoreboard latency/port-pressure preregistration (2026-10-26)

## Status and isolation
This is an additional falsification of the **existing V296** mechanism, not a replacement for its physical/electrical gate. V287 remains retired. Do not alter the existing draft PR, source branch, RTL evidence, or sealed real-workload holdouts. The original post-route implementations both failed setup/hold and capacitance. The retimed pair both failed the frozen +50 ps pre-CTS setup guard; candidate shortfall 75.959 ps. No feasible clock or GPU performance gain is established.

## Mechanistic question
The symmetric operand-capture experiment increases issue-to-result visibility latency from one to two cycles. The existing batch-barrier model does not represent individual warp scoreboards or RF bank pressure. Test the *necessary occupancy ceiling* for W independent warps with one outstanding dependent operation per warp, latency L, and issue width I=4:

    Q <= min(I, W/L) operations/cycle.

This is a conservation upper bound, NOT a sufficient predictor when bank conflicts, fairness, control overhead, or memory pressure bind. The same two-read-port-per-bank 16-bank RF and the same deterministic admission policy must be used for both variants. No credit for a clock improvement unless explicitly hypothetical. With an externally imposed frequency ratio r, a necessary break-even threshold in the synthetic replay is r > Q_serial/Q_retimed. The ratio is computed from the *same frozen per-warp request sequences*.

## Frozen evaluation before opening new seeds
Use 32-bit deterministic Python random seeds **91371 and 91372**, 16 banks, two read ports/bank, four issue slots, one outstanding operation per warp, a 2000-cycle warmup and 18000 measured cycles. Generate 25000 requests per warp *before* replay, so architecture outcomes cannot affect request generation. Each request has two bank addresses; with probability 0.2 the second equals the first, otherwise uniform across 16 banks. The first bank is fixed to bank 0 with probability h, otherwise uniform. For each W and h, compare L=1 and L=2 with identical requests and scheduler fairness policy.

Eight frozen cells: (W,h,seed) = (2,0,91371), (4,0,91372), (8,0,91371), (16,0,91372), (32,0,91371), (8,0.8,91372), (16,0.8,91371), (32,0.8,91372).

Prospective qualitative predictions from *different exploratory seeds*:
- Low occupancy (W=2,4), low hotspot: L=2 loses >35% at equal clock; even hypothetical r=1.05 cannot rescue.
- W=8, low hotspot: >3% equal-clock loss.
- W>=16, low hotspot: absolute equal-clock change <1%; conditional r=1.05 positive, NOT a physical claim.
- High hotspot (h=.8), W>=8: bank contention dominates, so absolute equal-clock change <5%. No universal monotonicity claim: changing readiness may change conflict order.

**Fail conditions**: invalid port count, broken per-warp ordering, candidate and serial seeing different request sequences, violation of the occupancy ceiling, unreported failure of a frozen cell, or reporting a synthetic frequency ratio as measured. Preserve every failing cell. This is synthetic prospective transfer only; no real GPU holdouts are opened.

## Independent checks
Test 1- and 2-warp deterministic schedules against exact occupancy rates, include adversarial port cases, and run a separately written small-step scheduler reference on short random traces. Report counts, readiness, bank rejects, exact per-cell break-even frequency ratios, and finite-window limitations. Follow with RTL hazard/scoreboard and routed physical evidence before any architecture claim.
