#!/usr/bin/env python3
"""Exact offline finite-horizon scheduler oracle for bounded ordered bank traces.

Hindsight optimum is a mathematical upper bound, not feasible online hardware,
and is NOT RTL, synthesis, electrical or measured GPU performance evidence.
"""
import argparse
import itertools
import json
from functools import lru_cache

def exact(rows, banks, ports, slots, output, max_live=16):
    if min(banks, ports, slots, output) < 1:
        raise ValueError("positive resources required")
    requests = {}
    arrivals = []
    for expected_cycle, row in enumerate(rows):
        if type(row.get("cycle")) is not int or row["cycle"] != expected_cycle:
            raise ValueError("trace cycles must be contiguous zero-based integers; gaps cannot be compressed")
        if not isinstance(row.get("requests"), list):
            raise ValueError("requests must be a list")
        ids = []
        for req in row["requests"]:
            key = (type(req["id"]).__name__, req["id"])
            if key in requests:
                raise ValueError("duplicate request identity")
            operands = req["banks"]
            if not isinstance(operands, list) or not operands or any(
                type(b) is not int or b < 0 or b >= banks for b in operands
            ):
                raise ValueError("invalid bank operand: out of range, empty, or noninteger")
            need = tuple(operands.count(b) for b in range(banks))
            if max(need) > ports:
                raise ValueError("unschedulable request")
            requests[key] = need
            ids.append(key)
        arrivals.append(tuple(ids))
    limit = min(slots, output)

    @lru_cache(None)
    def solve(t, pending):
        if t == len(arrivals):
            return 0
        live = pending + arrivals[t]
        if len(live) > max_live:
            raise ValueError("exact oracle cap exceeded; no bound computed")
        best = -1
        for k in range(min(limit, len(live)) + 1):
            for subset in itertools.combinations(live, k):
                usage = [0] * banks
                for rid in subset:
                    usage = [a+b for a,b in zip(usage, requests[rid])]
                if any(u > ports for u in usage):
                    continue
                chosen = set(subset)
                remaining = tuple(r for r in live if r not in chosen)
                best = max(best, k + solve(t+1, remaining))
        return best
    return solve(0, ())

def selftest():
    rows = [{"cycle":0,"requests":[{"id":"a","banks":[0,1]},
            {"id":"b","banks":[0]},{"id":"c","banks":[1]}]}]
    assert exact(rows,2,1,2,2) == 2
    cases = 0
    for length in range(6):
        for operands in itertools.product(((0,), (1,), (0,1)), repeat=length):
            row = [{"cycle":0,"requests":[{"id":str(i),"banks":list(v)}
                   for i,v in enumerate(operands)]}]
            observed = exact(row,2,1,2,2)
            brute = max((len(s) for n in range(min(length,2)+1)
                for s in itertools.combinations(range(length),n)
                if all(sum(b in operands[i] for i in s)<=1 for b in (0,1))),default=0)
            assert observed == brute, (operands, observed, brute)
            cases += 1
    assert cases == 364
    # A missing idle cycle must not silently become a shorter scheduling horizon.
    gap = [{"cycle":0,"requests":[{"id":"a","banks":[0]}]},
           {"cycle":2,"requests":[{"id":"b","banks":[0]}]}]
    for invalid_rows in (gap, [{"cycle":1,"requests":[]}],
                         [{"cycle":True,"requests":[]}],
                         [{"cycle":0,"requests":{} }]):
        try:
            exact(invalid_rows,2,1,2,2)
        except ValueError:
            pass
        else:
            raise AssertionError(("malformed trace accepted", invalid_rows))
    for bad in ([-1], [2], [], [0, 2], [True], [0.0], ["0"]):
        invalid = [{"cycle":0,"requests":[{"id":"bad","banks":bad}]}]
        try:
            exact(invalid,2,1,2,2)
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid operand accepted", bad))
    print("PASS: counterexample, 364 independent single-cycle enumerations, 7 invalid-bank rejections, 4 malformed-timeline rejections")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("trace", nargs="?")
    p.add_argument("--banks",type=int)
    p.add_argument("--ports",type=int)
    p.add_argument("--slots",type=int)
    p.add_argument("--output",type=int)
    p.add_argument("--max-live",type=int,default=16)
    p.add_argument("--selftest",action="store_true")
    a=p.parse_args()
    if a.selftest:
        selftest()
        return
    if not a.trace or any(getattr(a,k) is None for k in ("banks","ports","slots","output")):
        p.error("trace and all resource parameters required")
    from ordered_trace_fail_closed_replay import load, replay
    provenance, rows = load(a.trace,a.banks)
    optimum=exact(rows,a.banks,a.ports,a.slots,a.output,a.max_live)
    comparators={name:replay(rows,a.banks,a.ports,a.slots,a.output,name)["completed"]
                 for name in ("fifo","greedy")}
    assert all(x<=optimum for x in comparators.values())
    print(json.dumps({"provenance":provenance,"offline_hindsight_optimum":optimum,
        "comparators":comparators,
        "evidence_tier":"bounded exact offline oracle; not RTL or physical validation"},indent=2))

if __name__=="__main__":
    main()
