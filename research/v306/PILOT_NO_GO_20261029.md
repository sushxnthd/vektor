# V306 pilot no-go: two-cycle bank lookahead adds no throughput over future-tie

Date: 2026-10-29. Evidence tier: **local deterministic synthetic simulator + independent exhaustive legality oracle**. Not GPU IPC, RTL, synthesis, electrical or measured hardware performance.

## Prospective integrity

The protocol was frozen at commit `bd1127949e5cf0d4ee74142e7bdb8fca07cb9b28` before formal pilot seeds 21–24 were opened. Exploratory prototypes using seeds 1–20 were explicitly disclosed before freeze and excluded. **Holdout seeds 1001–1020 remain unopened.** No retuning, no post-hoc threshold changes.

Run from repository root:

```sh
cd research/v306
python3 -m unittest test_simulator.py -v
python3 simulator.py --pilot > pilot.json
```

Local execution passed four tests, including an independent exhaustive `itertools.combinations` legality oracle over **20,736 states**. Every simulated instruction completed once, with no same-cycle RF bank-port conflicts. All policies had identical instruction traces, five warps, 48 instructions/warp, eight single-read-port banks, three issue slots and two source-bank reads per instruction.

## Frozen pilot, cycles to drain 240 warp instructions

| Regime | Seed | Fixed priority | Max-now | Future-tie strong control | V306 full lookahead |
|---|---:|---:|---:|---:|---:|
| W1 random banks | 21 | 130 | 115 | 99 | 99 |
| W1 random banks | 22 | 128 | 124 | 106 | 106 |
| W1 random banks | 23 | 129 | 123 | 95 | 95 |
| W1 random banks | 24 | 128 | 123 | 98 | 98 |
| N1 structured | 21 | 103 | 101 | 99 | 99 |
| N1 structured | 22 | 98 | 96 | 92 | 92 |
| N1 structured | 23 | 101 | 98 | 98 | 98 |
| N1 structured | 24 | 96 | 96 | 96 | 96 |

W1 mean cycles: priority **128.75**, max-now **121.25**, future-tie **99.50**, V306 **99.50**. N1 mean cycles: priority **99.50**, max-now **97.75**, future-tie **96.25**, V306 **96.25**. Since all policies retire the same 240 instructions, relative throughput is inversely proportional to total cycles.

**V306 versus strongest data-matched FUTURE-TIE: +0.000% throughput in W1, +0.000% in N1.** The frozen W1 survival threshold was +5%, so V306 is retired at pilot. The cheaper future-tie control improves W1 synthetic throughput by **21.86%** versus MAX-NOW, but this is *not* V306's incremental result or evidence of a novel GPU architecture. Future-tie uses the same next-instruction visibility and does not sacrifice immediate issue cardinality.

## Mechanistic boundary and hardware relevance

The two-cycle score is `m(S)+f(S)`, while FUTURE-TIE maximizes `(m(S),f(S))` lexicographically. V306 can improve on FUTURE-TIE only if sacrificing an immediate issue enables enough additional next-cycle issues to improve the long-run schedule. Across the frozen pilot, it does not: one lookahead downgrade in W1 seed 22 and zero in the other seven seed/regime combinations, with no cycle advantage. **This is an observed model result, not a theorem of global equivalence.**

The scheduler is deliberately more optimistic than a physical GPU: both policies see a second decoded instruction per warp, no dependency stalls, no collector stage, no memory pressure, no writeback contention, no wire/load delay and no multi-cycle scheduling path. If the expensive exhaustive lookahead cannot outperform the simpler same-information control here, physical implementation is unjustified. The gain against MAX-NOW is insufficient to save V306.

## Prior-art audit and next bottleneck

Bank-aware warp scheduling and operand collectors are already described by Barnes et al., HPCA 2023: https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf and GPGPU-Sim: https://github.com/gpgpu-sim/gpgpu-sim_distribution/wiki/test1. Neither source supports novelty of this lookahead policy. Before promoting any new architecture candidate, reproduce a bottleneck in a published GPU simulator or actual microbenchmark and compare against an optimized bank-aware scheduler. The simplified W1 synthetic speedup against MAX-NOW cannot be projected to SM-level IPC.

**Decision: NO-GO.** Close the draft PR unmerged, preserve this simulator and negative result, leave frozen holdouts unopened, and do not invest in RTL or claim RTX-5090 equivalence.
