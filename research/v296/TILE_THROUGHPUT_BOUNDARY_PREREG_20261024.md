# V296 positive-law candidate: tile critical-path and bandwidth boundary (2026-10-24)

**Evidence tier: ANALYTIC MODEL, NOT MEASURED GPU PERFORMANCE.** This is a new, falsifiable *conditional* prediction, not a demonstrated throughput breakthrough. V296 remains the sole provisional mechanism. V287 stays retired.

## The constraint that prevents benchmark overclaiming

V296 pairwise and serial one-hot bank arbitration implement the **same admission semantics** (previous functional-equivalence evidence). With identical resources, frequency, offered requests, occupancy and bank-port configuration, both admit the same operations in the same cycles. Therefore V296 has **zero direct IPC advantage at a fixed clock**. A controller area reduction is not itself a throughput gain; it might instead enable a smaller tile, a higher frequency, or reinvestment, each requiring separate physical evidence.

Let `q(B,S,P_conflict,occupancy,traffic,control_overhead)` be the **measured** accepted useful operations/cycle for the shared arbitration semantics. Do not infer q from a made-up independence assumption; obtain it from the cycle-accurate simulator and verify against RTL. Bank-port pressure, request compatibility and occupancy enter through q. Mask overlap was specific to retired V287 warp fusion, not to this bank-arbitration mechanism. Let `b` be measured off-chip bytes/useful operation, `W` sustained bandwidth in GB/s, `T_c` and `T_v` controller-limited clock periods (ns), and `T_o` the longest *other* tile path (ns). Under equal resources and no other bottlenecks:

```
T_tile,j = max(T_o, T_j)
R_j = min(q / T_tile,j, W / b)                 [Gop/s]
G = R_v / R_c - 1
W_crit = b * q / max(T_o, T_c)                 [GB/s]
```

A positive gain is possible **only if** (1) V296 reduces the actual tile period, and (2) the control is not already bandwidth saturated: `max(T_o,T_v) < max(T_o,T_c)` and `W > W_crit`. The gain is zero if `T_o >= T_c`, or `W <= W_crit`, or both variants run at the same fixed tile clock. A faster controller can still produce zero workload benefit. The ceiling for any positive gain in this simplified model is `max(T_o,T_c)/max(T_o,T_v)-1`. Other memory, port, latency and power constraints can only reduce this optimistic ceiling.

## Frozen synthetic falsification examples (not prospective GPU workload holdouts)

Use q=1 useful op/cycle and b=4 B/op. These examples are *unit tests of the algebra*, not empirical validations:

| Synthetic regime | T_c | T_v | T_o | W | Predicted gain |
|---|---:|---:|---:|---:|---:|
| Clock-limited, spare bandwidth | 4 ns | 3 ns | 2 ns | 2 GB/s | +33.33% |
| Bandwidth-limited | 4 ns | 3 ns | 2 ns | 0.8 GB/s | 0% |
| Another tile path dominates | 4 ns | 3 ns | 5 ns | 2 GB/s | 0% |
| Partially bandwidth-limited | 4 ns | 3 ns | 2 ns | 1.1 GB/s | +10% |

Reproduce with `python3 research/v296/tile_throughput_boundary.py --self-test` or `--example-regimes`. The local algebraic self-tests passed before commit. **Do not use the synthetic 4/3 ns path values as measured V296 clock periods.** The global-route slack difference cannot be directly interpreted as frequency gain; setup endpoints, clock-tree effects and full-tile paths must be characterized.

## Prospective empirical validation still required

1. Freeze **new, unopened** trace/workload regimes with low/high bank compatibility, low/high occupancy, low/high bank-port pressure, and bandwidth below/above the measured `W_crit`. No tuning on held-out outcomes.
2. Establish that q is equal cycle by cycle for both arbiters under RTL equivalence; measure q and b with independent counters. Compare against the strongest equal-resource serial one-hot control, not a deliberately weakened baseline.
3. Complete extracted detailed route, CTS, hold repair, switching activity/power and actual *tile* critical-path analysis. Use those measured T values to predict which holdouts win/no-win **before** observing throughput.
4. Validate the signed gain and its magnitude on unseen workloads; report errors, no-win cases, independent checker, and reject the model if its predictions fail.
5. Treat area savings as a separate physical resource metric until a matched-tile reinvestment experiment demonstrates an occupancy or power consequence.

**World-class completion gate: NOT REACHED.** The current 45%-density detailed-route experiment is only the next physical rung; this model supplies a conditional positive-law hypothesis and explicit no-win regimes, not validation.
