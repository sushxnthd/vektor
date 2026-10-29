# V298 variable-latency / false-dependency prospective falsification (2026-10-29)

**Decision: RETIRE V298 as an architecture-performance candidate.** This is a synthetic finite-MSHR result, not GPU IPC, physical timing, routed area, power, or proof of physical impossibility.

## Provenance and freeze

The [prospective protocol](V298_VARIABLE_LATENCY_PROTOCOL_20261029.md) was committed as `ffd308f41cf6b7c06b4ed6dc34b6c6ed1cb83dac` and the [executable model](v298_variable_latency_falsification.py) as `c561e9eef63cf8d58606d737bf027903bec19b13` **before the holdout evaluation**. Frozen seeds: 503, 509, 521, 523. Six regimes, 40,000 cycles/seed, four controllers, four MSHRs, one issue/cycle. This is 3,840,000 synthetic policy-cycles. All policies see identical exogenous arrival events and per-request service draws. Run `python3 research/v298/v298_variable_latency_falsification.py --selftest --evaluate` to reproduce full per-seed JSON and summary.

The new equal-state control `phase_reserve` holds the last MSHR while a scoreboard-visible critical chain is active. It requires a one-bit phase flag, versus the V298 one-bit dependent guard. It is implementable in principle but **not yet RTL-mapped or physically validated**. Work-conserving, fixed reserve, and guard are retained unchanged as policy definitions. False negatives occur on intermediate critical returns; false positives on final returns cancel after a frozen delay. This model does not represent DRAM bank timing, response-port contention, finite pending-queue capacity, cache-hit bypass, predictor energy or a GPU tile.

## Prospective results

Each table cell is mean critical-burst latency in cycles / mean background completions, averaged over four seeds.

| Regime | Work-conserving | Fixed reserve | V298 guard | One-bit phase reserve |
|---|---:|---:|---:|---:|
| V1 stable long | 254.759 / 4830.00 | 92.029 / 3635.50 | 96.964 / 4651.75 | 96.187 / 4557.75 |
| V2 variable long | 154.368 / 4286.50 | 91.835 / 3275.25 | 104.234 / 4172.50 | 99.030 / 4095.25 |
| V3 short no-win | 101.348 / 18480.50 | 92.029 / 13977.25 | 92.981 / 18061.75 | 93.085 / 17358.75 |
| V4 false positive | 154.368 / 4286.50 | 91.835 / 3275.25 | 104.122 / 4040.50 | 99.030 / 4095.25 |
| V5 delayed cancel | 149.479 / 4775.50 | 91.911 / 3654.75 | 100.564 / 4458.25 | 97.748 / 4558.50 |
| V6 low traffic | 92.677 / 1015.75 | 91.835 / 1015.75 | 92.047 / 1015.75 | 92.005 / 1015.75 |

V1 passes the pre-frozen **weak** work-conserving/fixed-reserve joint gate: critical latency -61.94% versus work-conserving, 96.31% of work-conserving background completions, and 127.95% of fixed-reserve background completions.

**V298 fails the preregistered equal-state survival gate.** Against phase reserve, V1 guard has **0.81% worse** critical latency for only **2.06% more** background completions; V2 guard has **5.26% worse** critical latency for only **1.89% more** background completions. Neither regime meets >=5% critical latency improvement or >=10% background retention advantage with <=5% critical latency penalty. No retuning is permitted.

The robustness gate formally passes (V4 and V5 retain 94.26% and 93.36% of work-conserving background completions), but false predictions materially hurt: V4 loses 132 background completions on average relative to V2 under the same base traffic/latency regime. V6 shows essentially no benefit, as predicted.

## Independent physicality warning: unstable background queue

The positive V1/V2 regimes are offered arrival rates above the nominal M/L background service capacity: V1 q=0.30 vs 4/32=0.125 requests/cycle before critical occupancy. Average V1 maximum pending queue is **7,336** for guard, V2 **7,816**. Such growing queues make completion-retention percentages a poor general workload objective. The finite-MSHR simulation bounds *in-flight* requests, not waiting-queue size. The existing H1/H2 positive result shares this caveat. No stable-workload or tile-level speedup should be inferred.

## Post-hoc load sensitivity (exploratory, NOT prospective)

After reading the frozen outcomes, varied V1 arrival probability q with the same four seeds, all other parameters fixed. Reproduce using `v298_load_sweep.py`.

| q | Guard critical latency improvement vs work-conserving | Guard latency difference vs phase reserve | Guard background completions vs phase reserve | Mean max pending queue (guard) |
|---:|---:|---:|---:|---:|
| 0.05 | +2.94% | 0.00% | 0.00% | 5 |
| 0.08 | +12.06% | 0.00% | +0.01% | 9 |
| 0.10 | +23.03% | -0.15% | +0.01% | 18 |
| 0.12 | +57.28% | +0.30% | +1.90% | 179 |
| 0.14 | +61.25% | +1.44% | +2.05% | 943 |

Positive guard improvement against work-conserving survives some stable queues, but **a simpler phase reserve matches its latency/background tradeoff in stable cases**. Signs: positive guard-vs-phase latency difference means guard is slower. The load sweep is exploratory and cannot replace the frozen gate.

## Bounded claim and next action

V298 is a conditional admission heuristic with an isolated-credit identity, not a novel general GPU throughput law. It fails the strong one-bit control comparison; its positive regimes can exhibit unstable offered load; and its same-cycle critical-return path still lacks matched extracted-RC closure. **Retire without spending more on V298 physical implementation.** Preserve the existing mapped RTL results (13.034 vs 12.236 um^2 isolated controller), the 15-event bug repair, liveness counterexample and negative holdouts. Close PR #15 unmerged, do not merge or force-push. Select a genuinely different prior-art-audited mechanism in the next research cycle. V287/V296/V297 remain retired. Kernellum PR #119 untouched.
