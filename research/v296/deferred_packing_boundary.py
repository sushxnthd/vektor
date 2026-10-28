#!/usr/bin/env python3
"""Mapped-only V296 deferred-write tile-packing law and synthetic falsification.
Frozen: DEFERRED_MAPPED_INTEGER_PACKING_PREREG_20261028.md. No physical signoff.
"""
import argparse, json, random
from array import array
from fractions import Fraction

AREAS = {'D4': (13044906, 13510406), 'D8': (18308514, 18769492)}  # milli-um2: pairwise, serial
SEEDS = (20261028, 20261029)
WARM, EVAL, WARPS, CAP = 1000, 7000, 410, 100


def boundary(a, s):
    if not 0 < a < s: raise ValueError('positive pairwise area below serial required')
    k = (a + s - a - 1) // (s-a)  # ceil(a/(s-a))
    for n in range(1, k): assert (n+1)*a > n*s
    assert (k+1)*a <= k*s
    # Independent interval-endpoint scan for first serial-multiple crossover.
    assert next(n for n in range(1, 1000) if n*s//a > n) == k
    current_a, current_s = 30000000//a, 30000000//s
    next_a, next_s = (current_a+1)*a, (current_s+1)*s
    assert next_a < next_s and next_a//s == current_s
    return dict(mapped_capacity_at_30000=[current_a,current_s],
                next_extra_candidate_threshold_um2=next_a/1000,
                next_serial_threshold_um2=next_s/1000,
                narrow_budget_window_um2=(next_s-next_a)/1000,
                serial_multiple_crossover_k=k, serial_multiple_budget_um2=k*s/1000,
                candidate_slices_at_serial_multiple=k+1,
                asymptotic_density_ratio=float(Fraction(s,a)))


def stream(seed, warps, cycles):
    valid, banks = [], []
    for w in range(warps):
        rng = random.Random(seed ^ (w*0x9E3779B1))
        v, b = array('B'), array('B')
        for _ in range(cycles):
            v.append(rng.random() < .98)
            x = rng.randrange(16)
            y = x if rng.random() < .20 else rng.randrange(16)
            b.append((x<<4)|y)
        valid.append(v); banks.append(b)
    return valid, banks


def schedule(requests, tiles, warps, cycles, independent=False, history=False):
    valid, banks = requests
    groups = [[w for w in range(warps) if w%tiles == i] for i in range(tiles)]
    ready = [0]*warps
    raw = capped = 0
    grants = []
    for t in range(cycles):
        issued = []
        for group in groups:
            used = {} if independent else [0]*16
            accepted = 0
            for off in range(len(group)):
                if accepted >= 4: break
                w = group[(t+off)%len(group)]
                if ready[w]>t or not valid[w][t]: continue
                x,y = divmod(banks[w][t],16)
                if independent:
                    need = {x:2} if x==y else {x:1,y:1}
                    if any(used.get(b,0)+n>2 for b,n in need.items()): continue
                    for b,n in need.items(): used[b]=used.get(b,0)+n
                else:
                    if x==y:
                        if used[x]+2>2: continue
                        used[x]+=2
                    else:
                        if used[x]>=2 or used[y]>=2: continue
                        used[x]+=1; used[y]+=1
                ready[w]=t+2
                issued.append(w)
                accepted += 1
        if history: grants.append(tuple(issued))
        if t>=WARM:
            raw+=len(issued); capped+=min(len(issued),CAP)
    return dict(raw_per_cycle=raw/max(1,cycles-WARM), capped_per_cycle=capped/max(1,cycles-WARM), history=grants if history else None)


def evaluate():
    rows={d:boundary(*areas) for d,areas in AREAS.items()}
    assert rows['D4']['mapped_capacity_at_30000']==[2,2]
    assert rows['D8']['mapped_capacity_at_30000']==[1,1]
    trials=[]
    for seed in SEEDS:
        req=stream(seed,WARPS,WARM+EVAL)
        for tiles in (40,41):
            assert schedule(req,tiles,WARPS,32,history=True)['history']==schedule(req,tiles,WARPS,32,independent=True,history=True)['history']
        s=schedule(req,40,WARPS,WARM+EVAL)
        c=schedule(req,41,WARPS,WARM+EVAL)
        gain=c['raw_per_cycle']/s['raw_per_cycle']-1
        capped=c['capped_per_cycle']/s['capped_per_cycle']-1
        trials.append(dict(seed=seed,serial=s,candidate=c,gain_fraction=gain,capped_gain_fraction=capped,
                           win_gate=gain>.005,no_win_gate=capped==0))
    for depth,tiles in (('D4',2),('D8',1)):
        req=stream(SEEDS[0],10*tiles,96)
        assert schedule(req,tiles,10*tiles,96,history=True)['history']==schedule(req,tiles,10*tiles,96,independent=True,history=True)['history']
    return dict(areas_milli_um2=AREAS,analytical=rows,synthetic=trials,
                prereg_exact_D4_count_falsified=True,
                prereg_note='D4 was incorrectly predicted as 1+1 at 30000; actual 2+2. Serial-multiple crossover is not earliest absolute budget crossover.',
                frozen_synthetic_gates_pass=all(t['win_gate'] and t['no_win_gate'] for t in trials),
                all_frozen_gates_pass=False,physical_signoff=False,holdouts='SEALED')


def selftest():
    for a,s in AREAS.values(): boundary(a,s)
    for a,s in ((0,4),(4,4),(5,4)):
        try: boundary(a,s)
        except ValueError: pass
        else: raise AssertionError('bad area accepted')
    req=stream(7,12,64)
    for tiles in (1,2,3):
        assert schedule(req,tiles,12,32,history=True)['history']==schedule(req,tiles,12,32,independent=True,history=True)['history']
    print('V296_DEFERRED_PACKING_SELFTEST_PASS')


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); p.add_argument('--evaluate',action='store_true'); p.add_argument('--output'); a=p.parse_args()
    if a.self_test: selftest()
    if a.evaluate:
        out=json.dumps(evaluate(),indent=2,sort_keys=True)+'\n'
        if a.output: open(a.output,'w').write(out)
        else: print(out)
    if not (a.self_test or a.evaluate): p.error('choose mode')
