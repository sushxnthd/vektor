# V302 prospective no-go: equal-entry LRU removes the claimed advantage

Date: 2026-10-29. **Retire V302; no RTL or physical claim.**

## Protocol integrity
The [prospective protocol](PROSPECTIVE_PROTOCOL.md) was committed as 978103419c88652794f8d6064d581ac5944cfe76 **before** running the eight frozen holdout seeds. Pilot seeds 100..101 (300 steps) were exploratory and separate. Holdout: seeds 20261030..20261037, 10,000 source steps per warp, four warps and four lanes per active step. Each policy executes the same complete logical program with finite 32-record input buffering and retrying blocked warp steps. Every key's 32-bit modular final sum is checked against the uncombined program.

## End-to-end synthetic logical updates per cycle (means across eight seeds)

| Regime | Warp-aggregated FIFO | Equal-entry LRU | V302 LFU | LFU / LRU | LFU / FIFO |
|---|---:|---:|---:|---:|---:|
| H1 skewed five-key, predicted win | 1.622739 | 5.132110 | 5.133394 | **1.000250** | 3.163413 |
| H2 256-key uniform | 1.005799 | 1.015756 | 1.015752 | 0.999996 | 1.009896 |
| H3 alternating hot-key sets | 1.622082 | 3.610401 | 3.680478 | 1.019410 | 2.268984 |
| H4 low offered load | 0.799413 | 0.801973 | 0.802263 | 1.000363 | 1.003566 |
| H5 two hot keys | 2.517409 | 7.948897 | 7.948897 | 1.000000 | 3.157570 |

**Binding H1 strong-control gate failed**: the frozen >=1.05x LRU requirement achieved only 1.000250x, approximately +0.0250%. All eight H1 per-seed LFU/LRU ratios lie in [0.997826, 1.003651]. The >=1.10x FIFO gate passed, but FIFO is not the strongest control. H2/H3/H4 robustness gates passed. No tuning on opened holdouts.

For H1, the V302 LFU emits **18,909.125** downstream atomic transactions per seed on average, compared with **17,817.75** for LRU, while taking 24,904.25 vs 24,910.5 cycles. This reveals that LFU does not even reduce the relevant transaction count relative to LRU in the intended win regime. H3's +1.94% gain is below the H1 precommitted requirement and cannot rescue the mechanism.

## Semantic and architectural audit
- An independent 512-case modular-add associativity check passes. The model also checks exact per-key conservation for every evaluated trace and policy, including final drain. A concurrent intermediate read observes a different value under deferred combining; the optimization is **not** legal for general atomic semantics.
- The age=8 parameter in the simulator is an **expiry trigger**, not a hard worst-case eight-cycle residency guarantee: one output per cycle can leave other expired entries resident. This contradicts the strict residency wording in the frozen protocol and is an independent reason not to promote without revised hardware and verification.
- The queue model stalls a source warp even when its next program step is a no-op if the input queue is full. This is a conservative scheduling simplification, not validated GPU warp scheduling.
- One downstream transaction/cycle, zero compare/selection delay, zero associative-table area/power and no memory-network contention are optimistic abstractions. Synthetic logical updates/cycle are **not GPU IPC or speedup**.
- Prior art covers warp aggregation, atomic buffering, reduction collision elimination and LFU/LRU. Novelty is **not established**.

## Decision and next gate
Kill V302 before RTL. The decisive equal-entry LRU control eliminates its conditional performance advantage even under optimistic ideal hardware. Do not tune the H1 weights, table size or age against the exposed seeds. The next candidate must target a measured or independently reproducible architectural bottleneck and preregister a predictive boundary against the strongest physically matched alternative.

Reproduce with Python 3: `python3 research/v302/sim.py > v302_holdout.json`. The script is standard-library-only; it emits full per-policy metrics and all frozen gates. Pilot: `python3 research/v302/sim.py --pilot`.

**Evidence tier:** executable synthetic falsification only. No RTL simulation, Nangate45 synthesis, placement, CTS, extracted-RC, electrical signoff, GPU IPC, power, tile-level speedup or RTX-5090 equivalence.
