# V296 warp-scoreboard latency and RF-port falsification (2026-10-26)

## Evidence tier and decision

**SYNTHETIC PROSPECTIVE SCOREBOARD TRANSFER, NOT PHYSICAL GPU PERFORMANCE.** Frozen protocol commit `62dd5e2c` preceded evaluation of seeds 91371/91372. A one-outstanding-operation-per-warp model with 16 banks, two read ports/bank, four issue slots and deterministic rotating-priority admission compares the unretimed serial-equivalent L=1 path against the symmetric operand-capture L=2 path. Same per-warp request streams and resources. The prior physical gate is unchanged: both original post-route designs failed setup/hold/capacitance; both retimed pre-CTS variants failed +50 ps setup guard. No feasible clock ratio is measured.

## Necessary occupancy law

With W active warps, one outstanding dependent operation per warp, issue width I, and completion latency L cycles:

    Q <= min(I, W/L) operations/cycle.

This is a conservation **upper bound**, not a sufficient prediction. RF conflicts, scheduler ordering, readiness, and bandwidth can lower Q. With equal clock, candidate/serial compute throughput ratio is Q2/Q1. Under a *hypothetical* feasible clock ratio r=f_candidate/f_serial, the necessary synthetic break-even condition is:

    r > Q1 / Q2.

A full GPU law would also require measured mask overlap, bank compatibility, bandwidth, occupancy, control, and realistic power/clock. Here Q1/Q2 is estimated by a port-exact synthetic replay; it is not a physically demonstrated frequency gain.

## Frozen unseen synthetic results

The first bank is fixed to bank 0 with probability h, otherwise uniform over 16 banks. The second bank equals the first with probability 0.2, otherwise uniform. Each warp has a pre-generated 25,000-operation sequence. Warmup 2,000 cycles, measurement 18,000 cycles. Equal clock for measured simulator comparisons. The +5% frequency column is a **counterfactual** sensitivity, not a measurement.

| Warps | h | Seed | Serial issued / 18k | L=2 issued / 18k | Equal-clock change | Hypothetical +5% clock change | Break-even r |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0.0 | 91371 | 35,128 | 18,000 | -48.759% | -46.197% | 1.951556 |
| 4 | 0.0 | 91372 | 65,799 | 35,413 | -46.180% | -43.489% | 1.858046 |
| 8 | 0.0 | 91371 | 71,977 | 66,987 | -6.933% | -2.279% | 1.074492 |
| 16 | 0.0 | 91372 | 72,000 | 72,000 | 0.000% | +5.000% | 1.000000 |
| 32 | 0.0 | 91371 | 72,000 | 72,000 | 0.000% | +5.000% | 1.000000 |
| 8 | 0.8 | 91372 | 34,916 | 34,852 | -0.183% | +4.808% | 1.001836 |
| 16 | 0.8 | 91371 | 35,163 | 35,152 | -0.031% | +4.967% | 1.000313 |
| 32 | 0.8 | 91372 | 35,061 | 35,036 | -0.071% | +4.925% | 1.000714 |

**All eight frozen qualitative predictions passed locally.** At low occupancy, the extra latency is disastrous; at >=16 warps with distributed banks, occupancy hides the latency completely; under a severe hot-bank bottleneck, bank ports, not the scoreboard, dominate. This is a negative/conditional result for retiming, not a positive V296 GPU-speedup result. The previous synchronized-batch model overgeneralizes if applied to per-warp independent chains: occupancy and bank contention materially change the dependency penalty.

## Checks and reproducibility

- Executable: `python3 research/v296/warp_latency_port_boundary.py --self-test --evaluate`. A separate event-list scheduler compares exact per-cycle issue histograms on nine short random traces (3/5/7 warps, latencies 1/2/3); one/two-warp constant-bank cases match exact occupancy rates.
- All 8 cells use the same per-warp requests across L=1 and L=2; per-bank port occupancy is asserted <=2; per-warp in-order issue is enforced by a single outstanding operation.
- Every observed Q is below the independent conservation ceiling `min(4,W/L)`. The finite-window sample is deterministic, not a confidence interval for real workloads.
- Hosted CI: `.github/workflows/v296-warp-scoreboard-latency.yml`; hosted outcome pending at report creation.
- Strong equal-resource serial control and V296 have identical *admission arbitration* at fixed ready masks. Differences here arise solely from the **symmetric extra pipeline latency**, not an invented issue-capacity benefit.
- No new RTL hazard logic was added; the current tile-slice RTL testbench does **not** prove scoreboard behavior. No mask-overlap model, cache hierarchy, inter-warp divergence, bypass network, dynamic energy, SRAM macro, extracted RC, or signoff is included.

## Falsification implications

1. The physical candidate still misses the frozen pre-CTS setup guard by 75.959 ps. Until routed closure and the strongest independently optimized serial control are demonstrated, the hypothetical +5% clock sensitivity must not be interpreted as a gain.
2. Under one outstanding dependent instruction per warp, low occupancy creates a clock-break-even requirement of roughly 1.86-1.95x for W=2-4. This is an *observed synthetic* requirement, not a general GPU constant.
3. Bank pressure can make latency nearly irrelevant, but then port pressure also limits any benefit from more slices or faster arbitration. A candidate cannot claim both an occupancy-hidden latency penalty and unlimited bandwidth.
4. The next physically decisive step remains a symmetric scheduler-to-RF operand-selection repair with extracted timing and electrical checks, followed by a dependency-aware, port-accurate comparison at **feasible measured clocks**.
5. Keep the existing V296 branch/draft PR and all negative artifacts. V287 remains retired; Kernellum PR #119 and sealed real holdouts remain untouched.

**World-class completion gate: NOT REACHED.** No measured GPU throughput, power improvement, final routed closure, or RTX-5090 equivalence is claimed.
