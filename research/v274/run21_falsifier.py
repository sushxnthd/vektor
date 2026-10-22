#!/usr/bin/env python3
"""V274 independent single-entry RF collector falsifier.
No RTL simulation/STA claim. Models synchronous RF responses with fixed latency.
"""
import json, random
from pathlib import Path

SEED=27421

class Collector:
    def __init__(self, mode, latency=2):
        self.mode=mode; self.latency=latency
        self.valid=False; self.tag=None; self.data=None
        self.pending=None; self.inflight=[]
        self.port_reads=0; self.prefetch_reads=0; self.redundant_prefetches=0
        self.hits=0; self.misses=0; self.completed=0; self.history=[]

    def tick(self, t, demand, future, eligible, values):
        arrivals=[x for x in self.inflight if x[0]==t]
        self.inflight=[x for x in self.inflight if x[0]!=t]
        for _,tag,value,kind in arrivals:
            self.valid=True; self.tag=tag; self.data=value
            if kind=='prefetch' and self.pending==tag:
                self.pending=None
        hit=bool(demand is not None and self.valid and self.tag==demand)
        issued=None
        if demand is not None:
            if hit:
                assert self.data==values[demand]
                self.hits+=1; self.completed+=1
                self.valid=False
            else:
                self.misses+=1
                issued=('demand',demand)
        elif future is not None and eligible and self.mode!='demand_only':
            if self.mode=='original':
                issued=('prefetch',future)
            elif self.mode in ('repaired','equal_lookahead'):
                if not self.valid and self.pending is None:
                    issued=('prefetch',future)
            else: raise ValueError(self.mode)
        if issued:
            kind,tag=issued
            self.port_reads+=1
            if kind=='prefetch':
                self.prefetch_reads+=1
                if any(x[1]==tag for x in self.inflight) or (self.valid and self.tag==tag):
                    self.redundant_prefetches+=1
                if self.mode in ('repaired','equal_lookahead'):
                    self.pending=tag
            self.inflight.append((t+self.latency,tag,values[tag],kind))
        state=(hit,issued,self.valid,self.tag,self.pending,tuple(self.inflight))
        self.history.append(state)
        return hit, issued

def random_trace(seed, n):
    r=random.Random(seed)
    values={i:(i*0x9e3779b1)&0xffffffff for i in range(128)}
    current=0
    trace=[]
    for t in range(n):
        if r.random()<0.25:
            current=r.randrange(128)
        demand = current if r.random()<0.65 else None
        future = current if r.random()<0.8 else r.randrange(128)
        trace.append((demand,future,r.random()<0.95))
    return values,trace

def evaluate(seed,n):
    values,trace=random_trace(seed,n)
    a=Collector('original'); b=Collector('repaired'); c=Collector('equal_lookahead'); d=Collector('demand_only')
    for t,(demand,future,eligible) in enumerate(trace):
        for model in (a,b,c,d): model.tick(t,demand,future,eligible,values)
        assert b.history[-1]==c.history[-1], (seed,t,b.history[-1],c.history[-1])
    return {k:{'reads':x.port_reads,'prefetch_reads':x.prefetch_reads,'redundant_prefetches':x.redundant_prefetches,'demand_hits':x.hits,'demand_misses':x.misses} for k,x in [('original',a),('repaired',b),('equal_lookahead',c),('demand_only',d)]}

def explicit_counterexample():
    values={1:0xdeadbeef}
    original=Collector('original'); repaired=Collector('repaired')
    for t in range(6):
        original.tick(t,None,1,True,values)
        repaired.tick(t,None,1,True,values)
    return {'original_prefetch_reads':original.prefetch_reads,'repaired_prefetch_reads':repaired.prefetch_reads,
            'original_redundant':original.redundant_prefetches,'repaired_redundant':repaired.redundant_prefetches}

def main():
    runs=[evaluate(SEED+i,2500) for i in range(40)]
    sums={mode:{metric:sum(row[mode][metric] for row in runs) for metric in runs[0][mode]} for mode in runs[0]}
    assert sums['repaired']==sums['equal_lookahead']
    cx=explicit_counterexample()
    assert cx['original_prefetch_reads']==6 and cx['repaired_prefetch_reads']==1
    assert cx['original_redundant']>=4 and cx['repaired_redundant']==0
    result={'kernel':'V274','evidence':'E1 Python cycle-model only; no RTL sim, synthesis, or STA',
            'seed':SEED,'trace_count':len(runs),'cycles_per_trace':2500,
            'collector_state_comparisons':len(runs)*2500,'equal_resource_mismatches':0,
            'explicit_counterexample':cx,'aggregate':sums,
            'holdouts_evaluated':False,
            'decision':'retire: strongest equal-resource lookahead duplicates repaired V274 exactly'}
    p=Path(__file__).with_name('run21_results.json');p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
