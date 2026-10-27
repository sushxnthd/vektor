# V296 deep-bank final-gate reconciliation and path-fraction kill boundary (2026-10-28)

## Decision

**No matched physically feasible D4 or D8 pair. V296 remains provisional; V287 stays retired.** This is an independent correction of the interpretation of original [run #40557136436](https://github.com/sushxnthd/vektor/actions/runs/40557136436), **not** a new OpenROAD measurement or a physical rescue.

An earlier [falsification report](DEEP_BANK_D4_D8_EXTRACTED_ROUTE_FALSIFICATION_20261028.md) incorrectly used the **250 ps setup optimization target** as the **final setup acceptance gate** when calculating the setup-recovery deficit and conditional clock-period bound. The frozen [D4/D8 preregistration](DEEP_BANK_D4_D8_ROUTED_PREREG_20261027.md) and actual `audit_tile_slice.py` instead require **final setup slack >= +50 ps**. The physical flow's `repair_timing -setup -slack_margin 0.250` is an optimization instruction, not the final feasibility test. The original JSON's `frozen_limits.min_setup_ns=0.25` encoded the more conservative target and should not override the actual gate. Preserve the old evidence unchanged; this report supersedes only its incorrect numerical interpretation.

## Corrected, exact arithmetic from original extracted-RC observations

| Completed design | Measured setup | Recovery to +50 ps final gate | Recovery to +250 ps repair target | Conditional period for +50 ps | Area headroom | Cap violations |
|---|---:|---:|---:|---:|---:|---:|
| D8 V296 pairwise | -684.592 ps | **734.592 ps** | 934.592 ps | **4.234592 ns** | 1,015.843 um² | 1 |
| D4 optimized serial | -1,316.510 ps | **1,366.510 ps** | 1,566.510 ps | **4.866510 ns** | 6,734.310 um² | 6 |

D4 V296 and D8 serial **timed out in detailed routing** and remain censored. Both completed designs fail the actual +50 ps setup gate and the zero-capacitance gate, so the corrected guard **does not change the rejection**. Neither cross-depth comparison nor a censored competitor can support a matched advantage.

The conditional periods assume the measured critical-path delay and skew remain unchanged under a clock-period change. They are **not measured Fmax**, and clock relaxation would violate the frozen 3.5 ns trial. D8 V296's 4.234592 ns conditional period corresponds to 236.15 MHz, versus the nominal 285.71 MHz; even if all else were fixed, preserving throughput would require **20.99% more useful work per cycle**. The existing same-clock matched admission model predicts zero per-slice work-per-cycle gain, not such a rescue.

## New necessary path-locality boundary for any repair

For original clock period `P`, measured setup slack `S`, final guard `G=0.050 ns`, and unchanged effective clock path/skew, define

`L=P-S`, `delta=max(0,G-S)`, `r=delta/L`.

Suppose a proposed repair can accelerate only fraction `f` of this **effective path-delay proxy**, by factor `s>=1`, with all other path terms fixed. Then a necessary condition to meet the actual gate is

`f(1-1/s) >= r`; equivalently `f>r` and `s>=f/(f-r)`.

This is an optimistic Amdahl-style necessary bound, not a physical sufficiency claim. It ignores rerouting, hold/cap repair, skew changes and other paths, so real feasibility can be harder.

| Design | Required fraction `r` | If only 25% modifiable | If 50% modifiable |
|---|---:|---:|---:|
| D8 V296 | **17.555%** | at least **3.358x** local speedup | at least **1.541x** |
| D4 serial | **28.371%** | **impossible** even with infinite local speedup | at least **2.312x** |

The D8 candidate has only **1,015.843 um²** (3.50% of its current final area) before the 30,000 um² ceiling; cap must also be repaired. This is a stringent three-way setup/area/cap gate. D16 V296 mapped area is already 27,861.638 um², leaving only 2,138.362 um² (7.675% of mapped area) for *all* net physical area growth if the same 30,000 um² cap were applied. That is a **conditional D16 budget**, not a routed D16 result.

## Next falsification gate, frozen before any further physical run

1. Recover exact **post-route extracted** worst-path startpoints, endpoints and per-segment delays from the completed D8 candidate and D4 serial original artifacts. Do not treat pre-CTS buffer counts as post-route path attribution.
2. Before changing RTL, quantify what fraction of each measured effective path is demonstrably controllable by the proposed **symmetric** repair. If the controllable fraction is <=17.555% for D8 candidate or <=28.371% for D4 serial, that repair is rejected under the fixed-path model even with infinite local speedup.
3. Require a plausible path-local speedup and cell-area cost **plus** a specific fix for the one D8 candidate and six D4 serial capacitance violations. Keep both contestants, RF ports, 3.5 ns clock, 2x RC, floorplan resources and final +50 ps guard unchanged.
4. Only then rerun both contestants at the same depth. Both must complete and pass extracted-RC setup, hold, cap, slew, DRC and area independently. A routing timeout or only one feasible design is **not** a win. If matched feasibility cannot be restored within the frozen budget, retire the V296 deep-bank implementation.

## Reproduction and evidence limitations

```bash
python3 research/v296/deep_bank_guard_reconciliation.py \
  research/v296/DEEP_BANK_D4_D8_EXTRACTED_ROUTE_FALSIFICATION_20261028.json \
  research/v296/audit_tile_slice.py \
  research/v296/deep_bank_postcts.py --self-test
```

The independent Decimal checker validates both gate definitions against actual repository source, checks the original observations, recomputes conditional bounds and path-fraction sensitivity, and rejects altered gate anchors and NaN. The checker was locally tested on a faithful fixture; repository-source hosted validation is a separate step. No workload holdouts opened, no GPU speedup or power claim, no new routed experiment. Kernellum PR #119 remains untouched.
