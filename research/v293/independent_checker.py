#!/usr/bin/env python3
"""Independent software oracle for the V293 four-entry cache hypotheses.
Functional checks are not STA, silicon energy, or novelty evidence.
Frozen holdouts are opened ONLY after RTL simulation succeeds in CI.
"""
import json
import random
import sys

def simulate(addresses, policy):
    # Independent explicit reference; no shared RTL state or hit decision.
    entries = [None] * 4
    rr = 0
    hits = 0
    for addr in addresses:
        if policy == "local":
            k = addr % 4
            if entries[k] == addr:
                hits += 1
            else:
                entries[k] = addr
        elif policy == "global_rr":
            if addr in entries:
                hits += 1
            else:
                entries[rr] = addr
                rr = (rr + 1) % 4
        elif policy == "global_lru":
            if addr in entries:
                hits += 1
                entries.remove(addr)
            elif len(entries) == 4:
                entries.pop(0)
            entries.append(addr)
        elif policy == "banked_equal_budget":
            k = addr & 3
            if entries[k] == addr:
                hits += 1
            else:
                entries[k] = addr
        else:
            raise ValueError(policy)
    return {"hits": hits, "rf_reads": len(addresses) - hits,
            "hit_rate": hits / len(addresses)}

def evaluate(name, trace):
    results = {p: simulate(trace,p) for p in
               ("local","global_rr","global_lru","banked_equal_budget")}
    assert results["local"] == results["banked_equal_budget"]
    return {"name":name,"count":len(trace),"policies":results}

def main():
    rng=random.Random(293)
    n=4096
    # Both holdouts frozen in FROZEN_PREDICTIONS.json before evaluation.
    workloads={
      "four_bank_stationary_reuse":[i % 4 for i in range(n)],
      "single_bank_four_address_cycle":[(i % 4)*4 for i in range(n)],
      "independent_uniform":[rng.randrange(256) for _ in range(n)],
      "two_addresses_per_bank":[(i % 8) for i in range(n)],
    }
    result={"evidence_class":"E0 software oracle; RTL only if CI preceding step passes",
            "cases":[evaluate(k,v) for k,v in workloads.items()]}
    pos=result["cases"][0]["policies"]
    neg=result["cases"][1]["policies"]
    assert abs(pos["local"]["hit_rate"]-pos["global_lru"]["hit_rate"]) <= 0.02
    assert neg["local"]["hit_rate"] < 0.02
    assert neg["global_lru"]["hit_rate"] > 0.98
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
