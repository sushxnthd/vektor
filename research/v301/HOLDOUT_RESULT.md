# V301 prospective holdout result, 2026-10-29

## Decision

**Conditional synthetic survival only.** All four frozen behavioral gates passed on seeds 101-120 (20 seeds, 5000 offered cycles each, five regimes, four return lanes). This is not physical validation, a GPU benchmark, or a novelty claim. The V301 queue-merge implementation remains provisional; do not promote it until matched RTL, area and extracted-RC electrical timing are checked against both the two-way set-associative control and the two-bank controller.

## Unseen holdout (mean lossless drain-time event rate)

| Regime | V301 full-associative | Two-way set2 | Two-bank | FIFO | Frozen prediction |
| --- | ---: | ---: | ---: | ---: | --- |
| H1 medium skew | 2.344153 | 2.005844 | 1.290044 | 0.999917 | Win; **+16.866% vs set2, +81.711% vs two-bank**, passes |
| H2 uniform high | 1.031981 | 1.018958 | 1.875179 | 0.999944 | No-win; **44.966% slower than two-bank**, passes |
| H3 low load | 0.796485 | 0.796485 | 0.796509 | 0.796286 | **+0.025% vs FIFO**, passes |
| H4 hot skew | 3.798889 | 3.798774 | 1.052716 | 0.999947 | **+0.003% vs set2**, tie prediction passes |
| H5 fast epoch | 2.211060 | 1.940849 | 1.290044 | 0.999917 | Diagnostic stress, no performance threshold |

Every policy preserved the bitwise OR completion result for each `(warp,epoch)`; no completion was dropped in the lossless model. Independent exhaustive audit passed 2,560 policy/trace configurations; 128 selftest runs passed.

## Predictive law, not an ex post fit

For B independent lanes with offered probability a and destination probabilities p_w, the expected number of unique destinations requiring distinct ingress updates is

`E[U]=sum_w [1-(1-a*p_w)^B]`.

The single-write-port ingress-only stability necessary condition is `E[U] <= 1` in the absence of inter-cycle merges. This does **not** predict the throughput of V301, whose associative queue can combine arrivals across cycles; it is a useful workload boundary and falsifiable null model.

For fully populated four-return batches, the frozen law `sum_w[1-(1-p_w)^4]` predicted unique destinations on unseen holdouts:

| Regime | Prediction | Observed | Absolute error |
| --- | ---: | ---: | ---: |
| H1 | 2.700175 | 2.708713 | 0.008538 |
| H2 | 3.976623 | 3.976107 | 0.000517 |
| H4 | 1.371422 | 1.374422 | 0.003000 |
| H5 | 2.700175 | 2.708713 | 0.008538 |

These counts were evaluated over all fully populated cycles from 20 held-out seeds, not selected favorable events. The law is elementary occupancy mathematics; it is not a new architecture theorem.

## Physicality and prior-art blockers

1. Eight parallel warp/epoch tag comparisons and queue insertion/OR muxing may cost more area, delay and switching energy than a banked scoreboard or a two-way set-associative accumulator. **No RTL or mapped-area evidence yet.**
2. The micro-model assumes a single scoreboard RMW port. If the target SM scoreboard already has sufficient update ports, the benefit vanishes. No public production GPU schematic has been verified.
3. The synthetic producer continues offering events while backpressured; the result is **drain-time throughput** under an unbounded upstream queue, not realistic warp IPC or end-to-end GPU speedup.
4. Merged-entry oldest age is not per-event latency. Do not cite it as such.
5. Prior work already covers memory divergence and GPU operand scheduling: SC'14 (10.1109/SC.2014.16), MeDiC (arXiv:1804.11038), Triple-A (IEEE ESL 2024), Warped-Compaction (HPCA 2025). No novelty is established for completion merging itself.

## Next hard kill test

Implement the **same four-lane, eight-entry, epoch-safe, lossless protocol** in clocked RTL for V301, two-way set2, and two-bank. Independent cycle-accurate equivalence must pass. Synthesize all in the same Nangate45 library, then check CTS, placement, routing, extracted-RC timing, DRC, slew, capacitance, area and toggle proxy. Compare at matched clock/area and include the upstream backpressure path. If the full-associative comparison loses to physically cheaper set2 or two-bank on the frozen H1 regime, **retire V301**. Do not adjust holdout thresholds.
