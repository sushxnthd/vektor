#!/usr/bin/env python3
"""V309 bounded exact antichain DP for source-conditional sector extrema.

NOT measured GPU traffic or hardware performance. On cap return unknown,
never an unproved exact extremum. Original active mask is unobserved.
"""
from __future__ import annotations
import argparse
import json


def insert(frontier, candidate, maximize):
    """At identical hidden-count state, prune dominated sector unions."""
    if maximize:
        if any((old | candidate) == old for old in frontier):
            return
        frontier[:] = [old for old in frontier if (old | candidate) != candidate]
    else:
        if any((old | candidate) == candidate for old in frontier):
            return
        frontier[:] = [old for old in frontier if (old | candidate) != old]
    frontier.append(candidate)


def exact_sector_extrema(mask, width, tokens, *, lanes=32,
                         max_states=3000, max_transitions=100000):
    """Return exact (min,max,meta), or (None,None,meta) on budget/overflow.

    A superset of M with popcount(A)=len(tokens) is the unknown original
    active mask. Tokens are ordered by A's set lanes. DP selects the ranks
    corresponding to the visible lanes, tracking hidden-lane placements.
    """
    k, n = mask.bit_count(), len(tokens)
    if not (0 < mask < (1 << lanes)) or not (k <= n <= lanes) or width < 1:
        raise ValueError("incompatible mask, address count or width")
    if max_states < 1 or max_transitions < 1:
        raise ValueError("invalid resource budget")
    max64 = (1 << 64) - 1
    footprints, sector_ids = [], {}
    for token in tokens:
        address = int(token, 0) if isinstance(token, str) else int(token)
        if address < 0 or address > max64 or address + width - 1 > max64:
            return None, None, {"status": "unknown_address_overflow", "transitions": 0}
        bits = 0
        for sector in range(address // 32, (address + width - 1) // 32 + 1):
            if sector not in sector_ids:
                sector_ids[sector] = len(sector_ids)
            bits |= 1 << sector_ids[sector]
        footprints.append(bits)
    visible = [lane for lane in range(lanes) if mask & (1 << lane)]
    h = n - k
    gaps = [visible[0]] + [visible[i] - visible[i-1] - 1 for i in range(1,k)]
    trailing = lanes - visible[-1] - 1
    mins, maxs = {0:[0]}, {0:[0]}
    transitions, peak = 0, 2
    for i, gap in enumerate(gaps):
        next_min, next_max = {}, {}
        for maximize, src, dst in ((False,mins,next_min),(True,maxs,next_max)):
            for used, states in src.items():
                for extra in range(min(gap,h-used)+1):
                    s = used + extra
                    remaining_capacity = lanes - visible[i] - 1 - (k-i-1)
                    if h-s > remaining_capacity:
                        continue
                    rank = i+s
                    for union in states:
                        transitions += 1
                        if transitions > max_transitions:
                            return None,None,{"status":"transition_cap","transitions":transitions,"peak_states":peak}
                        frontier = dst.setdefault(s,[])
                        insert(frontier,union | footprints[rank],maximize)
                        count = sum(map(len,next_min.values()))+sum(map(len,next_max.values()))
                        if count > max_states:
                            return None,None,{"status":"state_cap","transitions":transitions,"peak_states":peak}
        mins,maxs = next_min,next_max
        peak = max(peak,sum(map(len,mins.values()))+sum(map(len,maxs.values())))
    min_counts = [u.bit_count() for s,states in mins.items() if h-s<=trailing for u in states]
    max_counts = [u.bit_count() for s,states in maxs.items() if h-s<=trailing for u in states]
    if not min_counts or not max_counts:
        raise AssertionError("no compatible original mask")
    return min(min_counts),max(max_counts),{"status":"exact","transitions":transitions,
                                          "peak_states":peak,"unique_sectors":len(sector_ids)}


def brute(mask,width,tokens,lanes):
    visible=[i for i in range(lanes) if mask & (1<<i)]
    values=[]
    for a in range(1<<lanes):
        if (a&mask)!=mask or a.bit_count()!=len(tokens):
            continue
        active=[i for i in range(lanes) if a&(1<<i)]
        touched=set()
        for lane in visible:
            addr=int(tokens[active.index(lane)],0)
            touched.update(range(addr//32,(addr+width-1)//32+1))
        values.append(len(touched))
    return min(values),max(values)


def selftest():
    checks=0
    for lanes in range(2,8):
        for mask in range(1,1<<lanes):
            for n in range(mask.bit_count(),lanes+1):
                for mode in range(3):
                    tokens=[hex(0x1000+(32*j if mode==0 else
                           4*(j%3) if mode==1 else 31+32*j)) for j in range(n)]
                    for width in (4,8):
                        lo,hi,meta=exact_sector_extrema(mask,width,tokens,lanes=lanes,max_states=20000)
                        expected=brute(mask,width,tokens,lanes)
                        assert (lo,hi)==expected,(lanes,mask,n,mode,width,(lo,hi),expected,meta)
                        checks+=1
    assert exact_sector_extrema(0b10,4,["0x101f","0x1040"],lanes=3)[:2]==(1,2)
    assert exact_sector_extrema(0b10,4,["0xffffffffffffffff","0x1000"],lanes=3)[2]["status"]=="unknown_address_overflow"
    lo,hi,meta=exact_sector_extrema(0b101010,4,[hex(0x1000+32*j) for j in range(5)],
                                    lanes=8,max_transitions=1)
    assert lo is None and meta["status"]=="transition_cap"
    # A predicted no-win case: each visible rank always adds one new sector.
    lo,hi,_=exact_sector_extrema(0b1010,4,[hex(0x1000+32*j) for j in range(3)],lanes=4)
    assert (lo,hi)==(2,2)
    return {"selftest":"PASS","independent_bruteforce_cases":checks,
            "overflow_refusal":"PASS","budget_refusal":"PASS","no_win_fixture":"PASS"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(),sort_keys=True))
