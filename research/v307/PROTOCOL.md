# V307 prospective protocol: next-bank-pressure tie-break (2026-10-29)

**Evidence tier:** synthetic bank-issue scheduling, not GPU IPC, synthesis, area, timing or novelty.

## One mechanism
A five-warp, three-issue-slot, eight-bank, single-read-port-per-bank scheduler sees current and next bank-pair masks. Every instruction requires two *distinct* banks. The candidate first maximizes **current** conflict-free issue cardinality and, among tied subsets, chooses the one minimizing the next-cycle **bank pressure**:
P(S) = sum_b max(0, n_b(next_head_after_S)-1).
Tie-break by fixed ascending warp priority. It never sacrifices present cardinality. All instructions preserve per-warp order and must retire once.

## Equal-resource controls
MAX-NOW maximizes current cardinality with fixed priority. FUTURE-TIE uses exactly the same two-instruction visibility and chooses the maximum current-cardinality subset whose resulting next cycle permits the maximum conflict-free issue count. It is the **strongest data-matched control**; although likely more complex, no area or delay advantage is assumed until RTL. All policies share five warps, eight banks, three issue slots and exactly the same program traces.

## Frozen pilot / unseen holdouts
Exploratory source and focused tests are frozen at SHA-256 `868db459b4db9ac23ae4004b8eaa78359891cec5e4e8f7437a0098dd264e0d7a` (simulator.py) and `70ce13a22a0fd567a7849bb7d210e1c48b66024bd176de4ae50c95fd4270cfdf` (test_simulator.py) **before pilot**. Unit tests have run only on seeds 0,1,2; no formal pilot seeds opened. Pilot seeds: 31–34. Prospective holdout seeds: 2001–2020, not to be opened unless pilot passes. Same 48 instructions per warp, 240 total.

W1 predicted win: two uniformly random distinct bank IDs per instruction. N1 predicted no-win: rotating four disjoint bank pairs with 95% probability and random pair with 5%. N2 stress: fixed pair by warp. Primary metric total 240 instructions divided by drain cycles; no pipeline/collector stages modeled.

**Predeclared survival:** W1 mean candidate gain >= +10% versus MAX-NOW, W1 mean candidate gain >= -5% versus FUTURE-TIE, and N1 mean candidate gain >= -2% versus FUTURE-TIE. A failure kills V307 before RTL and holdout. A pass only licenses a stronger stage: realistic operand collectors, dependencies and clocked RTL plus matched physical PPA and prospective holdouts. These gates are screening thresholds, not claims of research novelty.

## Predictive boundary and falsifiers
Pressure is an imperfect proxy for the next-cycle maximum matching: distinct collision topologies can have equal P but different feasible issue counts. This is a predeclared falsifier. The proposed pressure metric may fail on graph structures, persistent hot banks, low occupancy or realistic subcore bank counts. Even success on W1 is only synthetic and cannot establish modern GPU benefit. Prior art includes Barnes, Shen and Rogers, HPCA 2023 (https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf), GPGPU-Sim operand collectors (https://github.com/gpgpu-sim/gpgpu-sim_distribution) and LTRF (https://arxiv.org/abs/2010.09330). No general bank-aware scheduling novelty is claimed.

## Independent checker
An independent combinations-based legal-subset oracle tests 1,296 four-warp bank-mask configurations, plus conservation and port legality. `python3 -m unittest -v test_simulator.py`; `python3 simulator.py --pilot`.
