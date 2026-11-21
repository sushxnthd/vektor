#!/usr/bin/env python3
"""V317 exact storage feasibility for retained two-operand requests.

This is a *necessary* resource check, not a throughput simulator or RTL.
For every outstanding request, each acquired operand consumes one word of
retention until completion. Requests completed in a cycle release both words.
A proposed schedule must never exceed the physical word budget, including
fully acquired requests waiting for a return grant. In-flight reads and
same-cycle bypass are deliberately excluded; this is a registered-retention
model. Any design using bypass must establish a separate timing/area proof.
"""
from itertools import product

def live_words(states):
    # 0=unread, 1/2=one operand, 3=both; completed requests omitted
    return sum(s.bit_count() for s in states)

def feasible(states, word_budget):
    return live_words(states) <= word_budget

def audit():
    cases = 0
    underestimated = 0
    for n in range(1, 7):
        for states in product(range(4), repeat=n):
            actual = live_words(states)
            request_slots = sum(s != 0 for s in states)
            partial = sum(s in (1, 2) for s in states)
            full = sum(s == 3 for s in states)
            assert actual == partial + 2 * full
            for budget in range(2 * n + 1):
                # A request-slot budget is an invalid replacement for a
                # word budget whenever a fully acquired request is pending.
                if request_slots <= budget < actual:
                    underestimated += 1
                    assert full > 0
                assert feasible(states, budget) == (actual <= budget)
                cases += 1
    # Two simultaneously fully-read requests blocked behind one return:
    # one can retire; the other retains two words. A two-word budget is
    # enough only AFTER retirement, not for the pre-retirement state.
    assert not feasible((3, 3), 2)
    assert feasible((0, 3), 2)
    # Three pending full requests need six words, not three request slots.
    assert live_words((3, 3, 3)) == 6
    assert not feasible((3, 3, 3), 3)
    print(f"PASS {cases} exhaustive state/budget pairs; "
          f"{underestimated} false-feasible request-slot cases")
    print("Necessary boundary: W >= partial + 2*full, "
          "with all simultaneously live requests charged.")
    print("LIMIT: no measured service gain, area, timing, electrical or power evidence.")

if __name__ == "__main__":
    audit()
