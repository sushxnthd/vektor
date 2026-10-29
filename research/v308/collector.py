"""V308 finite two-bank operand-collector falsification model.

Synthetic requests only. No GPU cycle/IPC, silicon, or RTL claim.
Each instruction has exactly two source reads; sources can hit the same bank.
Bank reads are independently staggered, not atomic per instruction.
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
from dataclasses import dataclass

@dataclass
class Slot:
    ident: int
    born: int
    left: list[int]


def workload(kind: str, seed: int, n: int) -> list[tuple[int,int]]:
    rng = random.Random(seed)
    if kind == 'iid':
        return [(rng.randrange(2),rng.randrange(2)) for _ in range(n)]
    if kind == 'skew':
        return [(0 if rng.random()<.85 else 1, 0 if rng.random()<.85 else 1) for _ in range(n)]
    if kind == 'alternating':
        return [(0,0) if (i//7)%2==0 else (1,1) for i in range(n)]
    if kind == 'mixed':
        return [(0,0) if i%3==0 else (0,1) if i%3==1 else (1,1) for i in range(n)]
    if kind == 'all_cross':
        return [(0,1) for _ in range(n)]
    raise ValueError(kind)


def legal_grants(slots: list[Slot], banks: int=2):
    """Enumerate all feasible per-bank grants; None means idle bank."""
    choices = [[None]+[i for i,s in enumerate(slots) if b in s.left] for b in range(banks)]
    for pair in itertools.product(*choices):
        yield pair


def grant_score(slots: list[Slot], pair: tuple[int|None,...], policy: str):
    granted = {i:0 for i in range(len(slots))}
    for i in pair:
        if i is not None:
            granted[i]+=1
    completions = sum(granted[i]==len(s.left) for i,s in enumerate(slots))
    count = sum(granted.values())
    ages = sum((100000-s.born)*granted[i] for i,s in enumerate(slots))
    if policy=='completion':
        return (completions,count,ages)
    if policy=='srpt':
        return (sum(granted[i]*(3-len(s.left)) for i,s in enumerate(slots)),count,ages)
    if policy=='oldest':
        return (ages,count,completions)
    raise ValueError(policy)


def select(slots: list[Slot], policy: str, banks: int=2):
    return max(legal_grants(slots,banks),key=lambda g:grant_score(slots,g,policy))


def run(trace: list[tuple[int,int]], policy: str, banks: int=2,
        collectors: int=4, arrival_interval: int=1, max_cycles: int=100000):
    if not (banks>0 and collectors>0 and arrival_interval>0):
        raise ValueError('nonpositive capacity')
    slots=[]
    cycle=0
    next_id=0
    done=0
    reads=0
    waits=0
    max_occupancy=0
    bank_counts=[0]*banks
    while done<len(trace):
        if cycle>=max_cycles:
            raise RuntimeError('cycle limit')
        if cycle%arrival_interval==0 and next_id<len(trace) and len(slots)<collectors:
            slots.append(Slot(next_id,cycle,list(trace[next_id])))
            next_id+=1
        if next_id<len(trace) and len(slots)==collectors:
            waits+=1
        max_occupancy=max(max_occupancy,len(slots))
        if slots:
            grant=select(slots,policy,banks)
            for b,i in enumerate(grant):
                if i is not None:
                    slots[i].left.remove(b)
                    bank_counts[b]+=1
                    reads+=1
            finished=[s for s in slots if not s.left]
            done+=len(finished)
            slots=[s for s in slots if s.left]
        cycle+=1
    assert next_id==len(trace) and reads==2*len(trace)
    assert sum(bank_counts)==reads
    return {'cycles':cycle,'completed':done,'reads':reads,'throughput':done/cycle,
            'admission_blocked_cycles':waits,'max_collectors':max_occupancy,
            'bank_reads':bank_counts}


def experiment(seeds=range(1001,1009), n=1200):
    output={}
    for kind in ['iid','skew','alternating','mixed','all_cross']:
        rows=[]
        for seed in seeds:
            trace=workload(kind,seed,n)
            modes={mode:run(trace,mode) for mode in ['oldest','srpt','completion']}
            rows.append({'seed':seed,'modes':modes,
                'completion_vs_srpt_pct':100*(modes['srpt']['cycles']/modes['completion']['cycles']-1),
                'completion_vs_oldest_pct':100*(modes['oldest']['cycles']/modes['completion']['cycles']-1)})
        output[kind]={'mean_vs_srpt_pct':sum(r['completion_vs_srpt_pct'] for r in rows)/len(rows),
                      'mean_vs_oldest_pct':sum(r['completion_vs_oldest_pct'] for r in rows)/len(rows),
                      'rows':rows}
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    seeds=range(31,35) if args.pilot else range(1001,1009)
    print(json.dumps(experiment(seeds),indent=2,sort_keys=True))
