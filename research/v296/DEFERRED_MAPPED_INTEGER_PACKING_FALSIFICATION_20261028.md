# V296 deferred-write mapped-area integer-packing falsification (2026-10-28)

**Decision:** At the frozen 30,000 um² area ceiling, the retimed V296 candidate does **not** buy an extra complete mapped tile slice against the same-latency, optimized V295 serial controller. This is a negative capacity result, not proof of equal routed performance. The candidate retains a small mapped-area advantage, but its benefit is contingent on narrow larger-budget integer thresholds and non-saturated shared resources.

## Provenance and frozen test

Preregistered before evaluation in [DEFERRED_MAPPED_INTEGER_PACKING_PREREG_20261028.md](DEFERRED_MAPPED_INTEGER_PACKING_PREREG_20261028.md), commit `704435a4`. Uses the four SHA-verified mapped synthesis areas from [V296_DEFERRED_WRITE_MAPPED_TRANSFER_FALSIFICATION_20261028.md](V296_DEFERRED_WRITE_MAPPED_TRANSFER_FALSIFICATION_20261028.md). Both variants use 16 banks, two read ports/bank, one global write port, four issue slots, and the *same* additional operand latency (L=2). The V295 serial comparator retains its strongest fifth-stage physical repair. At equal clock, V296/V295 bank admission semantics are identical. No routed area, frequency, macro, power, or real workload trace is inferred.

## Exact integer-packing result

Mapped capacities are `floor(budget / mapped_area)`, using exact integer milli-µm² arithmetic.

| RF depth | V296 mapped area | Serial mapped area | Mapped slices at 30,000 µm² (V296 / serial) | Next narrow candidate-only budget window |
|---|---:|---:|---:|---:|
| D4 | 13,044.906 µm² | 13,510.406 µm² | **2 / 2** | [39,134.718, 40,531.218) µm² |
| D8 | 18,308.514 µm² | 18,769.492 µm² | **1 / 1** | [36,617.028, 37,538.984) µm² |

Thus the current area ceiling gives **zero integer slice-count advantage**, although an independent clock-speed difference could still matter if physically demonstrated. The *first crossover at a budget equal to an integer number of complete serial slices* is D4 29 serial versus 30 candidate at 391,801.774 µm², and D8 40 serial versus 41 candidate at 750,779.680 µm². **These are not the first possible crossovers at arbitrary budgets**: the smaller narrow windows above occur earlier. At high replication, the asymptotic mapped area-density ratios are 1.03568 (D4) and 1.02518 (D8), before any physical overhead.

## Frozen synthetic positive/no-win boundary

At the D8 40-versus-41-slice serial-multiple threshold, run a fixed 410-warp closed-loop model, q=0.98 readiness, two-cycle cooldown, 16 banks, two read ports/bank, four issue slots, 0.20 operand-copy probability, 1,000 warmup plus 7,000 measured cycles, and frozen seeds 20261028/20261029. The two controllers use the same greedy admission oracle, identical per-warp per-cycle random streams, and identical latency. Only the mapped-area-permitted slice count differs.

| Seed | 40 serial waves/cycle | 41 V296 waves/cycle | Uncapped gain | Gain with shared cap 100 |
|---|---:|---:|---:|---:|
| 20261028 | 159.11886 | 162.84371 | +2.34093% | **0%** |
| 20261029 | 159.09000 | 162.85914 | +2.36919% | **0%** |

Both preregistered *synthetic* win/no-win gates passed. An independently implemented dictionary-based port oracle matched the array-based scheduler for 32 cycles at 40/41 slices per seed; the matched 30,000 µm² cases also passed independent 96-cycle replay. These are **exploratory synthetic workload results**, not unseen real GPU workloads, physical performance, or evidence that pairwise arbitration improves same-clock admissions.

## Preserved preregistration error

The protocol predicted that D4 would fit **one** slice of each variant at 30,000 µm². Exact calculation falsified that prediction: it fits **two** of each variant *at mapped-only area*. The equal-capacity conclusion survives, but the exact count was wrong; the result JSON therefore marks `all_preregistered_predictions_pass=false`. The term *serial-budget-multiple crossover* must not be confused with earliest possible arbitrary-budget crossover. Neither error is silently rewritten or removed.

## Physical decision

Do **not** claim a V296 tile throughput win from the retimed mapped-area margin alone. At the actual frozen 30,000 µm² area ceiling, there is no integer-packing gain; at the larger hypothetical budget, a shared bandwidth cap can erase the synthetic 2.34–2.37% gain. The outstanding D4/D8 same-depth pre-CTS matched timing/electrical results are still decisive, followed only if justified by routed checks and workload transfer. Existing sealed GPU workload holdouts remain sealed. V296 remains the sole provisional architecture mechanism, V287 retired. Kernellum PR #119 untouched.

## Reproduction

```sh
python3 research/v296/deferred_packing_boundary.py --self-test
python3 research/v296/deferred_packing_boundary.py --evaluate --output /tmp/deferred_packing.json
```

[Executable checker](deferred_packing_boundary.py) · [Machine-readable results](DEFERRED_MAPPED_INTEGER_PACKING_RESULT_20261028.json). No RTX-5090 equivalence, GPU power, SRAM-macro or matched routed signoff claim.
