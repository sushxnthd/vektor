#!/usr/bin/env python3
"""V317 prospective throughput-per-area boundary; conditional, NOT signoff.

A pairwise controller with grant-identical scheduling cannot claim additional
work/cycle from arbiter implementation alone. This checker exposes exactly how
much *independently measured* useful service would be required to overcome
area, clock, occupancy and bandwidth constraints. All example numbers are
historical cross-run observations and MUST NOT be accepted as physical proof.
"""
from dataclasses import dataclass
from math import isfinite
import json

@dataclass(frozen=True)
class Inputs:
    base_area: float
    candidate_area: float
    base_period: float
    candidate_period: float
    base_service_per_cycle: float
    candidate_service_per_cycle: float
    base_occupancy: float
    candidate_occupancy: float
    bandwidth_cap_per_ns: float

def throughput_per_area(x):
    values = vars(x).values()
    if any(not isinstance(v, (int, float)) or isinstance(v, bool)
           or not isfinite(v) for v in values):
        raise ValueError("nonfinite or nonnumeric input")
    if min(x.base_area, x.candidate_area, x.base_period,
           x.candidate_period, x.base_service_per_cycle,
           x.candidate_service_per_cycle) <= 0:
        raise ValueError("positive physical quantities required")
    if not (0 < x.base_occupancy <= 1 and 0 < x.candidate_occupancy <= 1):
        raise ValueError("occupancy must be in (0,1]")
    if x.bandwidth_cap_per_ns <= 0:
        raise ValueError("positive bandwidth required")
    b = min(x.base_service_per_cycle*x.base_occupancy/x.base_period,
            x.bandwidth_cap_per_ns)
    c = min(x.candidate_service_per_cycle*x.candidate_occupancy/x.candidate_period,
            x.bandwidth_cap_per_ns)
    return (c/x.candidate_area)/(b/x.base_area)

def required_candidate_service(x, target=1.02):
    """Exact minimum service/cycle for target, or None if bandwidth forbids it."""
    if not isfinite(target) or target <= 0:
        raise ValueError("invalid target")
    throughput_per_area(x)  # validate
    b = min(x.base_service_per_cycle*x.base_occupancy/x.base_period,
            x.bandwidth_cap_per_ns)
    required_rate = target*b*x.candidate_area/x.base_area
    if required_rate > x.bandwidth_cap_per_ns:
        return None
    return required_rate*x.candidate_period/x.candidate_occupancy

def selftest():
    # Frozen constructed predicted-win: unbounded bandwidth and +5% service.
    win = Inputs(100, 100, 2, 2, 1, 1.05, 1, 1, 100)
    assert abs(throughput_per_area(win)-1.05)<1e-12
    # Frozen predicted-no-win: both paths limited by the same output port.
    capped = Inputs(100, 100, 2, 2, 1, 1.05, 1, 1, .4)
    assert throughput_per_area(capped)==1
    assert required_candidate_service(capped, 1.02) is None
    # Stronger compact comparator: same grants and clock, pairwise larger.
    equal = Inputs(21314.6, 21324.7, 2.2, 2.2, 1, 1, 1, 1, 100)
    assert throughput_per_area(equal)<1
    # A clock improvement is not a service improvement if occupancy erases it.
    lost = Inputs(100, 100, 2.24, 2.20, 1, 1, 1, .95, 100)
    assert throughput_per_area(lost)<1
    # A legal physical run is NOT supplied here; historical mixed-run clocks.
    historical = Inputs(21314.6,21324.7,2.24,2.20,1,1,1,1,100)
    assert throughput_per_area(historical)<1.02
    assert required_candidate_service(historical,1.02)>1
    for value in (float('nan'),float('inf'),-1):
        try:
            throughput_per_area(Inputs(100,100,2,2,1,1,1,1,value))
        except ValueError:
            pass
        else:
            raise AssertionError("invalid bandwidth accepted")
    return {
        "constructed_win":throughput_per_area(win),
        "constructed_bandwidth_no_win":throughput_per_area(capped),
        "equal_service_equal_clock_compact_dominates":throughput_per_area(equal),
        "occupancy_erases_clock":throughput_per_area(lost),
        "historical_cross_run_conditional_only":throughput_per_area(historical),
        "required_service_for_2pct_historical_only":required_candidate_service(historical),
        "physical_acceptance":"BLOCKED: both routes electrically illegal; DRC unverified"
    }

if __name__=="__main__":
    print(json.dumps(selftest(),indent=2,sort_keys=True))
