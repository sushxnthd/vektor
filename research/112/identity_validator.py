"""Composite logical-thread identity adapter for V111's abstract SC model.
Not a Vortex memory consistency model. CTA reuse requires an external lifetime token.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"111"))
from scoped_validator import Access,validate as validate_sc
@dataclass(frozen=True)
class Event:
    cid:int; cta:int; wid:int; tid:int; pc:int; epoch:int
    op:str; space:str; addr:int; size:int; value:int=0
    @property
    def thread_key(self): return (self.cid,self.cta,self.wid,self.tid)
    @property
    def cta_key(self): return (self.cid,self.cta)
def lower(events):
    ts={k:i for i,k in enumerate(sorted({e.thread_key for e in events}))}
    cs={k:i for i,k in enumerate(sorted({e.cta_key for e in events}))}
    return [Access(ts[e.thread_key],cs[e.cta_key],e.pc,e.epoch,e.op,e.space,e.addr,e.size,e.value) for e in events]
def validate(events,waves):
    if any(any(type(x)!=int or x<0 for x in (e.cid,e.cta,e.wid,e.tid)) for e in events):return False
    return validate_sc(lower(events),waves)
def legacy(events,waves):
    return validate_sc([Access(e.tid,e.cta,e.pc,e.epoch,e.op,e.space,e.addr,e.size,e.value) for e in events],waves)
def replay(events,waves):
    events=lower(events); mem={}; reads={}
    for wave in waves:
        for i in wave:
            e=events[i]
            ns=("G",0) if e.space=="G" else (e.space,e.cta if e.space=="S" else e.tid)
            old=sum(mem.get((ns,e.addr+k),((e.addr+k)*37+11)&255)<<(8*k) for k in range(e.size))
            if e.op in ("L","A"):reads[i]=old
            if e.op in ("S","A"):
                new=(e.value if e.op=="S" else old+e.value)&((1<<(8*e.size))-1)
                for k in range(e.size):mem[(ns,e.addr+k)]=(new>>(8*k))&255
    return reads,mem
