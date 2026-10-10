"""Vektor-087: probe deadline ownership as a cross-latency fairness control."""
import json
from random import Random
from reservation_reference_087 import Calendar

class DeadlineOwner:
    def __init__(self,clients):
        self.clients=clients
        self.time=0
        self.booked={}
    def step(self,valid,latency):
        grants=[0]*self.clients
        for i in range(self.clients):
            l=latency[i]
            t=self.time+l
            if valid[i] and l>0 and t%self.clients==i and t not in self.booked:
                self.booked[t]=i
                grants[i]=1
        for i in range(self.clients):
            t=self.time+latency[i]
            if valid[i] and latency[i]==1 and t not in self.booked:
                self.booked[t]=i
                grants[i]=1
        self.time+=1
        return grants

def run(kind,cycles=10000,seed=20261012):
    rng=Random(seed)
    rr=Calendar(1,4,4,1)
    guard=DeadlineOwner(4)
    sums={'round_robin':[0]*4,'guarded':[0]*4}
    for t in range(cycles):
        if kind=='heterogeneous': v=[1]*4;l=[1,2,3,4]
        elif kind=='single': v=[1,0,0,0];l=[2]*4
        elif kind=='homogeneous': v=[1]*4;l=[2]*4
        else: v=[int(rng.random()<0.55) for _ in range(4)];l=[rng.randint(1,4) for _ in range(4)]
        g,_=rr.step(False,v,[0]*4,l)
        h=guard.step(v,l)
        for key,grants in [('round_robin',g),('guarded',h)]:
            sums[key]=[a+b for a,b in zip(sums[key],grants)]
    return dict(kind=kind,by_client=sums,totals={k:sum(v) for k,v in sums.items()})

if __name__=='__main__':
    print(json.dumps([run(k) for k in ['heterogeneous','single','homogeneous','random']],indent=2))
