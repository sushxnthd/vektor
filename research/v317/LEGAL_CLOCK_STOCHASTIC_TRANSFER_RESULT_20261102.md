# V317 legal-clock stochastic transfer: frozen-case results (2026-11-02)

## Provenance and scope

The [prospective protocol](FROZEN_LEGAL_CLOCK_STOCHASTIC_TRANSFER_20261102.md) was committed at `92e39d2` **before** the independent event simulator was implemented and evaluated. Implementation: [`rtl/legal_clock_stochastic_transfer.py`](rtl/legal_clock_stochastic_transfer.py), committed at `6dbdfa8`. Local command: `python3 research/v317/rtl/legal_clock_stochastic_transfer.py > results.json` (Python standard library only). The script asserts the frozen pass/fail gate and emits per-seed rates, ratios and queue lengths as JSON.

**Evidence tier:** Two prior *measured* Nangate45 routed control-area pairs; all other tile area, budget, 24/25-tile replication, issue opportunities, occupancy, global bandwidth, and queue behavior are synthetic. No SRAM macros, GPU datapath, physical tile floorplan, actual workload IPC, power measurement or real RF-port contention is included. The simulation tests conditional accounting transfer, **not** an independent new architecture mechanism.

The simulator uses 5 frozen seeds (17, 71, 173, 719, 1723), 4,096 warm-up cycles and 120,000 measured cycles per variant/seed. Every tile independently emits at most one useful operation per cycle with probability 1.0 for the source and `q` for pairwise. A separate work-conserving global bandwidth-credit server drains a **synthetic unbounded queue**. The event loop does not call the analytic prediction. Both measured legal-clock area rows yield 24 source and 25 pairwise hypothetical tiles under the frozen budget; the equal-resource controls explicitly override both to 24.

## Frozen predictions and measured five-seed averages

| Regime | Bandwidth b | Pairwise q | Predicted ratio | Event-sim mean | Absolute error | Decision |
|---|---:|---:|---:|---:|---:|---|
| W: original predicted win | 1.10 | 1.00 | 1.0416667 | 1.0416667 | 0 | PASS |
| N: original bandwidth no-win | 0.95 | 1.00 | 1.0000000 | 1.0000000 | 0 | PASS |
| R: original occupancy reversal | 1.10 | 0.95 | 0.9895833 | 0.9896047 | 0.0000213 | PASS |
| H1: unseen modest win | 1.07 | 0.97 | 1.0104167 | 1.0103780 | 0.0000387 | PASS |
| H2: unseen occupancy loss | 1.02 | 0.90 | 0.9375000 | 0.9375028 | 0.0000028 | PASS |
| H3: unseen bandwidth saturation | 0.88 | 0.97 | 1.0000000 | 1.0000000 | 0 | PASS |
| H4: unseen clipped win | 1.01 | 0.99 | 1.0100000 | 1.0100000 | 0 | PASS |
| E1: **equal 24-tile resources** | 1.10 | 1.00 | 1.0000000 | 1.0000000 | 0 | PASS |
| E2: **equal 24-tile resources**, occupancy penalty | 1.10 | 0.95 | 0.9500000 | 0.9500025 | 0.0000025 | PASS |

**All nine means pass the frozen absolute tolerance 0.002.** Maximum mean absolute error is 0.0000387. Per-seed ratio ranges in nontrivial stochastic cases: R 0.9893823–0.9897587, H1 1.0101521–1.0104740, H2 0.9372507–0.9377889, E2 0.9498132–0.9501507. The exact-looking saturated results arise from a synthetic server capacity ceiling, **not** empirical precision of GPU behavior.

### Negative controls and queue semantics

The separately frozen **unqueued** case (`b=0.75`, tile opportunity probability 0.75 for both) produced a mean ratio **1.0171293** across five seeds (range 1.0169665–1.0174458). The backlogged fluid law would instead predict 1.0000000, so applying it to unqueued arrivals is **falsified**. This reproduces the earlier observation that clipped stochastic service can retain headroom even when mean offered work exceeds the shared cap.

At `b=0.95`, the first seed's synthetic unbounded queue grows to **148,916 source** and **273,012 pairwise** pending operations by run end; at `b=0.88`, it grows to **357,397** and **387,730**. These are **not implementable hardware buffers**. They expose the model's lack of finite-buffer backpressure, latency and memory/NoC congestion. A saturated result cannot be promoted to real hardware without those constraints.

## Interpretation and falsification

The results validate the conditional mathematical boundary in its own synthetic service environment, including four predeclared additional regimes and two equal-resource controls. This is **not independent evidence that 25 real tiles can be placed, clocked, powered or fed**. Equal-resource E1 gives 1.0000000: both RTL variants produce identical grants, and the controller rewrite has no demonstrated same-clock intrinsic issue throughput benefit. The hypothetical 25th tile is the only positive lever, and a 5% pairwise occupancy penalty more than erases it.

The combined physical+synthetic evidence therefore supports only a bounded controller-area optimization. It does **not** support GPU IPC, tile throughput, novelty of a positive architectural mechanism, or RTX 5090 equivalence. The positive boundary is a known bottleneck/capacity identity, not a novel law.

## Next decisive gates

1. **Finite-buffer and bank-port physical integration**: replace the unbounded queue with backpressure, explicit RF SRAM read/write ports, wire/load and a matched tile datapath. If the extra tile cannot fit or sustain equal per-tile occupancy, kill the tile-throughput interpretation.
2. **Stronger equal-resource alternative**: allow original RTL retiming/logic restructuring at the same legal clock and area; preserve any counterexample to the pairwise margin.
3. **Physical sensitivity**: multi-corner electrical closure, wire/load perturbations, clock-tree and SRAM macro inclusion, plus activity-calibrated power.
4. **Realistic independent workloads**: freeze real workload regimes before evaluating, and test against measured port/traffic counters and catastrophic backpressure tails.

**Decision:** retain V317 solely as a physically promising controller implementation optimization; the world-class GPU architecture completion gate is not reached.
