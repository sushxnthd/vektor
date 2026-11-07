#!/usr/bin/env python3
"""Finite-credit latency falsification (synthetic; NOT RTL).

Credits are reserved from admission until retirement. Each request must spend
L full cycles in flight; bank and shared-output capacity bound retirement.
Independent token and cohort simulators are compared exhaustively.
"""
from collections import deque
from itertools import product

def aggregate(arrivals, bank, output, credits, latency):
    cohorts = [0] * (len(arrivals) + latency + 1)
    occupied = done = blocked = 0
    for t, offered in enumerate(arrivals):
        ready_end = max(0, t-latency+1)
        retire = min(sum(cohorts[:ready_end]), bank, output)
        for j in range(ready_end):
            take = min(cohorts[j], retire)
            cohorts[j] -= take
            retire -= take
            done += take
            occupied -= take
        admit = min(offered, credits-occupied)
        cohorts[t] += admit
        occupied += admit
        blocked += offered-admit
        assert occupied == sum(cohorts)
    return done, occupied, blocked

def oracle(arrivals, bank, output, credits, latency):
    inflight = deque()
    done = blocked = 0
    for t, offered in enumerate(arrivals):
        n = min(bank, output)
        while n and inflight and inflight[0] + latency <= t:
            inflight.popleft()
            done += 1
            n -= 1
        admit = min(offered, credits-len(inflight))
        inflight.extend([t]*admit)
        blocked += offered-admit
    return done, len(inflight), blocked

def test():
    n = 0
    for length in range(5):
        for arrivals in product(range(3), repeat=length):
            for bank, output, credits, latency in product(range(3), range(3), range(4), range(1,5)):
                a = aggregate(arrivals,bank,output,credits,latency)
                b = oracle(arrivals,bank,output,credits,latency)
                assert a == b, (arrivals,bank,output,credits,latency,a,b)
                n += 1
    print("PASS", n, "exhaustive cohort-vs-token cases")
    for latency in [1,2,4,8]:
        for credits in [1,2,4,8,16]:
            base = aggregate([8]*2000,1,2,credits,latency)[0]
            cand = aggregate([8]*2000,2,2,credits,latency)[0]
            print("L",latency,"credits",credits,"baseline",base,"candidate",cand,
                  "ratio",round(cand/base,4) if base else None)
    print("Conditional asymptotic upper bound: min(bank, output, credits/latency).")
    print("No GPU performance, RTL, timing, power, or physicality claim.")
if __name__ == "__main__":
    test()
