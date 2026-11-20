#!/usr/bin/env python3
"""V317 independent finite-FIFO conservation and paired-trace regression.
Synthetic scheduler model only; no RTL, timing, power, or GPU IPC claims.
"""
import importlib.util
from collections import deque
from pathlib import Path

SRC=Path(__file__).with_name("finite_queue_prospective_20261120.py")
spec=importlib.util.spec_from_file_location("v317_prospective",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def reference(trace,policy):
    q=deque()
    offered=admitted=dropped=completed=0
    measured_offered=measured_dropped=measured_completed=0
    for t,batch in enumerate(trace):
        requests=list(q)
        selected=m.choose(requests,policy)
        assert m.feasible(requests,selected)
        assert len(selected)==len(set(selected))
        if policy=="protected" and q: assert 0 in selected
        for i in sorted(selected,reverse=True):
            del q[i]
        completed+=len(selected)
        if t>=m.WARMUP: measured_completed+=len(selected)
        for operands in batch:
            offered+=1
            if t>=m.WARMUP:measured_offered+=1
            if len(q)<m.CAP:
                q.append((t,operands))
                admitted+=1
            else:
                dropped+=1
                if t>=m.WARMUP:measured_dropped+=1
        assert offered==admitted+dropped
        assert admitted==completed+len(q)
        assert len(q)<=m.CAP
    return (measured_completed,measured_dropped,measured_offered)

def trace(seed,regime,rate):
    import random
    rng=random.Random(seed)
    weights=m.REGIMES[regime]
    out=[]
    for _ in range(m.CYCLES):
        n=int(rate)+(rng.random()<rate%1)
        out.append([tuple(rng.choices(range(m.BANKS),weights,k=2)) for _ in range(n)])
    return out

def main():
    cases=((20261121,"uniform",1.5),(20261122,"hot65",2.5),
           (20261123,"hot85",2.0),(20261124,"uniform",2.5))
    for seed,regime,rate in cases:
        arrivals=trace(seed,regime,rate)
        for policy in ("greedy","protected"):
            completed,dropped,offered=reference(arrivals,policy)
            result=m.simulate(seed,regime,policy,rate)
            assert abs(result["throughput"]-completed/(m.CYCLES-m.WARMUP))<1e-12
            assert abs(result["drop_rate"]-dropped/max(1,offered))<1e-12
    print("PASS: 8 paired-trace reference checks; full-window FIFO conservation, legality and warmup accounting")

if __name__=="__main__":main()
