# V296: finite-occupancy break-even law rejects free one-cycle retiming (2026-10-28)

**Evidence tier:** exact stationary finite-state analysis and independent seeded synthetic Monte Carlo. **Not RTL, synthesis, physical signoff, actual GPU traces, or a demonstrated V296 gain.** This result addresses whether a *symmetric* extra-cycle RF retiming could recover enough clock frequency to offset its occupancy cost. It does not replace the sole V296 mechanism or revive V287.

## Question and positive law

The original D8 V296 extracted path misses the frozen +50 ps setup guard by **734.592 ps**; D4 optimized serial misses by **1366.510 ps**, but these are different RF depths and cannot be compared as a matched pair. Naive delayed RF reads were separately falsified by read-before-write collisions. Even if a functionally correct, equal-port repair were found, an extra cycle may lower sustained useful work per second.

Model N identical closed-loop resident waves, independent per-ready-wave admission eligibility q, B global admissions per cycle, and deterministic L-cycle residence after admission. Each ready wave independently becomes eligible with probability q; a fixed-priority controller grants at most B eligible waves. After a grant, that wave cannot reissue for L-1 cycles. No additional waves arrive, and no instruction dependencies, memory traces, write hazards, bank correlations, or physical wire loads are modeled. In this abstract model, **the exact single-wave law** is

T(N=1,B>=1,L,q) = q / [1 + q(L-1)] waves/cycle.

For N>1, enumerate all L^N cooldown states, each eligible subset, and its transition probability. Compute the stationary reward (expected grants/cycle). This is an exact finite-state *model law*, not a closed-form universal GPU throughput formula. The simple resource ceiling T <= min(B, N/L, Nq) is necessary but not generally tight. The necessary frequency gain for an extra-cycle design to improve **waves per second** at unchanged workload parameters is

f_new / f_old > T_old / T_new.

Equality gives zero throughput gain. This is a quantitative rejection threshold for any proposed extra-latency physical repair. A frequency gain below the threshold is a no-win for that workload regime under the stated model.

## Executed independent validation

The script implements a stationary Markov enumerator and a separate cycle-by-cycle random simulation (seeds 101 and 911, 200,000 cycles/seed/regime). All eight preselected **exploratory synthetic** regimes passed a frozen-in-code absolute prediction tolerance of 0.012 waves/cycle. The maximum observed error was **0.00159 waves/cycle**. The code also tests the single-wave renewal formula at 12 q/L combinations and exact single-cycle control identities. No real workload holdout was opened; this is not a prospectively preregistered GPU test.

| Regime (N, B, L, q) | Exact waves/cycle | Simple ceiling | Max simulation error |
|---|---:|---:|---:|
| Low population (1,1,3,0.55) | 0.26190 | 0.33333 | 0.00041 |
| Occupancy limited (2,2,3,0.90) | 0.64286 | 0.66667 | 0.00013 |
| Bandwidth saturated (4,1,2,0.90) | 0.99900 | 1.00000 | 0.00014 |
| Eligibility sparse (4,2,2,0.20) | 0.65257 | 0.80000 | 0.00034 |
| Balanced (4,2,3,0.55) | 1.02241 | 1.33333 | 0.00055 |
| Deep latency (4,2,4,0.85) | 0.95237 | 1.00000 | 0.00033 |
| Single-cycle control (4,1,1,0.55) | 0.95899 | 1.00000 | 0.00077 |
| Port-rich control (4,4,1,0.55) | 2.20000 | 2.20000 | 0.00159 |

## Extra-cycle physical repair: conditional break-even predictions

All comparisons keep N, B and q fixed, changing only L=1 to L=2. A clock ratio strictly above the threshold is necessary to overcome the modeled occupancy penalty. These are **prospective predictions for later independent workload validation**, not real traces or physical frequency measurements.

| Workload regime | L=1 waves/cycle | L=2 waves/cycle | Necessary f_new/f_old |
|---|---:|---:|---:|
| Scarce occupancy: N=2, B=2, q=0.90 | 1.80000 | 0.94737 | **>1.9000x** |
| Shared bandwidth: N=4, B=1, q=0.90 | 0.99990 | 0.99900 | **>1.0009x** |
| Sparse eligibility: N=4, B=2, q=0.20 | 0.77120 | 0.65257 | **>1.1818x** |
| Balanced: N=4, B=2, q=0.55 | 1.71751 | 1.33473 | **>1.2868x** |

**Interpretation:** an extra cycle is particularly damaging with few resident waves and abundant ports; it is nearly free when a shared bandwidth cap is already saturated. A retiming proposal that shows only a few percent of clock improvement cannot be called a general throughput win. Even a clock improvement exceeding a boundary is not sufficient for V296 superiority, since the optimized serial baseline must receive the same repair and still pass area, hold, cap, slew and route checks.

## Decision and next falsification

Do not pursue an extra-cycle delayed-RF fix solely because it improves setup. First require a two-read-port, read-before-write-correct RTL and matched **same-depth** serial control. Quantify the actual change in instruction latency, occupancy, issue rate, and clock period; compare against the exact model on **new, sealed, correlated workload traces** and a strong trace-replay baseline. Reject a repair if its measured clock ratio does not clear the appropriate workload break-even boundary, or if routed timing, area, electrical constraints or shared bandwidth erase its gain. The fixed-priority independent-q abstraction must not be extrapolated to temporally correlated GPU traces without new validation.

The previously frozen V296 high-occupancy predicted-win and shared-bandwidth predicted-no-win regimes are not redefined here. No physical benefit, power benefit, tile-level throughput advantage or RTX-5090 equivalence is claimed. Kernellum #119 and its holdouts remain untouched.

Reproduce: python3 research/v296/v296_occupancy_latency_law.py --self-test --output /tmp/v296_occupancy_latency.json.
