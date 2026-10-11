from dataclasses import dataclass
@dataclass(frozen=True)
class Access:
    tid:int; cta:int; pc:int; epoch:int; op:str; space:str; addr:int; size:int; value:int=0
def namespace(e):
    if e.space=='G': return ('G',0)
    if e.space=='S': return ('S',e.cta)
    if e.space=='L': return ('L',e.tid)
    raise ValueError(e.space)
def conflict(a,b):
    return namespace(a)==namespace(b) and a.addr<b.addr+b.size and b.addr<a.addr+a.size and (a.op!='L' or b.op!='L')
def validate(events,waves,width=32):
    if not events or not waves or type(width) is not int or not 1<=width<=32: return False
    for e in events:
        if (any(type(x) is not int or x<0 for x in (e.tid,e.cta,e.pc,e.epoch,e.addr))
            or e.op not in ('L','S','A') or e.space not in ('G','S','L')
            or type(e.size) is not int or e.size not in (1,2,4,8,16)
            or e.addr+e.size>1<<64): return False
    pos=[-1]*len(events)
    for step,w in enumerate(waves):
        if not w or len(w)>width: return False
        sig=None;tids=set()
        for i in w:
            if type(i) is not int or i<0 or i>=len(events) or pos[i]>=0: return False
            e=events[i];key=(e.cta,e.pc,e.epoch,e.op,e.space,e.size)
            if sig is None: sig=key
            elif sig!=key: return False
            if e.tid in tids: return False
            tids.add(e.tid);pos[i]=step
    if -1 in pos: return False
    last={};epochs={}
    for i,e in enumerate(events):
        if e.tid in last and pos[last[e.tid]]>=pos[i]: return False
        last[e.tid]=i
        key=(e.cta,e.epoch)
        if key not in epochs: epochs[key]=[len(waves),-1]
        epochs[key][0]=min(epochs[key][0],pos[i])
        epochs[key][1]=max(epochs[key][1],pos[i])
        for j in range(i):
            if conflict(events[j],e) and pos[j]>=pos[i]: return False
    for cta in {e.cta for e in events}:
        spans=sorted((ep,b) for (c,ep),b in epochs.items() if c==cta)
        for (_,a),(_,b) in zip(spans,spans[1:]):
            if a[1]>=b[0]: return False
    return True
