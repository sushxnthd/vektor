"""Necessary (not sufficient) physical throughput-win certificate for V317.
Conditional analytical bound, NOT routed or benchmark evidence.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Inputs:
    cycle_ratio: float
    clock_ratio: float
    occupancy_ratio: float
    traffic_ratio: float
    bandwidth_ratio: float
    overhead_ratio: float = 0.0

def upper_bound_speedup(x: Inputs) -> float:
    vals = (x.cycle_ratio,x.clock_ratio,x.occupancy_ratio,x.traffic_ratio,x.bandwidth_ratio,x.overhead_ratio)
    assert all(isfinite(v) for v in vals)
    assert min(vals[:5]) > 0 and x.overhead_ratio >= 0
    compute=x.clock_ratio*x.occupancy_ratio/(x.cycle_ratio+x.overhead_ratio)
    memory=x.bandwidth_ratio/x.traffic_ratio
    return max(compute,memory)

def guaranteed_no_win(x: Inputs) -> bool:
    return upper_bound_speedup(x) <= 1.0

def actual_speedup(x: Inputs, baseline_compute_s: float, baseline_memory_s: float) -> float:
    assert baseline_compute_s > 0 and baseline_memory_s > 0
    candidate_compute=baseline_compute_s*(x.cycle_ratio+x.overhead_ratio)/(x.clock_ratio*x.occupancy_ratio)
    candidate_memory=baseline_memory_s*x.traffic_ratio/x.bandwidth_ratio
    return max(baseline_compute_s,baseline_memory_s)/max(candidate_compute,candidate_memory)

def test():
    cases=[Inputs(1,.9758,1,1,1),Inputs(.9,.9758,1,1,1),
           Inputs(.9,.9758,.8,1.25,1),Inputs(.9,.9758,1,1.25,.75),
           Inputs(.9,.9758,1,1,1,.15)]
    n=0
    for x in cases:
        ceiling=upper_bound_speedup(x)
        for k in range(-40,41):
            ratio=2.0**(k/4)
            observed=actual_speedup(x,1,ratio)
            assert observed <= ceiling+1e-12
            if guaranteed_no_win(x): assert observed <= 1+1e-12
            n+=1
    x=Inputs(.9,.9758,1,1.25,1)
    assert actual_speedup(x,1,100)==.8
    assert upper_bound_speedup(x)>1 and actual_speedup(x,1,100)<1
    print(f'PASS {n} deterministic roofline upper-bound checks; no new hardware evidence')

if __name__=='__main__': test()
