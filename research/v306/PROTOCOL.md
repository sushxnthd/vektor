# V306 frozen protocol: two-cycle bank-aware warp issue lookahead

Date: 2026-10-29. Status: FROZEN BEFORE FORMAL PILOT (seeds 21–24). This is a synthetic structural-bottleneck hypothesis, **not** a demonstrated modern GPU bottleneck or a novelty claim.

## Mechanism and physical contract

V306 considers at most five ready warp heads, with at most three warp instructions issued per cycle. Each instruction has exactly two distinct register-bank reads; eight RF banks each have one read port per cycle. The scheduler examines the current and next instruction of each warp. V306 exhaustively chooses a conflict-free current subset to maximize total feasible issue count over the current and next cycle, using the next-cycle maximum as a two-cycle planning score. Only current instructions are issued; next-cycle decisions are recomputed. No instructions are dropped, reordered within a warp, or executed more than once. There is no speculative read or preemption.

**Strongest data-matched simple control:** FUTURE-TIE first maximizes current-cycle issue count and then uses the same two-instruction-per-warp visibility to maximize the next-cycle feasible issue count. Other controls: current-cycle maximum cardinality (MAX-NOW), fixed ascending warp priority (PRIORITY). All share identical bank count, read ports, issue slots, warp programs, and lookahead visibility where applicable. V306 has *more* combinational selection work than FUTURE-TIE, so any gain must first exceed that control and then survive matched RTL area/timing. It is not a matched-area comparison yet.

## Prospective integrity

Exploratory prototypes using seeds 1–20 were run **before** this protocol and are not prospective evidence. Formal pilot seeds 21–24 are unopened at freeze; holdout seeds 1001–1020 remain unopened unless the pilot survival gate passes. Do not adjust workload parameters, controls, metrics, or gates after opening formal pilot. A failed pilot closes the mechanism without holdout or RTL.

## Frozen workloads and thresholds

Five warps, 48 instructions per warp, eight banks, three issue slots, one read per bank per cycle. W1 predicted win: two independent uniformly sampled bank identifiers without replacement per instruction. N1 predicted no-win: four rotating bank pairs indexed by warp and instruction position, with 95% probability of the structured pair and 5% random replacement. A deterministic per-seed RNG generates all programs. Both regimes use the same program across all schedulers.

Primary metric: total instructions / cycles until all warp programs drain. Also report cycles, issue distribution, idle slots, and conflict-free capacity. The W1 survival gate requires >=5% mean throughput improvement over FUTURE-TIE with no seed >2% worse; N1 requires <=2% absolute improvement or regression versus FUTURE-TIE. MAX-NOW and PRIORITY are diagnostic weaker controls and cannot establish survival.

## Independent checker and physical gate

Implement a separate reference enumerator for current-cycle legal subsets and test per-bank port constraints, in-warp order, conservation, deterministic replay and no deadlock. A surviving V306 requires matched clocked RTL, equal decoder visibility, same bank/issue resources, Nangate45 synthesis, timing, fanout/wire sensitivity, power proxy and an end-to-end tile model. If the extra lookahead logic erases the improvement, kill immediately.

## Predictive boundary hypothesis

For available current subsets S, let m(S) be the number issued now and f(S) the maximum feasible issue count one cycle after S. V306 chooses argmax [m(S)+f(S)], whereas FUTURE-TIE chooses lexicographic argmax [m(S), f(S)]. **Necessary positive boundary:** there must be a state with m(S*) < m(S_tie) and m(S*)+f(S*) > m(S_tie)+f(S_tie), with the extra future capacity outweighing its present loss and control delay. If no such states occur, the two policies cannot diverge by their primary objective. This is an algorithmic necessary condition, not a predicted GPU speedup law.

## Prior art and claim boundary

Bank-aware GPU warp scheduling and operand collectors are established, including Barnes et al., HPCA 2023 (https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf) and the GPGPU-Sim operand collector (https://github.com/gpgpu-sim/gpgpu-sim_distribution/wiki/test1). V306 cannot claim novelty merely from avoiding bank conflicts. The synthetic model omits dependencies, memory, writeback contention, collector staging, real ISA decoding, subcore partitioning, wire delays and compiler effects. No GPU IPC or RTX-5090 equivalence claim is permitted.
