#!/usr/bin/env python3
"""V317: falsify unconditional simultaneous-live-word storage gate.

This is a deliberately small *cycle-phase* transition model, not RTL or STA.
A bank read can either be registered before a return grant (registered mode)
or directly bypassed to the return datapath (bypass mode). A grant can consume
at most one complete two-word request per cycle. In bypass mode only a granted
request may use combinational operands; all other newly acquired operands
must be stored or the read must be suppressed. The checker enumerates choices
rather than assuming every read must occur.
"""
from itertools import product

def feasible(reads, grant, budget, bypass):
    """reads: tuple of acquired word counts (0..2), grant: request id or -1."""
    assert all(0 <= x <= 2 for x in reads)
    assert grant == -1 or 0 <= grant < len(reads)
    if grant != -1 and reads[grant] != 2:
        return False
    # In registered mode both words are live at the pre-retirement edge.
    # Bypass only eliminates storage for the granted complete request.
    held = sum(reads)
    if bypass and grant != -1:
        held -= reads[grant]
    return held <= budget

def audit():
    checked = 0
    bypass_rescues = 0
    for n in range(1, 5):
        for reads in product(range(3), repeat=n):
            for grant in (-1, *range(n)):
                if grant != -1 and reads[grant] != 2:
                    continue
                for budget in range(2*n+1):
                    registered = feasible(reads, grant, budget, False)
                    bypass = feasible(reads, grant, budget, True)
                    assert not registered or bypass
                    if bypass and not registered:
                        bypass_rescues += 1
                        assert grant != -1 and reads[grant] == 2
                    checked += 1
    assert feasible((2,), 0, 0, True)
    assert not feasible((2,), 0, 0, False)
    assert not feasible((2, 2), 0, 0, True)
    assert feasible((2, 2), 0, 2, True)
    print(f"PASS {checked} enumerated phase/budget states; "
          f"{bypass_rescues} bypass-only feasible states")
    print("Counterexample: one complete request, same-cycle return, "
          "zero registered operand words.")
    print("LIMIT: bypass timing, combinational bank-to-return path, "
          "fanout and output-port arbitration are unmeasured.")

if __name__ == "__main__":
    audit()
