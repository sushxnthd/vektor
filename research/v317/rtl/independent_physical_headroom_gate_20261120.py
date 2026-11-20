#!/usr/bin/env python3
"""Independent physical-headroom gate for V317 development-only observations.

This checker intentionally does not import the scheduler simulator and does not
open prospective holdouts. It verifies a necessary, not sufficient, boundary.
"""
from math import isfinite

SEED_RATIOS = {
    20261121: 1.000009115360,
    20261122: 0.999919909597,
    20261123: 0.999751245871,
    20261124: 1.000058828344,
}
MATERIALITY = 1.02

def upper_bound(service_ratio, clock_ratio=1.0, occupancy_ratio=1.0,
                bandwidth_ratio=float("inf")):
    """Optimistic throughput ceiling, ignoring all extra control costs.

    Ratios are relative to an equal-resource compact-greedy reference.
    service*clock*occupancy bounds compute-side issue capacity;
    bandwidth_ratio bounds delivered traffic throughput.
    """
    assert all(isfinite(x) and x > 0 for x in
               (service_ratio, clock_ratio, occupancy_ratio))
    assert bandwidth_ratio > 0
    return min(service_ratio * clock_ratio * occupancy_ratio, bandwidth_ratio)

def required_service(materiality=MATERIALITY, clock_ratio=1.0,
                     occupancy_ratio=1.0, bandwidth_ratio=float("inf")):
    if bandwidth_ratio < materiality:
        return float("inf")
    return materiality / (clock_ratio * occupancy_ratio)

def main():
    assert len(SEED_RATIOS) == 4
    assert max(SEED_RATIOS.values()) < MATERIALITY
    assert upper_bound(max(SEED_RATIOS.values())) < MATERIALITY
    assert upper_bound(1.05, 0.95, 0.98, 2.0) < MATERIALITY
    assert required_service(clock_ratio=0.95, occupancy_ratio=0.98) > 1.09
    assert required_service(bandwidth_ratio=1.01) == float("inf")
    assert upper_bound(1.5, 1.0, 1.0, 1.01) == 1.01
    print("PASS: independent necessary physical-headroom boundary; "
          "development policy no-go; prospective holdouts untouched")

if __name__ == "__main__":
    main()
