#!/usr/bin/env python3
"""Independent exact branch-and-bound sector envelope for V309 format-0 traces.

Source-conditional computational identifiability only. Not GPU transactions.
Unlike antichain DP, enumerate visible-token rank sequences and prune with
admissible suffix union bounds. Caps return UNKNOWN, never an exact answer.
"""
from __future__ import annotations
from itertools import combinations
from math import comb
import json
import random

MAX64 = (1 << 64) - 1


def exact_branch_bound(mask, width, tokens, *, lanes=32, node_cap=500000):
    if mask <= 0 or mask >= (1 << lanes) or width <= 0 or node_cap <= 0:
        raise ValueError('invalid mask, width or budget')
    visible = [i for i in range(lanes) if mask & (1 << i)]
    k, n = len(visible), len(tokens)
    if n < k or n > lanes:
        raise ValueError('incompatible token count')
    sector_ids = {}
    footprints = []
    for token in tokens:
        addr = int(token, 0) if isinstance(token, str) else int(token)
        if addr < 0 or addr + width - 1 > MAX64:
            return None, None, {'status':'unknown_address_overflow','nodes':0}
        bits = 0
        for sec in range(addr//32, (addr+width-1)//32+1):
            if sec not in sector_ids:
                sector_ids[sec] = len(sector_ids)
            bits |= 1 << sector_ids[sec]
        footprints.append(bits)
    gaps = [visible[0]] + [visible[i]-visible[i-1]-1 for i in range(1,k)]
    trailing = lanes-visible[-1]-1
    hidden = n-k
    suffix_possible = [0]*(k+1)
    for i in range(k-1,-1,-1):
        suffix_possible[i] = suffix_possible[i+1]
        for rank in range(i,min(n-1,i+hidden)+1):
            suffix_possible[i] |= footprints[rank]
    active = sorted(visible + [i for i in range(lanes) if not mask & (1<<i)][:hidden])
    ranks = {lane:j for j,lane in enumerate(active)}
    seed = 0
    for lane in visible:
        seed |= footprints[ranks[lane]]
    best_min = best_max = seed.bit_count()
    nodes = 0
    seen_min = set()
    seen_max = set()
    aborted = False

    def walk(i, used, union, maximize):
        nonlocal best_min, best_max, nodes, aborted
        nodes += 1
        if nodes > node_cap:
            aborted = True
            return
        if i == k:
            if hidden-used <= trailing:
                if maximize:
                    best_max = max(best_max,union.bit_count())
                else:
                    best_min = min(best_min,union.bit_count())
            return
        key = (i,used,union)
        cache = seen_max if maximize else seen_min
        if key in cache:
            return
        cache.add(key)
        count = union.bit_count()
        if maximize:
            if (union | suffix_possible[i]).bit_count() <= best_max:
                return
        elif count >= best_min:
            return
        gap = gaps[i]
        extras = list(range(min(gap,hidden-used)+1))
        if maximize:
            extras.sort(key=lambda e:(union | footprints[i+used+e]).bit_count(),reverse=True)
        else:
            extras.sort(key=lambda e:(union | footprints[i+used+e]).bit_count())
        for extra in extras:
            s=used+extra
            capacity=lanes-visible[i]-1-(k-i-1)
            if hidden-s>capacity:
                continue
            walk(i+1,s,union|footprints[i+s],maximize)
            if aborted:
                return

    walk(0,0,0,False)
    if aborted:
        return None,None,{'status':'node_cap','nodes':nodes}
    walk(0,0,0,True)
    if aborted:
        return None,None,{'status':'node_cap','nodes':nodes}
    return best_min,best_max,{'status':'exact','nodes':nodes,'unique_sectors':len(sector_ids),
                              'original_mask_completions':comb(lanes-k,hidden)}


def brute(mask,width,tokens,lanes):
    vis=[i for i in range(lanes) if mask&(1<<i)]
    vals=[]
    for hid in combinations([i for i in range(lanes) if not mask&(1<<i)],len(tokens)-len(vis)):
        active=sorted(vis+list(hid))
        sec=set()
        for lane in vis:
            addr=int(tokens[active.index(lane)])
            sec.update(range(addr//32,(addr+width-1)//32+1))
        vals.append(len(sec))
    return min(vals),max(vals)


def selftest():
    rng=random.Random(30920261030)
    checked=nonpoint=0
    for lanes in range(2,10):
        for mask in range(1,1<<lanes):
            k=mask.bit_count()
            for n in range(k,lanes+1):
                for mode in range(3):
                    tokens=[0x1000+32*(j if mode==0 else j%3 if mode==1 else rng.randrange(5))+(j%4)*7 for j in range(n)]
                    width=(4,8,16)[mode]
                    lo,hi,meta=exact_branch_bound(mask,width,tokens,lanes=lanes,node_cap=200000)
                    expected=brute(mask,width,tokens,lanes)
                    assert meta['status']=='exact' and (lo,hi)==expected,(lanes,mask,n,mode,lo,hi,expected,meta)
                    checked+=1
                    nonpoint+=lo!=hi
    for _ in range(200):
        k=rng.randrange(1,30)
        h=rng.randrange(0,min(3,32-k)+1)
        vis=rng.sample(range(32),k)
        mask=sum(1<<x for x in vis)
        tokens=[0x10000+32*rng.randrange(8)+rng.randrange(30) for _ in range(k+h)]
        width=rng.choice((1,4,8,16))
        if comb(32-k,h)>3000:
            continue
        lo,hi,meta=exact_branch_bound(mask,width,tokens,node_cap=1000000)
        assert meta['status']=='exact' and (lo,hi)==brute(mask,width,tokens,32)
        checked+=1
    a=exact_branch_bound(0b101010,4,[0x1000+32*j for j in range(5)],lanes=8,node_cap=1)
    assert a[0] is None and a[2]['status']=='node_cap'
    a=exact_branch_bound(0b10,8,[MAX64,0x1000],lanes=3)
    assert a[0] is None and a[2]['status']=='unknown_address_overflow'
    return {'status':'PASS','brute_force_cases':checked,'nonpoint_cases':nonpoint,
            'cap_refusal':'PASS','overflow_refusal':'PASS',
            'evidence_tier':'synthetic_source_conditional_not_GPU_cycles'}

if __name__=='__main__':
    print(json.dumps(selftest(),sort_keys=True))
