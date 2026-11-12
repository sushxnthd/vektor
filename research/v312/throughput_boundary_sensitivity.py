#!/usr/bin/env python3
"""V312 necessary throughput boundary from frozen synthetic admissions.

Upper-bound model only: not a cycle-accurate GPU or timing result.
f = fraction of baseline time limited by RF issue admission.
d = candidate/base tile-clock period ratio (>=1 means slower).
c = extra normalized control/occupancy overhead (>=0).
b = independent bandwidth/port speedup ceiling (>=1).
Upper bound S <= min(1/((1-f)+f/G), b)/(d*(1+c)).
"""
import json, sys

def bound(g,f,d=1.,c=0.,b=float("inf")):
    assert g>=1 and 0<=f<=1 and d>0 and c>=0 and b>=1
    return min(1/((1-f)+f/g),b)/(d*(1+c))

def main():
    with open(sys.argv[1],encoding="utf-8") as fh: evidence=json.load(fh)
    out={}
    for regime,row in evidence["regimes"].items():
        g=row["predicted_gain"]
        out[regime]={"issue_gain":g,"sensitivity":[]}
        for f in (.25,.5,.75,1.):
            ideal=bound(g,f)
            out[regime]["sensitivity"].append({
                "issue_limited_fraction":f,
                "ideal_no_overhead_speedup_upper":ideal,
                "max_clock_period_ratio_for_10pct_speedup":ideal/1.10,
                "with_5pct_clock_penalty_and_2pct_control_overhead":bound(g,f,1.05,.02),
                "with_5pct_clock_penalty_and_1p10_bandwidth_ceiling":bound(g,f,1.05,0.,1.10)
            })
    # Physical falsification controls, including a bandwidth-limited no-win.
    assert bound(1.0,.75,1.05)<1.0
    assert bound(1.95,.5,1.05,.02,1.0)<1.0
    assert bound(1.2685676392572944,.5,1.05,.02)<1.10
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
