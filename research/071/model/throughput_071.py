#!/usr/bin/env python3
"""Vektor-071: handshake-preserving vs invalid resampling throughput model."""
from random import Random
import json

def run(depth, service, clone, seed=7, cycles=50000, hold=True):
    rng=Random(seed); q=0; pending=None; accepted=0; clones=0; terminal=0
    for _ in range(cycles):
        if pending is None:pending=1+int(rng.random()<clone)
        n=pending
        if q+n<=depth:
            q+=n;accepted+=1;clones+=n-1;pending=None
        elif not hold:
            pending=None  # INVALID: violates ready/valid payload stability
        if q and rng.random()<service:
            q-=1;terminal+=1
    assert accepted+clones==terminal+q
    return {"rate":accepted/cycles,"accepted_clone_fraction":clones/accepted,
            "physical_rate":terminal/cycles,"pending":pending,
            "capacity_bound_at_accepted_mix":service/(1+clones/accepted)}

def main():
    good=run(16,.8,.5,hold=True)
    invalid=run(16,.8,.5,hold=False)
    assert invalid["rate"]>good["rate"]+0.05
    assert abs(good["accepted_clone_fraction"]-.5)<.02
    records=[run(d,s,c,seed=7) for d in (2,4,8,16)
             for s in (.5,.8,1.) for c in (0,.5,1.)]
    probes=[run(d,s,c,seed=1000+i) for i,(d,s,c) in enumerate((
             (3,.31,.19),(5,.71,.88),(7,.93,.47),
             (9,.22,.96),(11,.84,.05),(13,.57,.66)))]
    print(json.dumps({"valid":good,"invalid":invalid,
                      "structured":len(records),"exploratory":len(probes),
                      "all_conserved":True},indent=2))
if __name__=="__main__":main()
