"""Vektor-087 independent absolute-time event calendar and deterministic vectors."""
from collections import defaultdict
from pathlib import Path
from random import Random
import argparse, json

class Calendar:
    def __init__(self, banks, reqs, maxlat, ports):
        self.banks, self.reqs, self.maxlat, self.ports = banks, reqs, maxlat, ports
        self.time = 0
        self.events = defaultdict(int)
        self.pointer = {(b,l): 0 for b in range(banks) for l in range(1,maxlat+1)}
    def step(self, reset, valid, bank, latency):
        grants, due = [0]*self.reqs, [0]*self.banks
        if reset:
            self.events.clear()
            self.pointer = {(b,l): 0 for b in range(self.banks) for l in range(1,self.maxlat+1)}
        else:
            due = [self.events[(self.time,b)] for b in range(self.banks)]
            for b in range(self.banks):
                for l in range(1,self.maxlat+1):
                    key = (b,l)
                    start = self.pointer[key]
                    for delta in range(self.reqs):
                        i = (start+delta)%self.reqs
                        event = (self.time+l,b)
                        if valid[i] and bank[i]==b and latency[i]==l and self.events[event]<self.ports:
                            self.events[event]+=1
                            grants[i]=1
                            self.pointer[key]=(i+1)%self.reqs
        self.time+=1
        assert max(due,default=0)<=self.ports
        return grants,due

def pack(xs,width):
    return sum(x<<(i*width) for i,x in enumerate(xs))

def stimulus(c,rng,banks,reqs,maxlat,cycles):
    if c<cycles//8: return [1]*reqs,[0]*reqs,[1]*reqs
    if c<cycles//4: return [1]*reqs,[i%banks for i in range(reqs)],[1]*reqs
    if c<cycles*3//8: return [1]*reqs,[0]*reqs,[1+i%maxlat for i in range(reqs)]
    if c<cycles//2: return [1]*reqs,[0]*reqs,[0]*reqs
    if c>=cycles*7//8:
        return ([rng.randrange(2) for _ in range(reqs)],
                [rng.randrange(1<<max(1,(banks-1).bit_length())) for _ in range(reqs)],
                [rng.randrange(1<<max(1,(maxlat+1).bit_length())) for _ in range(reqs)])
    return ([rng.randrange(2) for _ in range(reqs)],
            [rng.randrange(banks) for _ in range(reqs)],
            [rng.randrange(maxlat+2) for _ in range(reqs)])

def generate(path,banks=4,reqs=4,maxlat=4,ports=1,cycles=4096,seed=20261010):
    rng=Random(seed)
    c=Calendar(banks,reqs,maxlat,ports)
    resets={0,17,103,cycles//2,cycles*3//4}
    counts=[0]*reqs
    with Path(path).open('w') as f:
        for t in range(cycles):
            v,b,l=stimulus(t,rng,banks,reqs,maxlat,cycles)
            reset=t in resets
            grants,due=c.step(reset,v,b,l)
            for i,g in enumerate(grants): counts[i]+=g
            f.write('%d %x %x %x %x %x\n'%(0 if reset else 1,
                pack(v,1),pack(b,max(1,(banks-1).bit_length())),
                pack(l,max(1,(maxlat+1).bit_length())),
                pack(grants,1),pack(due,max(1,ports.bit_length()))))
    print(json.dumps(dict(cycles=cycles,seed=seed,grants_by_client=counts,
        random_probe_fraction=0.125)))

def self_test():
    c=Calendar(1,4,4,1)
    counts=[0]*4
    for t in range(1000):
        g,_=c.step(False,[1]*4,[0]*4,[1]*4)
        assert g==[int(i==t%4) for i in range(4)]
        for i in range(4): counts[i]+=g[i]
    assert counts==[250]*4
    c=Calendar(1,2,4,1)
    counts=[0,0]
    for _ in range(1000):
        g,_=c.step(False,[1,1],[0,0],[1,2])
        for i in range(2): counts[i]+=g[i]
    assert counts==[1,1000],counts  # CROSS-LATENCY STARVATION NEGATIVE RESULT

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('output')
    p.add_argument('--banks',type=int,default=4)
    p.add_argument('--reqs',type=int,default=4)
    p.add_argument('--max-latency',type=int,default=4)
    p.add_argument('--ports',type=int,default=1)
    p.add_argument('--cycles',type=int,default=4096)
    p.add_argument('--seed',type=int,default=20261010)
    a=p.parse_args()
    self_test()
    generate(a.output,a.banks,a.reqs,a.max_latency,a.ports,a.cycles,a.seed)
