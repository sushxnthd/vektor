#!/usr/bin/env python3
"""V317: exact finite-trace memory-order equivalence oracle (sequential model).

This is a *necessary bounded check*, not a GPU memory-model proof.
It catches the missing identity of load destinations in multiset-based audits.
Each event: (thread, op, address, register_or_value).
Store values are integers; load destinations are register names.
All traces execute in listed order with sequentially consistent byte cells.
"""
from collections import Counter
from itertools import permutations

def run(trace, initial):
    mem = dict(initial)
    registers = {}
    for thread, op, address, arg in trace:
        if op == "S":
            if not isinstance(arg, int):
                raise ValueError("store requires integer")
            mem[address] = arg
        elif op == "L":
            registers[(thread, arg)] = mem.get(address, 0)
        else:
            raise ValueError("bad opcode")
    return registers, mem

def signature(trace):
    # Preserve each thread's program order, load destination, and store value.
    by_thread = {}
    for event in trace:
        by_thread.setdefault(event[0], []).append(event[1:])
    return {k: tuple(v) for k, v in by_thread.items()}

def check(base, candidate, initials):
    if signature(base) != signature(candidate):
        return "INVALID_THREAD_ORDER"
    for initial in initials:
        if run(base, initial) != run(candidate, initial):
            return "SEMANTIC_MISMATCH"
    return "BOUNDED_PASS_NOT_PROOF"

def tests():
    # Cross-thread independent loads commute, even when their values differ.
    a = [(0,"L",0,"r0"), (1,"L",1,"r1")]
    b = list(reversed(a))
    assert check(a,b,({0:3,1:7},)) == "BOUNDED_PASS_NOT_PROOF"
    # Store/load cross-thread conflict; same thread-local signatures.
    a = [(0,"S",0,9),(1,"L",0,"r")]
    b = list(reversed(a))
    assert check(a,b,({0:2},)) == "SEMANTIC_MISMATCH"
    # Same-address load/load commutation is safe in this SC model.
    a = [(0,"L",0,"r0"),(1,"L",0,"r1")]
    assert check(a,list(reversed(a)),({0:5},)) == "BOUNDED_PASS_NOT_PROOF"
    # Reordering a single thread is forbidden even if final values match.
    a = [(0,"L",0,"r0"),(0,"L",1,"r1")]
    assert check(a,list(reversed(a)),({0:0,1:0},)) == "INVALID_THREAD_ORDER"
    # Exhaustively check every interleaving of one store and two tagged loads.
    events = [(0,"S",0,7),(1,"L",0,"x"),(2,"L",1,"y")]
    for perm in permutations(events):
        verdict = check(events,perm,({0:1,1:2},{0:7,1:2}))
        expected = all(run(events,s)==run(perm,s) for s in ({0:1,1:2},{0:7,1:2}))
        assert (verdict=="BOUNDED_PASS_NOT_PROOF")==expected
    print("PASS: tagged destination, thread order, conflict and exhaustive interleavings")

if __name__=="__main__":
    tests()
