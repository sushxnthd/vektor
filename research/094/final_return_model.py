"""Synthetic Vektor-094 return model. Admissions are not GPU throughput."""
from dataclasses import dataclass
from collections import deque

@dataclass(frozen=True)
class Beat:
    uid: int
    tag: int
    final: bool
    due: int
    born: int

class ReturnModel:
    def __init__(self, tags=2, width=1, policy='final', guard=0, suppress_nonfinal=False):
        assert tags>0 and width>0 and policy in ('first','final') and guard>=0
        self.tags,self.width,self.policy,self.guard=tags,width,policy,guard
        self.suppress_nonfinal=suppress_nonfinal
        self.t=0
        self.active=[None]*tags
        self.last_free=[-10**9]*tags
        self.next_tag=0
        self.next_uid=0
        self.scheduled=[]
        self.queue=deque()
        self.metrics={k:0 for k in ('admitted','stalls','correct','false','stale','ignored','max_queue','max_age','delivered')}
        self.trace=[]
    def step(self, offer=True, latency=2, copies=1, spacing=1, cancel_mask=0, soft_reset=False, duplicate_final_delta=None):
        assert latency>=1 and copies>=1 and spacing>=1
        t=self.t
        due=[b for b in self.scheduled if b.due<=t]
        self.scheduled=[b for b in self.scheduled if b.due>t]
        self.queue.extend(due)
        self.metrics['max_queue']=max(self.metrics['max_queue'],len(self.queue))
        for _ in range(min(self.width,len(self.queue))):
            b=self.queue.popleft()
            self.metrics['delivered']+=1
            self.metrics['max_age']=max(self.metrics['max_age'],t-b.born)
            if self.policy=='final' and not b.final:
                self.metrics['ignored']+=1
                continue
            owner=self.active[b.tag]
            if owner is None:
                self.metrics['stale']+=1
            elif owner[0]!=b.uid:
                self.metrics['false']+=1
                self.active[b.tag]=None
                self.last_free[b.tag]=t
            else:
                if owner[1] and not soft_reset:self.metrics['correct']+=1
                else:self.metrics['stale']+=1
                self.active[b.tag]=None
                self.last_free[b.tag]=t
        if soft_reset:
            self.active=[None if a is None else (a[0],False) for a in self.active]
        else:
            for tag in range(self.tags):
                if cancel_mask & (1<<tag) and self.active[tag] is not None:
                    self.active[tag]=(self.active[tag][0],False)
        granted=None
        if offer and not soft_reset:
            for offset in range(self.tags):
                tag=(self.next_tag+offset)%self.tags
                if self.active[tag] is None and t>self.last_free[tag]+self.guard:
                    uid=self.next_uid;self.next_uid+=1
                    self.active[tag]=(uid,True)
                    self.next_tag=(tag+1)%self.tags
                    for j in range(copies):
                        if not self.suppress_nonfinal or j==copies-1:
                            self.scheduled.append(Beat(uid,tag,j==copies-1,t+latency+j*spacing,t))
                    if duplicate_final_delta is not None:
                        self.scheduled.append(Beat(uid,tag,True,t+latency+(copies-1)*spacing+duplicate_final_delta,t))
                    self.metrics['admitted']+=1
                    granted=(uid,tag)
                    break
            if granted is None:self.metrics['stalls']+=1
        self.trace.append((t,granted,tuple(self.active),self.metrics['false']))
        self.t+=1
        return granted

def run(steps,tags=2,width=1,policy='final',guard=0,suppress_nonfinal=False):
    m=ReturnModel(tags,width,policy,guard,suppress_nonfinal)
    for kw in steps:m.step(**kw)
    return m
