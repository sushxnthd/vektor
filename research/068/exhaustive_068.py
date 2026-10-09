#!/usr/bin/env python3
"""Finite abstract protocol exploration; NOT RTL or an unbounded proof."""
from collections import deque
from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path

@dataclass(frozen=True)
class S:
    d: int=0
    a: int=0
    q: int=0
    dc: bool=False
    ac: bool=False
    seen: bool=False

EVENTS=list(product((0,1),repeat=10))

def step(s,e,cap=2):
    ds,dx,dt,dd,close,asend,ax,at,ad,unused=e
    if unused or (ds and (s.dc or close)) or (dx and not s.d) or (dt and not s.d and not ds) or (dd and not dt): return None
    if (asend and not s.q) or (ax and not s.a) or (at and not s.a and not asend) or (ad and not at): return None
    if s.ac and dd: return None
    d=s.d+ds+dx-dt
    a=s.a+asend+ax-at
    q=s.q+dd-asend
    if not all(0<=x<=cap for x in (d,a,q)):return None
    ac=s.ac or (s.dc and s.d==0 and s.q==0 and not (ds or dx or dt or dd))
    return S(d,a,q,s.dc or bool(close),ac,s.seen or bool(ad))

def run():
    root=S()
    todo=deque([root]); visited={root}; edges=0; late_after_close=0
    retire_states=0; witness=None
    while todo:
        s=todo.popleft()
        if s.seen and s.ac and s.d==s.a==s.q==0:
            retire_states+=1
        for e in EVENTS:
            t=step(s,e)
            if t is None:continue
            edges+=1
            if s.ac and e[8]:
                late_after_close+=1
                if witness is None:witness={'before':s.__dict__,'event':e,'after':t.__dict__}
            if s.ac and (t.d or t.q):
                raise AssertionError('producer closure allowed new DATA or ACK queue')
            if t.ac and not t.dc:
                raise AssertionError('ACK closed before sender closure')
            if t not in visited:
                visited.add(t);todo.append(t)
    assert (len(visited),edges,retire_states,late_after_close)==(114,6064,1,16)
    out={'states':len(visited),'transitions':edges,'retirable_states':retire_states,
         'legal_late_ack_transitions':late_after_close,
         'legacy_guard_false_error_witness':witness,
         'evidence':'finite abstract state enumeration only'}
    Path(__file__).with_name('results_068.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':run()
