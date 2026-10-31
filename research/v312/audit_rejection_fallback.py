#!/usr/bin/env python3
"""Independent numerical/structural audit for frozen V312 simulator output."""
import copy, itertools, json, math, sys

REF={
 "hotspot":(2.0,3.9,3.9995125,16),
 "disjoint":(4.0,4.0,4.0,1),
 "transfer":(2.9453125,3.736328125,3.976104736328125,256)
}
SEEDS={"hotspot":312031,"disjoint":312032,"transfer":312033}

def audit(obj):
    assert obj["trials"]==100000
    assert set(obj["regimes"])==set(REF)
    for name,(base,candidate,oracle,nstates) in REF.items():
        row=obj["regimes"][name]
        assert row["seed"]==SEEDS[name] and row["states"]==nstates
        expected=(base,candidate,oracle)
        for key,tol in (("predicted",1e-9),("observed",.02)):
            got=row[key]
            assert len(got)==3
            for x,y in zip(got,expected):
                assert math.isfinite(x) and abs(x-y)<tol,(name,key,x,y)
            assert got[0]<=got[1]+1e-12 and got[1]<=got[2]+1e-12
        p=row["predicted"]; q=row["observed"]
        for key,val in (
            ("predicted_gain",p[1]/p[0]),
            ("observed_gain",q[1]/q[0]),
            ("predicted_oracle_fraction",p[1]/p[2]),
            ("observed_oracle_fraction",q[1]/q[2])
        ):
            assert abs(row[key]-val)<1e-10
        if name=="hotspot":
            assert row["observed_gain"]>1.5
            assert row["observed_oracle_fraction"]>.9
        if name=="disjoint":
            assert row["observed_gain"]==1.0 and row["observed_oracle_fraction"]==1.0
    law=obj["single_late_slot_law"]
    r,a,c=(law[k] for k in ("rejection","backup_ready_conditional","backup_compatible_conditional"))
    assert (r,a,c)==(.35,.75,.8)
    assert abs(law["predicted_gain"]-(1+r*a*c/(1-r)))<1e-12

def negative_controls(obj):
    edits=[
        ("hotspot gain",lambda x:x["regimes"]["hotspot"].__setitem__("observed_gain",1.1)),
        ("transfer oracle",lambda x:x["regimes"]["transfer"]["predicted"].__setitem__(2,3.1)),
        ("fabricated no-win",lambda x:x["regimes"]["disjoint"]["observed"].__setitem__(1,3.5)),
        ("wrong seed",lambda x:x["regimes"]["hotspot"].__setitem__("seed",1)),
        ("law distortion",lambda x:x["single_late_slot_law"].__setitem__("predicted_gain",1.4))
    ]
    for label,edit in edits:
        corrupted=copy.deepcopy(obj); edit(corrupted)
        try: audit(corrupted)
        except (AssertionError,KeyError,TypeError): continue
        raise AssertionError("mutation escaped independent audit: "+label)
    return len(edits)

if __name__=="__main__":
    with open(sys.argv[1],encoding="utf-8") as f: obj=json.load(f)
    audit(obj)
    print("V312 independent reference audit passed; adversarial controls:",negative_controls(obj))
