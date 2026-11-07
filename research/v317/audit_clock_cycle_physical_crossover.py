#!/usr/bin/env python3
"""V317 physical throughput break-even: measured routed area, conditional clock/work.

This is NOT timing closure. Both 2026-11-02 routes have electrical violations.
Compare equal useful work; a candidate wins iff cycles_c * period_c <
cycles_b * period_b. Area is a separate hard gate, not traded for IPC.
"""
from decimal import Decimal as D
from fractions import Fraction
import argparse, json

COMPACT_AREA=D("21314.6")
PAIRWISE_AREA=D("21324.7")
COMPACT_VIOLATIONS={"hold":6,"max_cap":14}
PAIRWISE_VIOLATIONS={"hold":0,"max_cap":21}

def boundary(candidate_cycles, baseline_cycles, baseline_period_ns,
             candidate_period_ns, candidate_area=PAIRWISE_AREA,
             baseline_area=COMPACT_AREA, candidate_violations=21,
             baseline_violations=20):
    assert min(candidate_cycles,baseline_cycles)>0
    assert min(candidate_period_ns,baseline_period_ns)>0
    cycle_ratio=D(candidate_cycles)/D(baseline_cycles)
    clock_ratio=D(candidate_period_ns)/D(baseline_period_ns)
    speedup=D(1)/(cycle_ratio*clock_ratio)
    return {"speedup":str(speedup),
            "required_candidate_period_ratio_strictly_below":str(D(1)/cycle_ratio),
            "cycle_ratio":str(cycle_ratio),
            "clock_period_ratio":str(clock_ratio),
            "area_delta_um2":str(candidate_area-baseline_area),
            "area_legal":candidate_area<=baseline_area,
            "electrically_legal":candidate_violations==0 and baseline_violations==0,
            "throughput_win":speedup>1,
            "all_gates_pass":speedup>1 and candidate_area<=baseline_area and
                             candidate_violations==0 and baseline_violations==0}

def test():
    # 10% cycle reduction tolerates <11.111...% period penalty.
    x=boundary(90,100,D("1"),D("1.10"))
    assert x["throughput_win"] and not x["all_gates_pass"]
    y=boundary(90,100,D("1"),D("1.12"))
    assert not y["throughput_win"]
    z=boundary(100,100,D("1"),D("1"))
    assert not z["throughput_win"]
    assert D(z["area_delta_um2"])==D("10.1")
    assert not z["electrically_legal"]
    print("PASS: clock/cycle crossover, area and electrical negative controls")
    print("MEASURED: pairwise 10.1 um2 larger; compact 20 and pairwise 21 violations")
    print("LIMIT: no new physical timing, repaired routing or GPU workload measurements")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--baseline-cycles",type=int)
    p.add_argument("--candidate-cycles",type=int)
    p.add_argument("--baseline-period-ns")
    p.add_argument("--candidate-period-ns")
    a=p.parse_args()
    if a.selftest: test()
    else:
        if None in (a.baseline_cycles,a.candidate_cycles,a.baseline_period_ns,a.candidate_period_ns):
            p.error("provide all four workload and timing inputs or --selftest")
        print(json.dumps(boundary(a.candidate_cycles,a.baseline_cycles,D(a.baseline_period_ns),
                                  D(a.candidate_period_ns)),indent=2))
