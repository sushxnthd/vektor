#!/usr/bin/env python3
"""Independent, rational-arithmetic physical break-even certificate for V317.

This is a necessary-condition filter, not an RTL or performance measurement.
The optimistic upper bound assumes at most one extra completion per four-request
batch, at least one greedy completion, no additional traffic or power costs.
"""
from fractions import Fraction

C = {3: 153, 4: 212, 5: 61, 6: 4}

def falling(b, k):
    v = 1
    for i in range(k):
        v *= b - i
    return v

def event_probability(b):
    if b < 2:
        raise ValueError("at least two banks required")
    return Fraction(sum(v * falling(b, k) for k, v in C.items()), b**8)

def upper_net(b, independent_fraction, clock_penalty):
    p = event_probability(b) * independent_fraction
    return (1 + p) / (1 + clock_penalty)

def minimum_independent_fraction(b, clock_penalty):
    p = event_probability(b)
    if p == 0:
        return None
    return clock_penalty / p

def main():
    delta = Fraction(1, 200)  # 0.5% clock-period increase
    print("banks,p_event,q_min_necessary,q_025_upper,q_1_upper,kill_even_if_q_1")
    for b in (4, 8, 12, 16, 32, 48, 64):
        p = event_probability(b)
        q_min = minimum_independent_fraction(b, delta)
        quarter = upper_net(b, Fraction(1, 4), delta)
        full = upper_net(b, Fraction(1), delta)
        print(f"{b},{float(p):.9f},{float(q_min):.6f},"
              f"{float(quarter):.9f},{float(full):.9f},{full <= 1}")
        assert full >= quarter
        assert q_min * p == delta
    assert upper_net(48, Fraction(1), delta) < 1
    assert upper_net(16, Fraction(1, 4), delta) < 1
    assert upper_net(4, Fraction(1), delta) > 1
    assert event_probability(64) < event_probability(48)
    # Independent limit: B^2 P(E) tends to four, not a measured GPU law.
    assert abs(float(64**2 * event_probability(64)) - 4) < 1
    print("PASS: rational break-even certificates")

if __name__ == "__main__":
    main()
