# V314 preregistration: completion-hint bank-port arbitration (2026-10-31)

## Mechanism, scope, and hypothesis

One active mechanism: **completion-hint priority** within an existing four-slot, buffered, early-capable, bank-aware GPU operand collector. For each otherwise-eligible register-file read, prefer an operand whose partner was already collected, subject to a 16-cycle age-protection override. All other reads use oldest-first priority. No additional issue slots, register-bank ports, queues, bypass capacity or early-read privileges. This is an architectural *screen*, not a novelty or GPU-performance claim.

The physical motivation is modest: a single already-collected partner bit per operand-collector entry may reduce wasted partial progress under bank contention. A pilot (seed 121, 20,000 cycles) observed only 0.14-0.17% completion gain and worse p99 latency in hot regimes. **This pilot is disclosed, not treated as prospective evidence.** Strong equal-information collectors may already implement this priority; any novelty claim is prohibited without prior-art and exact strong-control checks.

## Strong baseline and resource model

- Both: four independent warp-head FIFOs, depth four each; 16 banks, two read ports per bank/cycle, two *distinct physical register* operands per instruction, four issue slots/cycle.
- Both: ready instructions served before dependency-blocked heads; early-ready operands of blocked instructions use only remaining bank-port capacity; no source-version changes in the model.
- Baseline: bank-aware, buffered, age-first, early-capable collector, rotating slot tie-break. This is much stronger than an unbuffered/head-only collector.
- Candidate: same information, resources, and trace; completion-hint priority and 16-cycle age shield. The hint/selection logic must be accounted for in any future matched RTL area/timing comparison.
- All offered traces are generated *before* either policy is evaluated. No bank address/operand-value oracle is exposed to one policy alone.

## Frozen prospective tests (not used in pilot)

All tests use 2,000 warmup + 20,000 measured cycles; independent fixed seeds:
1. **Predicted small-win / bank-hot:** seed 314801, arrival probability .98/slot/cycle, first bank hot probability .97, second bank slot-affinity .85, no dependency delay. Predicted completion ratio **1.0005 to 1.004**. Materiality gate nevertheless **>=1.0200**. A statistically small positive result is not enough.
2. **Predicted no-win / uncongested:** seed 314802, arrival .70, both banks uniform, no dependency delay. Predict **1.0000** completion ratio, no dropped jobs and no p99 regression.
3. **Unseen transfer:** seed 314803, arrival .93, first-bank hot probability .75, second-bank affinity .50, no dependency delay. Prediction **1.0000 to 1.0060**.
4. **Dependency sensitivity:** seed 314804, arrival .97, first-bank hot .94, second-bank affinity .70, second operand delayed by six cycles with probability 1/4. No directional gain promised.

## Mandatory kill gates

- Any bank consumes more than two read ports/cycle, issue exceeds four/cycle, or a source is read before ready: reject.
- Any significant increase in p99 latency under predicted win: reject for tail-safe use.
- If predicted-win completion ratio is below **1.02**, reject as immaterial before RTL, even if the small-win interval is met.
- If equal-information, equal-resource, competent completion-aware collector reproduces decisions, reject incremental novelty.
- No claim of GPU throughput, physical timing, electrical signoff, or RTX 5090 equivalence follows from this synthetic model.
- Independently check workload conservation, port limits, exact read accounting, and freeze the negative result even if inconvenient.

## Analytical boundary

For any bank b and T cycles, at most 2T RF reads can be served at b. For N completed two-operand instructions with empirical average bank-b demand d_b per completed instruction, N <= 2T/d_b plus the finite queue boundary correction. Reordering **cannot change d_b**. Thus any benefit is limited to scheduling efficiency below this fixed-capacity ceiling. A positive result must survive the strong collector, physical timing and area, and real trace tests.
