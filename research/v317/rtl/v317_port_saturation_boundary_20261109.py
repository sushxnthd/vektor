#!/usr/bin/env python3
"""Predeclared RF-port-limited boundary sweep for V317; analytic upper bound only.

No GPU throughput claim. Models a two-read-port bank and a contender whose
additional scheduling logic cannot create physical read bandwidth.
"""
from fractions import Fraction as F
from itertools import product

COMPACT_AREA = F("21314.6")
PAIRWISE_AREA = F("21324.7")
TARGET = F("1.02")
PORTS = 2

def bound(compatibility, overlap, offered_reads, occupancy, control_cycles,
          clock_ratio=1, extra_tile_area=0):
    """Optimistic service/area upper bound; occupancy in [0,1].

    Pairing saves one scheduling cycle for compatible, disjoint requests,
    but cannot save operand reads. This is deliberately generous: assumes
    zero pairing hardware cost beyond measured controller area and no
    extra switching/retention cost.
    """
    p, o, r, q, h, t = map(lambda x: F(str(x)),
                          (compatibility, overlap, offered_reads, occupancy,
                           control_cycles, clock_ratio))
    assert 0 <= p <= 1 and 0 <= o <= 1 and 0 < r and 0 < q <= 1
    assert h >= 0 and t > 0 and extra_tile_area >= 0
    # baseline cycles: one issue per request, or reads/ports, whichever dominates
    baseline = max(F(1), r / PORTS) / q
    # theoretical issue-cycle savings only for compatible nonoverlapping masks
    proposed = max(F(1) - p * (1-o) / 2, r / PORTS) / q + h
    speedup = baseline / proposed / t
    area_factor = (COMPACT_AREA + F(str(extra_tile_area))) / (PAIRWISE_AREA + F(str(extra_tile_area)))
    return speedup * area_factor

def main():
    # Frozen prospective predictions: these regimes must not be changed after
    # observing workload traces; analytic outcomes are not measurements.
    regimes = {
        "predicted_win_issue_limited": dict(compatibility="0.9", overlap="0.05",
            offered_reads="1", occupancy="0.9", control_cycles="0.01"),
        "predicted_no_win_port_limited": dict(compatibility="0.9", overlap="0.05",
            offered_reads="4", occupancy="0.9", control_cycles="0.01"),
    }
    for name, params in regimes.items():
        result = bound(**params)
        print(name, "optimistic_throughput_per_area", float(result),
              "crosses_2pct", result >= TARGET)
    assert bound(**regimes["predicted_win_issue_limited"]) > TARGET
    assert bound(**regimes["predicted_no_win_port_limited"]) < 1
    # When ports dominate, compatibility cannot increase service capacity.
    for p, o, q, h in product(("0", "0.5", "1"), ("0", "0.5", "1"),
                               ("0.5", "1"), ("0", "0.1")):
        result = bound(p, o, "4", q, h)
        assert result <= COMPACT_AREA / PAIRWISE_AREA
    # More wiring delay cannot improve the throughput-per-area result.
    for params in regimes.values():
        assert bound(**params, clock_ratio="1.05") < bound(**params)
    print("PASS: prospective optimistic bound; physical/electrical closure NOT established")

if __name__ == "__main__":
    main()
