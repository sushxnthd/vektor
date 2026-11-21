#!/usr/bin/env python3
"""V317 bounded-buffer backpressure falsification (synthetic; NOT GPU RTL).

Every cycle: retire output, move bank requests into bounded output FIFO,
then admit new requests subject to a global in-flight credit limit.
Service is work-conserving. The independent token oracle tracks identities.
"""
from collections import deque
from itertools import product

def counts(cycles, arrivals, bank_rate, out_rate, credits, fifo_depth):
    bank = out = done = accepted = blocked = 0
    for t in range(cycles):
        out_take = min(out, out_rate)
        out -= out_take
        done += out_take
        move = min(bank, bank_rate, fifo_depth - out)
        bank -= move
        out += move
        want = arrivals[t]
        take = min(want, max(0, credits - bank - out))
        bank += take
        accepted += take
        blocked += want - take
        assert accepted == done + bank + out
        assert out <= fifo_depth and bank + out <= credits
    return (accepted, done, blocked, bank, out)

def tokens(cycles, arrivals, bank_rate, out_rate, credits, fifo_depth):
    bank, out = deque(), deque()
    accepted = done = blocked = 0
    serial = 0
    for t in range(cycles):
        for _ in range(min(out_rate, len(out))):
            out.popleft()
            done += 1
        for _ in range(min(bank_rate, len(bank), fifo_depth - len(out))):
            out.append(bank.popleft())
        for _ in range(arrivals[t]):
            if len(bank) + len(out) < credits:
                bank.append(serial)
                serial += 1
                accepted += 1
            else:
                blocked += 1
        assert accepted == done + len(bank) + len(out)
    return (accepted, done, blocked, len(bank), len(out))

def test():
    n = 0
    for length in range(5):
        for arrivals in product(range(3), repeat=length):
            for bank_rate, out_rate, credits, fifo_depth in product(range(3), range(3), range(4), range(4)):
                a = counts(length, arrivals, bank_rate, out_rate, credits, fifo_depth)
                b = tokens(length, arrivals, bank_rate, out_rate, credits, fifo_depth)
                assert a == b, (length, arrivals, bank_rate, out_rate, credits, fifo_depth, a, b)
                n += 1
    # Fixed output bottleneck: faster bank cannot improve steady-state completions.
    slow = counts(100, [4]*100, 1, 1, 8, 2)
    fast = counts(100, [4]*100, 2, 1, 8, 2)
    assert fast[1] <= slow[1] + 1, (slow, fast)
    # With output headroom, candidate can win, conditional on credit capacity.
    slow2 = counts(100, [4]*100, 1, 2, 8, 2)
    fast2 = counts(100, [4]*100, 2, 2, 8, 2)
    assert fast2[1] > slow2[1], (slow2, fast2)
    # No buffer credits: no throughput despite nominal bank/output capacity.
    assert counts(100, [4]*100, 2, 2, 0, 2)[1] == 0
    print("PASS", n, "exhaustive token-vs-count cases")
    print("output-limited", slow, fast)
    print("output-headroom", slow2, fast2)
    print("Limitations: zero latency within each stage, fixed per-cycle arrivals, no clock/area/RTL evidence")

if __name__ == "__main__":
    test()
