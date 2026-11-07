#!/usr/bin/env python3
"""V317 falsification: an occupancy-limited producer can erase bank-service gains.

Deterministic, zero-cost synthetic model, NOT RTL or GPU measurements.
Physical time is in integer ticks. Each tick: issue up to occupancy slots,
then retire up to bank capacity, then up to shared output capacity.
All queues and issued/completed totals are conserved. No claim of novelty.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Result:
    issued: int
    completed: int
    pending_bank: int
    pending_output: int

def run(ticks, demand, occupancy, bank, output):
    assert ticks >= 0 and min(demand, occupancy, bank, output) >= 0
    issued = done = bank_q = out_q = 0
    for _ in range(ticks):
        new = min(demand, occupancy)
        issued += new
        bank_q += new
        moved = min(bank_q, bank)
        bank_q -= moved
        out_q += moved
        retired = min(out_q, output)
        out_q -= retired
        done += retired
        assert issued == done + bank_q + out_q
    return Result(issued, done, bank_q, out_q)

def independent_reference(ticks, demand, occupancy, bank, output):
    # Independently track every request as a token rather than queue counts.
    bank_q, out_q = [], []
    issued = completed = 0
    for t in range(ticks):
        for j in range(min(demand, occupancy)):
            bank_q.append((t, j))
            issued += 1
        for _ in range(min(bank, len(bank_q))):
            out_q.append(bank_q.pop(0))
        for _ in range(min(output, len(out_q))):
            out_q.pop(0)
            completed += 1
    return Result(issued, completed, len(bank_q), len(out_q))

def test():
    cases = 0
    for ticks in range(0, 9):
        for demand in range(0, 5):
            for occupancy in range(0, 5):
                for bank in range(0, 5):
                    for output in range(0, 5):
                        actual = run(ticks, demand, occupancy, bank, output)
                        expected = independent_reference(ticks, demand, occupancy, bank, output)
                        assert actual == expected, (ticks, demand, occupancy, bank, output)
                        # Constant per-tick arrivals and capacities yield exact service law.
                        assert actual.completed == ticks * min(demand, occupancy, bank, output)
                        cases += 1
    # Predeclared predicted-no-win: occupancy bottleneck.
    a = run(1000, 4, 1, 1, 4)
    b = run(1000, 4, 1, 2, 4)
    assert a.completed == b.completed == 1000
    # Predeclared conditional predicted-win: all other limits permit doubling.
    c = run(1000, 4, 4, 1, 4)
    d = run(1000, 4, 4, 2, 4)
    assert c.completed == 1000 and d.completed == 2000
    # Shared output port erases that gain.
    e = run(1000, 4, 4, 1, 1)
    f = run(1000, 4, 4, 2, 1)
    assert e.completed == f.completed == 1000
    print(f"PASS: {cases} independently cross-checked finite-horizon cases")
    print("NO-WIN occupancy: 1000/1000; conditional win: 2000/1000; output bottleneck: 1000/1000")
    print("Scope: constant deterministic arrivals, ideal zero-cost service, no RTL or clock effects.")

if __name__ == "__main__":
    test()
