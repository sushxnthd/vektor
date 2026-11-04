#!/usr/bin/env python3
"""Conditional throughput roofline kill test; not GPU/RTL evidence.

Candidate ceiling is compared with an OBSERVED equal-resource baseline rate.
Occupancy and control-overhead inputs must be justified as optimistic bounds:
overstating overhead or understating occupancy invalidates a kill.
"""
import argparse
import json

def bound(baseline_measured, candidate_bank, issue, output, memory, occupancy, overhead):
    values = (baseline_measured, candidate_bank, issue, output, memory, occupancy)
    if any(type(v) not in (int, float) or v <= 0 for v in values):
        raise ValueError("positive numeric rates required")
    if not 0 < occupancy <= 1 or not 0 <= overhead < 1:
        raise ValueError("invalid occupancy or overhead")
    base = baseline_measured
    ceiling = occupancy * (1-overhead) * min(candidate_bank, issue, output, memory)
    return {"baseline_measured":base, "candidate_ceiling":ceiling,
            "ceiling_over_baseline":ceiling/base,
            "conditional_kill":ceiling<=base}

def selftest():
    # Prospective synthetic regimes, NOT observations or workload holdouts.
    win=bound(0.75,2,2,2,2,0.75,0.05)
    no=bound(0.6,2,2,0.8,2,0.75,0.05)
    assert abs(win["ceiling_over_baseline"]-1.9)<1e-12
    assert not win["conditional_kill"]
    assert abs(no["ceiling_over_baseline"]-0.95)<1e-12
    assert no["conditional_kill"]
    assert bound(0.5,2,2,2,2,0.5,0)["ceiling_over_baseline"]==2
    for params in [(1,2,2,2,2,0,0),(1,2,2,2,2,1,1),(0,2,2,2,2,1,0)]:
        try: bound(*params)
        except ValueError: pass
        else: raise AssertionError(params)
    print(json.dumps({"predicted_bank_limited":win,"predicted_output_limited":no,
       "evidence":"synthetic conditional ceiling; no GPU, physical, or real-kernel validation",
       "warning":"A positive ceiling gap cannot establish a speedup. Kill is valid only if occupancy and overhead inputs are independently justified as candidate-favorable bounds."},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    a=p.parse_args()
    if a.selftest: selftest()
    else: p.error("use --selftest; no real measured baseline has been supplied")
