#!/usr/bin/env python3
"""Independent necessary-condition physical dominance check; not a routed GPU result.

This is a falsification/sensitivity bound, not evidence of electrical closure.
Inputs are the previously reported OpenROAD RF-proxy cell areas, not fresh measurements.
"""
from fractions import Fraction

COMPACT_AREA = Fraction("21314.6")
PAIRWISE_AREA = Fraction("21324.7")
MIN_MATERIAL_GAIN = Fraction("1.02")

def required_service_ratio(pairwise_period_over_compact, extra_area=0, required_gain=MIN_MATERIAL_GAIN):
    """Minimum pairwise/compact service per cycle for gain in throughput/total area."""
    a0 = COMPACT_AREA + Fraction(str(extra_area))
    a1 = PAIRWISE_AREA + Fraction(str(extra_area))
    return required_gain * Fraction(str(pairwise_period_over_compact)) * a1 / a0

def required_clock_ratio(service_ratio, extra_area=0, required_gain=MIN_MATERIAL_GAIN):
    a0 = COMPACT_AREA + Fraction(str(extra_area))
    a1 = PAIRWISE_AREA + Fraction(str(extra_area))
    return Fraction(str(service_ratio)) * a0 / (required_gain * a1)

def main():
    assert PAIRWISE_AREA > COMPACT_AREA
    assert required_service_ratio(1) > MIN_MATERIAL_GAIN
    assert required_clock_ratio(1) < Fraction(1, 1) / MIN_MATERIAL_GAIN
    for extra in (0, 10000, 100000):
        print("identical_extra_tile_area_um2", extra)
        for clock in ("0.95", "1.00", "1.05", "1.10"):
            print("period_ratio", clock, "minimum_service_ratio_for_2pct_gain",
                  f"{float(required_service_ratio(clock, extra)):.9f}")
        print("equal_service_max_period_ratio_for_2pct_gain",
              f"{float(required_clock_ratio(1, extra)):.9f}")
    print("PASS: necessary conditions only; both existing routes have electrical violations")
if __name__ == "__main__":
    main()
