#!/usr/bin/env python3
"""Independent falsification: equal bandwidth in useful-ops/ns is not implied by equal byte/s.

The existing v317_bandwidth_occupancy_boundary_20261110.py uses a shared
bandwidth_cap_per_ns in units of useful operations/ns. That conversion is only
valid when both architectures transfer the same bytes per useful operation.
This audit supplies an explicit traffic-aware bound. Synthetic counterexamples
are NOT physical measurements and cannot override electrical signoff.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Variant:
    area: float
    period_ns: float
    useful_ops_per_cycle: float
    occupancy: float
    bytes_per_useful_op: float

def useful_rate(v, bandwidth_bytes_per_ns):
    vals = (v.area, v.period_ns, v.useful_ops_per_cycle,
            v.occupancy, v.bytes_per_useful_op, bandwidth_bytes_per_ns)
    if any(not isinstance(x, (float, int)) or isinstance(x, bool)
           or not isfinite(x) or x <= 0 for x in vals):
        raise ValueError("all inputs must be finite and positive")
    if v.occupancy > 1:
        raise ValueError("occupancy exceeds one")
    return min(v.useful_ops_per_cycle*v.occupancy/v.period_ns,
               bandwidth_bytes_per_ns/v.bytes_per_useful_op)

def ratio(base, candidate, bandwidth_bytes_per_ns):
    return ((useful_rate(candidate, bandwidth_bytes_per_ns)/candidate.area) /
            (useful_rate(base, bandwidth_bytes_per_ns)/base.area))

def audit():
    base = Variant(100, 2, 1, 1, 1)
    # Same area and issue rate, but twice the traffic per useful operation.
    traffic_heavy = Variant(100, 2, 1, 1, 2)
    assert ratio(base, traffic_heavy, .4) == .5
    # A 5% issue-service gain is erased by the candidate's larger traffic.
    issue_win = Variant(100, 2, 1.05, 1, 2)
    assert ratio(base, issue_win, .4) == .5
    # At high bandwidth, the intended issue-service advantage returns.
    assert abs(ratio(base, issue_win, 100)-1.05) < 1e-12
    # If bytes/useful-op match, the shared useful-op bandwidth cap is valid.
    same_traffic = Variant(100, 2, 1.05, 1, 1)
    assert ratio(base, same_traffic, .4) == 1
    # Pairwise vs competent compact: same service, larger area.
    compact = Variant(21314.6, 2.2, 1, 1, 1)
    pairwise = Variant(21324.7, 2.2, 1, 1, 1)
    assert ratio(compact, pairwise, 100) < 1
    return "PASS: five synthetic controls; traffic-dependent boundary falsifies shared-cap assumption"

if __name__ == "__main__":
    print(audit())
