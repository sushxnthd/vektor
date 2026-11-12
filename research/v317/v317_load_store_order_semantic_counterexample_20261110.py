#!/usr/bin/env python3
"""V317 falsification: lane multiset conservation does not preserve load values.

Executable minimal reference memory semantics. A store followed by a load
cannot generally be exchanged, even when load multisets and store issue
sequences are identical. This checker deliberately does not claim GPU
memory-model completeness or RTL equivalence.
"""
from collections import Counter

def structural_signature(trace):
    loads = Counter()
    stores = []
    for event in trace:
        op, address, value = event
        if op == "L":
            loads[address] += 1
        elif op == "S":
            stores.append((address, value))
        else:
            raise ValueError("unknown operation")
    return loads, tuple(stores)

def execute(trace, initial):
    memory = dict(initial)
    observations = []
    for op, address, value in trace:
        if op == "S":
            memory[address] = value
        elif op == "L":
            observations.append((address, memory.get(address, 0)))
        else:
            raise ValueError("unknown operation")
    return tuple(observations), memory

def audit_pair(baseline, candidate, initial):
    conserved = structural_signature(baseline) == structural_signature(candidate)
    base_observed, base_memory = execute(baseline, initial)
    cand_observed, cand_memory = execute(candidate, initial)
    return {
        "structural_conservation": conserved,
        "load_values_equal": base_observed == cand_observed,
        "final_memory_equal": base_memory == cand_memory,
        "semantic_counterexample": conserved and base_observed != cand_observed,
    }

def tests():
    # One store and one load, identical lane and store signatures.
    before = [("S", 64, 7), ("L", 64, None)]
    after = [("L", 64, None), ("S", 64, 7)]
    result = audit_pair(before, after, {64: 3})
    assert result == {
        "structural_conservation": True,
        "load_values_equal": False,
        "final_memory_equal": True,
        "semantic_counterexample": True,
    }, result
    # Disjoint addresses are a control in this simple sequential model.
    control = audit_pair([("S", 64, 7), ("L", 128, None)],
                         [("L", 128, None), ("S", 64, 7)],
                         {64: 3, 128: 5})
    assert control["structural_conservation"] and control["load_values_equal"]
    assert not control["semantic_counterexample"]
    # Even with no stores, load order can affect observable register assignment.
    a = [("L", 64, None), ("L", 128, None)]
    b = [("L", 128, None), ("L", 64, None)]
    assert structural_signature(a) == structural_signature(b)
    assert execute(a, {64: 3, 128: 5})[0] != execute(b, {64: 3, 128: 5})[0]
    print("PASS: two semantic counterexamples and disjoint-address control")

if __name__ == "__main__":
    tests()
