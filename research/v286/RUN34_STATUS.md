# V286 run34: conditional positive law, not a GPU breakthrough

Active kernel: V286 only. V285 retired on separate branch.

**Bottleneck law:** for two reads per bank, bank service cycles have lower bound max_b ceil(n_b/2). A warp-conditioned bijective bank permutation can lower the hot-bank maximum when logical register banks are correlated across warps, but can increase it when the workload correlates with the permutation itself.

**Exact mechanism:** compare (a) additive warp salt, (b) plain warp-ID XOR, and (c) one wiring-only permutation of warp-ID bits before XOR. All are fixed per-warp bijections on 16 banks, preserving storage distribution for a warp with 16 consecutive logical bank IDs. Read and write bank mapping must be identical.

**Strong controls:** identity, plain XOR, addition, other equal-cost bit permutations/GF(16) linear hashes, compiler-aware bank allocation. The chosen bit permutation is not established as best across all controls.

**Frozen unseen predictions:** rotated-XOR / plain-XOR grants = 1.9786x when logical bank tracks unpermuted warp ID; 0.5055x when it tracks the rotated ID; 1.0000x in hot-same; 1.0013x for independent indices. All within frozen tolerances. This is an explicit win/loss law, NOT measured throughput.

**RTL gate:** exhaustive 256-pattern bank-mapping inverse checker exists. Additive and plain-XOR mapper RTL simulations passed; mapped Nangate45 cell area additive 17.822 (14 cells, 4-cell path), plain XOR 6.384 (4 cells, 1-cell path). Additive variant is not equal-budget competitive. Permuted-XOR CI: https://github.com/sushxnthd/vektor/actions/runs/39803798594 (pending as of record). No max-cap/slew, STA, full RF row allocation, dynamic power, or wire sensitivity.

**Decisive next gate:** a single deployable permutation must beat the strongest same-area static hash on frozen workload families without intolerable regressions, with consistent RF storage/writeback and characterized timing. Otherwise retire V286. No extra runs on CI plumbing.

Prior art: https://patents.google.com/patent/EP3915009B1/en and https://arxiv.org/abs/2010.09330. Novelty not established. Integrated V-Tile unchanged. FP32 V153/V156 electrically disqualified. RTX 5090-class remains long-range reference.
