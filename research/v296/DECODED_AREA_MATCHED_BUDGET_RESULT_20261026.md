# Decoded-area equal-budget V296 replay: prospective conditional win/no-win (2026-10-26)

**Decision:** The symmetric bank decoder's mapped-area inversion eliminates the old 17-serial/18-V296 packing story. Under the decoder's *actual mapped area*, a budget for 17 decoded serial slices fits only 16 decoded V296 slices. A port-exact prospective synthetic replay independently reproduced the frozen no-win and hypothetical-win regimes. **This is not physical closure, measured GPU performance, or proof of scheduler superiority.**

## Frozen protocol and provenance

[Preregistration](DECODED_AREA_REPLAY_PREREG_20261026.md) committed at `47395ad9` before implementation or evaluation. Reproducible [Python simulator](decoded_area_matched_budget.py) committed at `78b53238`. Independent local replay using the original port-exact request generator, 16-bank/two-read-port resource checker, and a separately implemented reference state machine passed all small-state checks. Two frozen seeds: 61719 and 61743. Warmup 500 cycles, measurement 4000 cycles. The machine-readable [results](DECODED_AREA_REPLAY_RESULTS_20261026.json) preserve all 16 evaluations. The hosted Python CI gate is newly committed and **not assumed successful until its run completes**.

Mapped area is from original four-way Nangate45 synthesis ZIP, SHA-256 `0cafd08a8a4cbd2164336c9f2ad11e6037c3fac02aa42243ebd1a7641d704ba2`, run 40337484954: serial 10143.112 um²/slice, candidate 10426.402 um²/slice. Equal mapped budget = 17 × 10143.112 = **172432.904 um²**. The 16 candidate copies cost **166822.432 um²**; 17 copies cost **177248.834 um²** and do not fit. This is **not** equal routed tile area, SRAM-inclusive area, or physical clock-tree feasibility.

## Prospective matched-request synthetic results

Both contestants use the same 2-cycle latency and identical admission algorithm to isolate area packing. Thus this experiment **cannot** detect a distinct arbitration efficiency benefit of V296; that must be tested independently. Candidate period ratios below 1 are counterfactual, not measured clocks.

| Frozen workload | Seed 61719 | Seed 61743 | Interpretation |
|---|---:|---:|---|
| W=180, distributed banks, equal clocks | -5.70785% | -5.68907% | **Predicted no-win confirmed** |
| W=180, distributed banks, candidate period 0.90× | +4.76906% | +4.78992% | **Conditional predicted win confirmed**, hypothetical frequency only |
| Same W=180 and 0.90× period, fixed shared cap 25 waves / baseline period | 0.00000% | 0.00000% | **Predicted no-win confirmed**; bandwidth removes gain |
| W=180, period 0.94× | +0.31080% | +0.33078% | Boundary probe, small positive |
| W=32, equal clocks | 0.00000% | 0.00000% | Latency/occupancy-limited; area penalty dormant |
| W=32, period 0.90× | +11.11111% | +11.11111% | Hypothetical clock win at low occupancy |
| W=256, equal clocks | -5.88131% | -5.88201% | Nearly ideal 16/17 area-limited loss |
| W=180, 80% bank hotspot, equal clocks | -5.79110% | -5.72722% | Bank-constrained, still loses |

## New measured-in-simulator boundary

For admissions per local cycle `q_s(W,h)` and `q_p(W,h)`, period ratio `r=T_p/T_s`, and fixed shared physical-time cap `M` (waves per serial clock interval),

`G(W,h,r,M) = min(q_p(W,h)/r, M) / min(q_s(W,h), M) - 1`.

With no shared cap, `G>0` iff **`r<q_p/q_s`**. At W=180, h=0, the two prospective seeds give `q_p/q_s = 0.942922` and `0.943109`: the candidate needs a **5.689–5.708% shorter period** to win in this synthetic workload. At W=256 the boundary approaches `16/17=0.941176`, corresponding to a **5.882% shorter period**, or **6.25% higher frequency**. The distinction between period reduction and frequency uplift is material. Bank conflicts, occupancy, and shared cap alter the boundary. These are **simulator boundaries**, not demonstrated physical clocks.

The shared-cap falsification is evaluated in waves per *physical time*, after candidate frequency conversion. Applying the same per-cycle cap before frequency conversion would fabricate an 11.11% gain in the saturated case; the independent self-test explicitly rejects that mistake.

## Physical decision and required next gate

The latest decoded V296 candidate pre-CTS setup slack was only +0.050206 ns at a +0.050000 ns guard, leaving **0.206 ps margin**. The matched decoded serial pre-CTS partner and the strongest independently optimized serial fifth-stage control have not yet established a full paired feasible Pareto comparison. The previous unretimed post-route candidate failed setup, hold and capacitance. Do not mix those evidence tiers.

**Reject the claim that decoder area reinvestment by itself creates a V296 GPU throughput gain.** The conditional 0.90× period result is a falsifiable physical target, not an achieved improvement. Continue only if independently audited, routed, matched-resource timing/area and dependency-aware workload data support a positive boundary. Preserve the no-win regimes and unopened real holdouts. V296 remains the sole provisional mechanism, V287 retired, Kernellum PR #119 untouched.
