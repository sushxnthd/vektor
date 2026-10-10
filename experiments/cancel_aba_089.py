"""Vektor-089: synthetic cancellation/ABA event model; not GPU measurements."""
from dataclasses import dataclass
from collections import defaultdict
import random

@dataclass(frozen=True)
class Request:
    uid: int
    tag: int
    issued: int
    due: int

class TagMachine:
    def __init__(self, bits=2, max_delay=6, policy='unsafe'):
        assert 1 <= bits <= 8 and max_delay >= 1
        assert policy in ('unsafe','quarantine','quarantine_boundary','oracle')
        self.bits,self.max_delay,self.policy=bits,max_delay,policy
        self.n=1<<bits
        self.next_tag=self.next_uid=0
        self.active=None
        self.callbacks=defaultdict(list)
        self.quarantine_until=[-1]*self.n
        self.t=0
        self.false_accept=self.correct=self.stale_rejected=0
        self.tag_stalls=self.admitted=self.canceled=self.idle=0
        self.violations=0
        self.events=[]
    def step(self, offer=True, cancel=False, delay=1):
        t=self.t
        for event in self.callbacks.pop(t,[]):
            match=self.active is not None and event.tag==self.active.tag
            if match and event.uid!=self.active.uid:
                self.false_accept+=1
                self.events.append(('ABA',t,event.uid,self.active.uid,event.tag))
                self.active=None
            elif match:
                self.correct+=1
                self.active=None
            else:
                self.stale_rejected+=1
        if cancel and self.active is not None:
            self.events.append(('CANCEL',t,self.active.uid,self.active.tag))
            self.active=None
            self.canceled+=1
        if offer and self.active is None:
            tag=None
            if self.policy=='oracle':
                tag=self.next_uid
            elif self.policy=='unsafe':
                tag=self.next_tag
                self.next_tag=(tag+1)%self.n
            else:
                for j in range(self.n):
                    candidate=(self.next_tag+j)%self.n
                    safe=t>=self.quarantine_until[candidate] if self.policy=='quarantine_boundary' else t>self.quarantine_until[candidate]
                    if safe:
                        tag=candidate
                        self.next_tag=(tag+1)%self.n
                        break
            if tag is None:
                self.tag_stalls+=1
            else:
                uid=self.next_uid
                self.next_uid+=1
                self.active=Request(uid,tag,t,t+delay)
                self.callbacks[t+delay].append(self.active)
                if self.policy in ('quarantine','quarantine_boundary'):
                    self.quarantine_until[tag]=t+self.max_delay
                if delay>self.max_delay:self.violations+=1
                self.admitted+=1
                self.events.append(('ISSUE',t,uid,tag,t+delay))
        if self.active is None:self.idle+=1
        self.t+=1
    def metrics(self):
        return {k:getattr(self,k) for k in ('false_accept','correct','stale_rejected','tag_stalls','admitted','canceled','idle','violations')}

def simulate(bits,bound,cancel_prob,seed,cycles=2000,violation=False):
    rng=random.Random(seed)
    machines={p:TagMachine(bits,bound,p) for p in ('unsafe','quarantine','oracle','quarantine_boundary')}
    for _ in range(cycles):
        offer=rng.random()<.95
        cancel=rng.random()<cancel_prob
        delay=rng.randint(1,bound+(bound if violation else 0))
        for m in machines.values():m.step(offer,cancel,delay)
    return {p:m.metrics() for p,m in machines.items()}
