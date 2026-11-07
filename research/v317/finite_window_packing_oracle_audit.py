#!/usr/bin/env python3
"""Exact finite-window bank packing audit. Oracle is not physical RTL."""
import itertools
import json
import argparse
from collections import deque
from ordered_trace_fail_closed_replay import load

def choose(q, banks, ports, slots, output, window, exact):
    cap = min(slots, output)
    candidates = list(q)[:window]
    def legal(indices):
        counts = [0] * banks
        for i in indices:
            for b in candidates[i]["banks"]:
                counts[b] += 1
                if counts[b] > ports:
                    return False
        return True
    if exact:
        if window > 18:
            raise ValueError("exponential oracle window limited to 18")
        for n in range(min(cap, len(candidates)), -1, -1):
            for indices in itertools.combinations(range(len(candidates)), n):
                if legal(indices):
                    return {candidates[i]["id"] for i in indices}
    else:
        indices = []
        for i in range(len(candidates)):
            if len(indices) == cap:
                break
            if legal(indices + [i]):
                indices.append(i)
        return {candidates[i]["id"] for i in indices}
    raise AssertionError("empty selection must be legal")

def replay(rows, banks, ports, slots, output, window, exact):
    if min(banks, ports, slots, output, window) < 1:
        raise ValueError("resources must be positive")
    q = deque()
    completed = 0
    for row in rows:
        q.extend(row["requests"])
        for r in q:
            if any(r["banks"].count(b) > ports for b in set(r["banks"])):
                raise ValueError("unschedulable request")
        selected = choose(q, banks, ports, slots, output, window, exact)
        q = deque(r for r in q if r["id"] not in selected)
        completed += len(selected)
    assert completed + len(q) == sum(len(row["requests"]) for row in rows)
    return {"completed": completed, "backlog": len(q)}

def self_test():
    rows = [{"requests": [{"id":0,"banks":[0,1]},{"id":1,"banks":[0]},{"id":2,"banks":[1]}]}]
    assert replay(rows,2,1,2,2,3,False)["completed"] == 1
    assert replay(rows,2,1,2,2,3,True)["completed"] == 2
    count = 0
    for n in range(5):
        for seq in itertools.product(((0,),(1,),(0,1)), repeat=n):
            q = [{"id":i,"banks":list(bs)} for i,bs in enumerate(seq)]
            for slots in (1,2,3):
                for window in range(1,6):
                    greedy = choose(q,2,1,slots,slots,window,False)
                    oracle = choose(q,2,1,slots,slots,window,True)
                    assert len(oracle) >= len(greedy)
                    count += 1
    print(json.dumps({"exhaustive_one_cycle_cases":count,"result":"PASS"}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--trace")
    ap.add_argument("--banks",type=int,default=2)
    ap.add_argument("--ports",type=int,default=1)
    ap.add_argument("--slots",type=int,default=2)
    ap.add_argument("--output",type=int,default=2)
    ap.add_argument("--window",type=int,default=3)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.trace:
        ap.error("--trace required")
    p,rows = load(a.trace,a.banks)
    print(json.dumps({"provenance":p,"greedy":replay(rows,a.banks,a.ports,a.slots,a.output,a.window,False),"oracle":replay(rows,a.banks,a.ports,a.slots,a.output,a.window,True),"evidence_tier":"trace replay only; per-cycle oracle is neither implementable RTL nor a global throughput upper bound"},indent=2))
if __name__ == "__main__":
    main()
