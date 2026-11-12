"""Fail-closed matched physical/workload acceptance gate. No fabricated measurements."""
from decimal import Decimal
import json, sys
MATCH = ("experiment_id","library_sha","constraints_sha","corner","routing_mode","workload_sha")
LEGAL = ("max_cap_violations","max_slew_violations","drc_violations")
def dec(x):
    if isinstance(x,bool) or x is None: raise ValueError("invalid numeric evidence")
    y=Decimal(str(x))
    if not y.is_finite(): raise ValueError("nonfinite evidence")
    return y
def evaluate(pair):
    try:
        c,b=pair["candidate"],pair["baseline"]
        for k in MATCH:
            if not c.get(k) or c[k]!=b.get(k): raise ValueError("missing or mismatched "+k)
        if not c.get("rtl_sha") or not b.get("rtl_sha") or c["rtl_sha"]==b["rtl_sha"]:
            raise ValueError("missing or identical RTL provenance")
        for r in (c,b):
            if not r.get("post_route_extracted_rc"): raise ValueError("missing extracted RC")
            if dec(r["setup_wns_ns"])<0 or dec(r["hold_wns_ns"])<0:
                raise ValueError("timing violation")
            for k in LEGAL:
                n=dec(r[k])
                if n!=0: raise ValueError("electrical/DRC violation: "+k)
            for k in ("area_um2","period_ns","workload_cycles","workload_completed"):
                if dec(r[k])<=0: raise ValueError("nonpositive "+k)
        if dec(c["workload_completed"])!=dec(b["workload_completed"]):
            raise ValueError("unmatched completed work")
        ratio=(dec(b["workload_cycles"])*dec(b["period_ns"])*dec(b["area_um2"]))/(dec(c["workload_cycles"])*dec(c["period_ns"])*dec(c["area_um2"]))
        return {"decision":"WIN" if ratio>1 else "NO_WIN","throughput_per_area_ratio":str(ratio)}
    except (KeyError,TypeError,ValueError,ArithmeticError) as e:
        return {"decision":"INSUFFICIENT_OR_ILLEGAL","reason":str(e)}
def test():
    common=dict(experiment_id="frozen",library_sha="lib",constraints_sha="sdc",corner="ss",routing_mode="detailed",workload_sha="w",post_route_extracted_rc=True,setup_wns_ns=0,hold_wns_ns=0,max_cap_violations=0,max_slew_violations=0,drc_violations=0,area_um2=100,period_ns=1,workload_completed=1000,workload_cycles=1000)
    c=dict(common,rtl_sha="c",workload_cycles=900)
    b=dict(common,rtl_sha="b")
    assert evaluate(dict(candidate=c,baseline=b))["decision"]=="WIN"
    c["area_um2"]=120
    assert evaluate(dict(candidate=c,baseline=b))["decision"]=="NO_WIN"
    c["area_um2"]=100
    for k,v in (("max_cap_violations",1),("setup_wns_ns",-1),("post_route_extracted_rc",False),("period_ns","NaN")):
        old=c[k];c[k]=v
        assert evaluate(dict(candidate=c,baseline=b))["decision"]=="INSUFFICIENT_OR_ILLEGAL"
        c[k]=old
    print("six assertions passed")
if __name__=="__main__":
    if sys.argv[1:]==["--self-test"]: test()
    elif len(sys.argv)==2:
        with open(sys.argv[1]) as f: print(json.dumps(evaluate(json.load(f)),indent=2))
    else: sys.exit("usage: gate.py --self-test | paired.json")
