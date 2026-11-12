#!/usr/bin/env python3
"""V312 buffered-collector strong control: finite-queue synthetic stress test.
Exploratory regimes were inspected on 2026-10-31, NOT prospective holdouts.
This is not a GPU cycle simulator or a matched physical implementation.
"""
import json, random

SLOTS, PORTS, BANKS, DEPTH = 4, 2, 16, 2
WARMUP, MEASURE = 2000, 30000
SEEDS = {"hotspot":312411, "diversified":312412, "disjoint":312413, "all_hot":312414}

def generate(regime,rng,slot):
    if regime=="disjoint": return (2*slot,2*slot+1)
    if regime=="all_hot": return (0,1)
    p=.95 if regime=="hotspot" else .70
    return (0,1) if rng.random()<p else (2*slot+2,2*slot+3)

def fits(counts,pair):
    next_counts=counts.copy()
    for b in pair: next_counts[b]+=1
    return max(next_counts)<=PORTS,next_counts

def service(queues,mode):
    counts=[0]*BANKS
    choices=[]
    if mode in ("head","fallback"):
        for q in queues:
            selected=None
            for k in range(min(len(q),1 if mode=="head" else 2)):
                ok, next_counts=fits(counts,q[k][1])
                if ok:
                    selected=k
                    counts=next_counts
                    break
            choices.append(selected)
    elif mode=="collector":
        # Independent one-hot occupancy, oldest feasible candidate first.
        once=twice=0
        for q in queues:
            options=[]
            for k,item in enumerate(q[:2]):
                a,b=item[1]
                ma,mb=1<<a,1<<b
                ok=((once&ma)==0) if a==b else ((twice&(ma|mb))==0)
                if ok: options.append((k,ma,mb,a==b))
            if not options: choices.append(None)
            else:
                k,ma,mb,equal=min(options)
                choices.append(k)
                twice |= ma if equal else once&(ma|mb)
                once |= ma|mb
        # Independent numeric bank-port audit of bitset decisions.
        for q,k in zip(queues,choices):
            if k is not None:
                ok,counts=fits(counts,q[k][1])
                assert ok
    else: raise ValueError(mode)
    assert max(counts)<=PORTS
    return [q.pop(k) if k is not None else None for q,k in zip(queues,choices)]

def run(regime):
    rng=random.Random(SEEDS[regime])
    qs={m:[[] for _ in range(SLOTS)] for m in ("head","fallback","collector")}
    stats={m:dict(issued=0,dropped=0,offered=0,wait_sum=0) for m in qs}
    for t in range(WARMUP+MEASURE):
        incoming=[]
        for slot in range(SLOTS):
            if rng.random()<.95: incoming.append((t*SLOTS+slot,generate(regime,rng,slot),t))
            else: incoming.append(None)
        for mode,queues in qs.items():
            for slot,item in enumerate(incoming):
                if item is None: continue
                if t>=WARMUP: stats[mode]["offered"]+=1
                if len(queues[slot])<DEPTH: queues[slot].append(item)
                elif t>=WARMUP: stats[mode]["dropped"]+=1
            selected=service(queues,mode)
            if t>=WARMUP:
                for item in selected:
                    if item is not None:
                        stats[mode]["issued"]+=1
                        stats[mode]["wait_sum"]+=t-item[2]
        assert qs["fallback"]==qs["collector"], f"same-information queue mismatch at {t}"
        assert stats["fallback"]==stats["collector"], f"same-information throughput mismatch at {t}"
    result={m:{**s,"throughput_per_cycle":s["issued"]/MEASURE,
               "mean_wait":s["wait_sum"]/max(1,s["issued"])} for m,s in stats.items()}
    result["gain_vs_head"]=result["fallback"]["issued"]/result["head"]["issued"]
    result["gain_vs_equal_info_collector"]=result["fallback"]["issued"]/result["collector"]["issued"]
    assert result["gain_vs_equal_info_collector"]==1.0
    if regime in ("disjoint","all_hot"): assert result["gain_vs_head"]==1.0
    return result

if __name__=="__main__":
    out={"tier":"synthetic finite-queue service, NOT GPU workload/physical proof",
         "retrospective_exploratory":True,"queue_depth":DEPTH,
         "warmup":WARMUP,"cycles":MEASURE,"arrival_probability":.95,
         "regimes":{name:run(name) for name in SEEDS}}
    print(json.dumps(out,indent=2,sort_keys=True))
