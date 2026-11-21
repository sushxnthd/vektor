#!/usr/bin/env python3
"""Independent conservation and fairness audit for V317's periodic FIFO control.
No GPU IPC, timing, electrical, or power claims. Standard library only.
"""
from collections import deque
from itertools import combinations

BANKS=4
PORTS=2
CAPACITY=4

def legal(requests, chosen):
    usage=[0]*BANKS
    for i in chosen:
        for bank in requests[i]:
            usage[bank]+=1
            if usage[bank]>PORTS:
                return False
    return True

def choose(requests, protected):
    n=len(requests)
    subsets=[s for k in range(n+1) for s in combinations(range(n),k) if legal(requests,s)]
    if protected and n:
        subsets=[s for s in subsets if 0 in s]
    if protected:
        return max(subsets,key=lambda s:(len(s),tuple(-i for i in s)))
    chosen=()
    for i in range(n):
        if legal(requests,chosen+(i,)):
            chosen=chosen+(i,)
    return chosen

def simulate(pattern, protected, cycles=3000):
    queue=deque()
    offered=admitted=completed=dropped=0
    max_wait=0
    for t in range(cycles):
        before=len(queue)
        selection=choose([r for r,arrival in queue],protected)
        assert legal([r for r,arrival in queue],selection)
        assert not protected or not queue or 0 in selection
        for index in reversed(selection):
            _,arrival=queue[index]
            max_wait=max(max_wait,t-arrival)
            del queue[index]
        completed+=len(selection)
        for request in pattern[t%len(pattern)]:
            offered+=1
            if len(queue)<CAPACITY:
                queue.append((request,t))
                admitted+=1
            else:
                dropped+=1
        assert 0<=len(queue)<=CAPACITY
        assert offered==admitted+dropped
        assert admitted==completed+len(queue)
    return completed,dropped,offered,len(queue),max_wait

def main():
    for period in (1,2,3):
        for skew in range(4):
            pattern=tuple(tuple(((skew+t)%4,(skew+t)%4) if j==0 else ((skew+t)%4,(skew+t+1)%4) for j in range(2)) for t in range(period))
            g=simulate(pattern,False)
            p=simulate(pattern,True)
            assert g[2]==p[2]==6000
            assert g[0]==p[0],(period,skew,g,p)
            assert g[0]+g[3]+g[1]==g[2]
            assert p[0]+p[3]+p[1]==p[2]
    print("PASS: 12 full-window periodic comparisons, per-cycle conservation, oldest protection and bank-port legality")
if __name__=="__main__":
    main()
