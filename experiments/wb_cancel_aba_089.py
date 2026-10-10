"""Vektor-089: bounded-callback cancellation ABA experiment; software model only."""
from collections import defaultdict
import random

class Model:
    def __init__(self, bits=2, delay_bound=6, policy='unsafe'):
        assert policy in ('unsafe','quarantine','boundary','oracle')
        self.bits,self.D,self.policy=bits,delay_bound,policy
        self.n=1<<bits
        self.t=self.uid=self.next=0
        self.active=None
        self.events=defaultdict(list)
        self.reuse_after=[-1]*self.n
        self.false=self.good=self.rejected=self.stalls=self.issued=0
    def step(self, offer, cancel, latency):
        t=self.t
        for uid,tag in self.events.pop(t,[]):
            if self.active and self.active[1]==tag:
                if self.active[0]==uid:self.good+=1
                else:self.false+=1
                self.active=None
            else:self.rejected+=1
        if cancel:self.active=None
        if offer and self.active is None:
            tag=None
            if self.policy=='oracle':tag=self.uid
            elif self.policy=='unsafe':
                tag=self.next;self.next=(tag+1)%self.n
            else:
                for offset in range(self.n):
                    candidate=(self.next+offset)%self.n
                    safe=t>=self.reuse_after[candidate] if self.policy=='boundary' else t>self.reuse_after[candidate]
                    if safe:
                        tag=candidate;self.next=(tag+1)%self.n;break
            if tag is None:self.stalls+=1
            else:
                self.active=(self.uid,tag)
                self.events[t+latency].append(self.active)
                if self.policy in ('quarantine','boundary'):
                    self.reuse_after[tag]=t+self.D
                self.uid+=1;self.issued+=1
        self.t+=1

def trial(bits=2,D=6,p_cancel=.6,seed=100,cycles=2000,late=False):
    rng=random.Random(seed)
    models={p:Model(bits,D,p) for p in ('unsafe','quarantine','boundary','oracle')}
    for _ in range(cycles):
        offer=rng.random()<.95;cancel=rng.random()<p_cancel
        latency=rng.randint(1,2*D if late else D)
        for m in models.values():m.step(offer,cancel,latency)
    return {p:{'false':m.false,'good':m.good,'stalls':m.stalls,'issued':m.issued} for p,m in models.items()}

def experiment():
    cases=[]
    for bits in (1,2,3,4):
        for D in (3,6,9):
            for p in (0,.25,.6):
                for seed in range(100,112):
                    cases.append(trial(bits,D,p,seed))
    for i in range(54):
        rng=random.Random(9000+i)
        cases.append(trial(rng.randint(1,5),rng.randint(2,12),rng.random()*.9,9000+i))
    return {p:{k:sum(c[p][k] for c in cases) for k in ('false','good','stalls','issued')} for p in cases[0]}

if __name__=='__main__':
    import json
    print(json.dumps({'cases':486,'surprise':54,'summary':experiment(),
                      'late_callback_negative_control':trial(1,2,.9,1200,20000,True)},indent=2))
