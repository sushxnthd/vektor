#!/usr/bin/env python3
"""Independent list-based implementation of the 065 fabric abstraction."""
import random
from quiescence_065 import simulate

def replica(seed, tags, count, dup_p, max_gap, policy, loss_p):
    rng = random.Random(seed)
    events = []
    slots = [None] * tags
    serial = issued = credits = false = stale = retired = injected = terminal = 0
    for cycle in range(200000):
        due = [e for e in events if e[0] <= cycle]
        events = [e for e in events if e[0] > cycle]
        for _, tag, owner, delivered in due:
            terminal += 1
            slot = slots[tag]
            if slot is not None and slot[0] == owner:
                slot[1] -= 1
            if delivered:
                if slot is None:
                    stale += 1
                elif not slot[2]:
                    slot[2] = True
                    if slot[0] == owner:
                        credits += 1
                    else:
                        false += 1
                elif slot[0] != owner:
                    stale += 1
        for tag, slot in enumerate(slots):
            if slot is not None and slot[2] and (policy == 'first_delivery' or slot[1] == 0):
                slots[tag] = None
                retired += 1
        if issued < count:
            free = next((j for j, slot in enumerate(slots) if slot is None), None)
            if free is not None:
                issued += 1
                serial += 1
                delay = rng.randint(1, 4)
                copies = [(cycle + delay, True)]
                if rng.random() < dup_p:
                    copies.append((cycle + delay + rng.randint(1, max_gap), rng.random() >= loss_p))
                slots[free] = [serial, len(copies), False]
                for due_at, deliver in copies:
                    injected += 1
                    events.append((due_at, free, serial, deliver))
        if issued == count and not any(slot is not None for slot in slots) and not events:
            return (cycle + 1, retired, credits, false, stale, injected, terminal)
    raise AssertionError('replica horizon exceeded')

def run():
    rng = random.Random(650650)
    for i in range(72):
        seed = rng.randrange(1000000)
        tags = rng.randint(1, 8)
        p = rng.random()
        gap = rng.randint(1, 45)
        loss = rng.random()
        policy = ('first_delivery', 'quiescence')[i % 2]
        a = simulate(seed, tags, 150, p, gap, policy, loss)
        b = replica(seed, tags, 150, p, gap, policy, loss)
        assert (a['cycles'], a['retired'], a['good_credits'], a['false_credits'],
                a['stale'], a['injected'], a['terminal']) == b, (i, a, b)
    print('PASS 72 independent list/event-heap differential comparisons')

if __name__ == '__main__':
    run()
