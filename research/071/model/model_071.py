#!/usr/bin/env python3
"""Vektor-071 independent deque and ring-buffer conservation regression."""
from collections import deque
from random import Random
import json

class Oracle:
    def __init__(self,depth):
        self.depth=depth; self.q=[deque(),deque()]; self.admit=[0,0]; self.term=[0,0]
    def step(self, actions):
        out=[]
        for k,(uid,clone,drop,stall,ready) in enumerate(actions):
            q=self.q[k]; n=0 if uid is None else 1+clone
            admit=n>0 and len(q)+n<=self.depth
            pop=bool(q) and not stall and (drop or ready)
            old=q.popleft() if pop else None
            if pop:self.term[k]+=1
            if admit:q.extend([uid]*n);self.admit[k]+=n
            out.append((admit,pop,old))
        return out

class Ring:
    def __init__(self,depth):
        self.depth=depth;self.b=[[None]*depth for _ in range(2)]
        self.h=[0,0];self.t=[0,0];self.n=[0,0];self.admit=[0,0];self.term=[0,0]
    def step(self,actions):
        out=[]
        for k,(uid,clone,drop,stall,ready) in enumerate(actions):
            n=0 if uid is None else 1+clone
            admit=n>0 and self.n[k]+n<=self.depth
            pop=self.n[k]>0 and not stall and (drop or ready)
            old=self.b[k][self.h[k]] if pop else None
            if admit:
                for i in range(n):self.b[k][(self.t[k]+i)%self.depth]=uid
                self.t[k]=(self.t[k]+n)%self.depth;self.admit[k]+=n
            if pop:self.h[k]=(self.h[k]+1)%self.depth;self.term[k]+=1
            self.n[k]+=n*int(admit)-int(pop)
            out.append((admit,pop,old))
        return out
    def queue(self,k):
        return tuple(self.b[k][(self.h[k]+i)%self.depth] for i in range(self.n[k]))

def main():
    count=0;quiescent=0
    for depth in (2,3,4,5,8):
        for seed in range(240):
            rng=Random(seed);o=Oracle(depth);r=Ring(depth)
            for cycle in range(200):
                closed=cycle>=100
                actions=[]
                for _ in range(2):
                    uid=None if closed or rng.randrange(3)==0 else rng.randrange(4)
                    actions.append((uid,rng.randrange(2),rng.randrange(5)==0,
                                    rng.randrange(4)==0,rng.randrange(2)==0))
                assert o.step(actions)==r.step(actions),(depth,seed,cycle)
                for k in range(2):
                    assert tuple(o.q[k])==r.queue(k)
                    assert o.admit[k]==o.term[k]+len(o.q[k])
                    assert o.admit[k]==r.admit[k] and o.term[k]==r.term[k]
                if closed and not o.q[0] and not o.q[1]:quiescent+=1
                count+=1
    # A delayed ACK clone survives the first ACK's delivery. Sender closure
    # alone would falsely authorize identifier reuse.
    stale=deque([0,0]);stale.popleft()
    assert len(stale)==1
    assert not (len(stale)==0)
    print(json.dumps({"paired_traces":1200,"differential_cycles":count,
                      "exact":True,"empty_closed_cycles":quiescent,
                      "unsafe_ack_alias_counterexample":True}))

if __name__=="__main__":main()
