"""V113 fail-closed CTA generation tagging. Host trace model; not GPU validation."""
import csv, io
from dataclasses import dataclass

@dataclass(frozen=True)
class E:
    cid:int; slot:int; gen:int; wid:int; tid:int; op:str; va:int; size:int; space:str
    @property
    def cta(self): return (self.cid,self.slot,self.gen)
    @property
    def thread(self): return (*self.cta,self.wid,self.tid)

def parse(stream):
    active={}; generations={}; events=[]
    lines=list(csv.reader(stream))
    if not lines: raise ValueError("empty trace")
    for seq,row in enumerate(lines):
        if len(row)!=13: raise ValueError("bad columns")
        try: n=[int(row[i]) for i in (0,1,2,3,4,5,6,8,9)]
        except ValueError as exc: raise ValueError("noninteger") from exc
        observed,cid,slot,wid,tid,uuid,pc,va,size=n
        if observed!=seq or min(n)<0 or max(uuid,pc,va)>=2**64: raise ValueError("bad identity/sequence")
        op,space,address_stage,event_stage=row[7],row[10],row[11],row[12]
        key=(cid,slot)
        if op in ("B","E"):
            if (space,address_stage,event_stage)!=("U","none","cta_allocate" if op=="B" else "cta_release"):
                raise ValueError("bad CTA provenance")
            if any((wid,tid,uuid,pc,va,size)): raise ValueError("bad CTA payload")
            if op=="B":
                if key in active: raise ValueError("duplicate allocation")
                generations[key]=generations.get(key,0)+1;active[key]=generations[key]
            else:
                if key not in active: raise ValueError("unpaired release")
                del active[key]
        elif op in ("L","S","A","F"):
            if key not in active: raise ValueError("LSU outside CTA lifetime")
            if (address_stage,event_stage)!=("virtual","lsu_issue"): raise ValueError("wrong stage")
            if op=="F":
                if size or space!="U": raise ValueError("bad fence")
            elif size not in (1,2,4,8,16) or space not in ("G","S","I") or va%size or va+size>2**64:
                raise ValueError("bad memory interval")
            events.append(E(cid,slot,active[key],wid,tid,op,va,size,space))
        else: raise ValueError("unknown op")
    if active: raise ValueError("truncated CTA lifetime")
    return events

def hazard(a,b):
    """Restricted SC byte-hazard only. Reject atomics, fences and I/O."""
    if a.op not in ("L","S") or b.op not in ("L","S") or a.space not in ("G","S") or b.space not in ("G","S"):
        raise ValueError("unsupported")
    if a.space!=b.space or (a.op,b.op)==("L","L"): return False
    if a.space=="S" and a.cta!=b.cta: return False
    return max(a.va,b.va)<min(a.va+a.size,b.va+b.size)

def row(seq,cid,slot,op,va=0,size=0,space="U"):
    return [seq,cid,slot,0,0,0,0,op,va,size,space,
            "none" if op in ("B","E") else "virtual",
            ("cta_allocate" if op=="B" else "cta_release") if op in ("B","E") else "lsu_issue"]

def directed_tests():
    def decode(rows):
        s=io.StringIO();w=csv.writer(s,lineterminator="\n");w.writerows(rows)
        return parse(io.StringIO(s.getvalue()))
    reuse=[row(0,1,0,"B"),row(1,1,0,"S",4096,4,"S"),row(2,1,0,"E"),
           row(3,1,0,"B"),row(4,1,0,"L",4096,4,"S"),row(5,1,0,"E")]
    a,b=decode(reuse)
    assert a.cta!=b.cta and not hazard(a,b) and a.thread!=b.thread
    reuse[1][10]=reuse[4][10]="G"
    a,b=decode(reuse)
    assert hazard(a,b)
    reuse[1][10]=reuse[4][10]="S"
    for bad in (reuse[:-1],reuse[1:],reuse[:1]+reuse[:1]+reuse[1:]):
        try: decode(bad)
        except ValueError: pass
        else: raise AssertionError("accepted malformed lifecycle")
    print("V113 directed lifecycle and global/shared controls: PASS")

if __name__=="__main__": directed_tests()
