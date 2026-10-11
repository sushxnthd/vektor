"""Strict Vortex SimX LSU issue trace parser. Addresses are virtual, not physical."""
import csv
from dataclasses import dataclass
FIELDS=("seq","cid","cta_id","wid","tid","uuid","pc","op","va","size","addr_class","address_stage","event_stage")
@dataclass(frozen=True)
class Record:
    seq:int; cid:int; cta_id:int; wid:int; tid:int; uuid:int; pc:int
    op:str; va:int; size:int; addr_class:str; address_stage:str; event_stage:str
    @property
    def hart(self):return (self.cid,self.wid,self.tid)
    @property
    def cta_instance(self):return (self.cid,self.cta_id)
def read_trace(stream):
    rows=list(csv.reader(stream))
    if not rows:raise ValueError("empty")
    if rows[0]==list(FIELDS):rows=rows[1:]
    if not rows:raise ValueError("header only")
    out=[]; seen=set()
    for row in rows:
        if len(row)!=len(FIELDS):raise ValueError("column mismatch")
        try: nums=[int(row[i],10) for i in (0,1,2,3,4,5,6,8,9)]
        except ValueError as e:raise ValueError("bad integer") from e
        seq,cid,cta,wid,tid,uuid,pc,va,size=nums
        op,cls,addr_stage,event_stage=row[7],row[10],row[11],row[12]
        if any(x<0 for x in nums) or any(x>=1<<64 for x in (uuid,pc,va)):raise ValueError("range")
        if op not in ("L","S","A","F") or cls not in ("G","S","I","U"):raise ValueError("enum")
        if addr_stage!="virtual" or event_stage!="lsu_issue":raise ValueError("stage")
        if op=="F":
            if size!=0 or cls!="U":raise ValueError("fence")
        elif size not in (1,2,4,8,16) or va+size>1<<64 or va%size or cls=="U":
            raise ValueError("memory interval")
        if seq in seen:raise ValueError("duplicate sequence")
        seen.add(seq)
        out.append(Record(seq,cid,cta,wid,tid,uuid,pc,op,va,size,cls,addr_stage,event_stage))
    if [r.seq for r in out]!=sorted(seen):raise ValueError("unordered observer sequence")
    return out
