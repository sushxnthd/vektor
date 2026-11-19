# Conditional service-ceiling boundary — 2026-11-19

## Status

This is a **new sensitivity/falsification analysis over existing V317 oracle evidence**, not a new GPU measurement and not a new architecture mechanism. It does not supersede the compact-greedy physical falsification. V317's positive integrated-tile area/throughput interpretation remains killed until a new matched implementation is electrically legal and materially better.

## Boundary

For the same request distribution and the same bank-port resources, define:

- `r_s`: instantaneous service ratio versus the strong compact-greedy control;
- `r_f`: clock-frequency ratio;
- `r_o`: occupancy/availability ratio;
- `r_b`: independently established bandwidth ceiling.

Under the explicit proportional-service assumption,

`G <= min(r_b, r_s * r_f * r_o)`.

For the frozen 2% materiality threshold `T = 1.02`, a material gain is impossible whenever either:

1. `r_b < 1.02`; or
2. `r_f * r_o < 1.02 / r_s`.

This is a **necessary**, not sufficient, condition. It cannot be transferred to latency-limited, changed-distribution or different-queueing workloads without independent validation.

## Existing four-slot oracle evidence mapped onto the boundary

| Regime | Existing oracle/greedy service ceiling | Required `r_f*r_o` for 2% | Equal-clock/equal-occupancy verdict |
|---|---:|---:|---|
| uniform 16-bank | 1.001025 | 1.0189556 | FALSIFIED |
| 70% same-bank | 1.002278 | 1.0176817 | FALSIFIED |
| uniform 4-bank | 1.046683 | 0.9745071 | POSSIBLE, conditional |
| 65% hot-bank | 1.099869 | 0.9273832 | POSSIBLE, conditional |

The first two regimes cannot reach the frozen 2% threshold at equal clock and occupancy even with the zero-cost unfair oracle. The latter two only remain candidates if the implementation retains enough clock/occupancy and at least a 1.02 bandwidth ratio.

## Frozen next-test predictions

**Predicted no-win regime:** uniform 16-bank traffic. Under equal ports and the same distribution, no same-clock/equal-occupancy scheduler constrained by the four-slot oracle ceiling can produce a >=2% service gain.

**Predicted potential-win regime:** 65% hot-bank traffic. A >=2% gain is only possible if a future legal implementation satisfies both `r_f*r_o >= 0.9273832` and `r_b >= 1.02`. Failure of either condition kills the positive case before any GPU-throughput extrapolation.

These predictions are frozen before any new physical or workload evaluation derived from this boundary.

## Required physical gate before promotion

A future mechanism may only be promoted if it simultaneously demonstrates:

1. matched-resource electrically legal RTL/P&R against compact greedy;
2. setup/hold/max-cap legality and reproducible raw artifacts;
3. matched area and a bounded energy/power proxy;
4. measured or independently simulated workload service consistent with the frozen boundary;
5. no hidden occupancy or bandwidth penalty large enough to cross the kill boundary;
6. transfer to an unseen workload regime.

The exact-rational checker is `research/v317/rtl/conditional_service_ceiling_20261119.py`.

No SRAM-macro GPU tile, GPU IPC, calibrated power or RTX-5090-equivalence claim is made.
