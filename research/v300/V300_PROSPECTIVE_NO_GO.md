# V300 final prospective no-go — 2026-10-29

**Decision: RETIRE without RTL/physical implementation.** The frozen H1 survival gate required >=5% lower mean warp wakeup latency than the strongest simple greedy control. The measured reduction was **0.1903449181%**. Do not retune against the opened seeds.

## Proven algorithmic identity

With exactly four outstanding sectors and unit sector-return time, the V300 two-prefix enumeration is *already an exact 24-permutation oracle*, not an independently new scheduling principle. Fix any first two sectors. There are two remaining sectors. Swapping their order changes only the wakeup time of warps whose remaining demand consists of exactly one of those sectors. Warps needing both complete on the fourth return in either order. Thus choosing the third sector with the most immediate unlocks minimizes the total wakeup sum for that prefix. V300 enumerates all 4*3=12 ordered two-sector prefixes and selects the minimum. Consequently its cost equals the global four-sector optimum for **all** demand masks, not merely sampled masks. This identity is not a new architecture theorem.

The independent full 24-permutation oracle agreed with V300 on all 4,368 exhaustively checked demand tuples of one to three warps. A deliberately defective fixed-order control was detected.

## Frozen prospective results

Five independent seeds, 1,000 line-fill episodes per seed per regime, 25,000 episodes total. All requests for each line arrive simultaneously. The measured quantity is mean cycles to release a waiting warp, **not GPU throughput**.

| Regime | V300 mean | Strongest greedy mean | Relative improvement |
|---|---:|---:|---:|
| H1 predicted win | 2.280975 | 2.285325 (shortest remaining) | +0.190345% |
| H2 predicted no-win | 1.907925 | 1.907925 | 0% |
| H3 random masks | 2.826050 | 2.831525 (unlock) | +0.193359% |
| H4 high overlap | 2.034225 | 2.034650 (shortest remaining) | +0.020888% |
| H5 sparse warps | 2.384300 | 2.384300 | 0% |

The exact oracle was identical to V300 in all five regimes. The H1 improvement is over **26 times smaller** than the frozen 5% requirement. More complex combinational scheduling has no demonstrated payoff over a cheap implementable shortest-remaining greedy policy.

## Limits and reproduction

- Raw JSON artifact: https://github.com/sushxnthd/vektor/actions/runs/40809192260/artifacts/12870050476
- Hosted workflow: https://github.com/sushxnthd/vektor/actions/runs/40809192260
- Reproduction: `python research/v300/sector_fill.py --holdout`
- Independent exhaustive check: `python research/v300/sector_fill.py`
- The synthetic model omits sector return arbitration across cache lines, arrival times, bandwidth contention, queue capacity, wire delay, area and power. None of these omissions can rescue the preregistered synthetic gate.
- Prior art includes critical-word-first/early restart and dependency-aware scheduling. No novelty claim is made.

**Kill rule:** Do not spend time synthesizing V300 or asserting a tile-level speedup. Preserve this result as a counterexample to equating exact small-instance optimization with a competitive GPU microarchitecture.
