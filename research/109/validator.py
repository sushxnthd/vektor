"""Vektor-109: fail-closed Wave32 cohort validity checker (host model)."""
from collections import defaultdict

def dependencies(events):
    deps=[set() for _ in events]
    last_thread={}; last_write={}; readers=defaultdict(set)
    for i,e in enumerate(events):
        if e.tid in last_thread: deps[i].add(last_thread[e.tid])
        last_thread[e.tid]=i
        if e.addr in last_write: deps[i].add(last_write[e.addr])
        if e.op in ('S','A'):
            deps[i].update(readers[e.addr]); readers[e.addr].clear()
            last_write[e.addr]=i
        else: readers[e.addr].add(i)
    return deps

def strict_valid(events,waves,width=32):
    if not events or not waves or type(width) is not int or width<1:return False
    n=len(events); pos=[-1]*n
    for t,w in enumerate(waves):
        if not w or len(w)>width:return False
        signature=None; lanes=set()
        for idx in w:
            if type(idx) is not int or idx<0 or idx>=n or pos[idx]!=-1:return False
            pos[idx]=t; e=events[idx]; sig=(e.pc,e.op,e.epoch)
            if signature is None:signature=sig
            elif signature!=sig:return False
            if e.tid in lanes:return False
            lanes.add(e.tid)
    if any(t<0 for t in pos):return False
    for i,preds in enumerate(dependencies(events)):
        if any(pos[p]>=pos[i] for p in preds):return False
    bounds={}
    for i,e in enumerate(events):
        if e.epoch not in bounds:bounds[e.epoch]=[len(waves),-1]
        bounds[e.epoch][0]=min(bounds[e.epoch][0],pos[i])
        bounds[e.epoch][1]=max(bounds[e.epoch][1],pos[i])
    eps=sorted(bounds)
    return all(bounds[a][1]<bounds[b][0] for a,b in zip(eps,eps[1:]))
