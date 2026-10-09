#!/usr/bin/env python3
"""H7 preregistered: equal-mean variance creates occupancy cliffs; synthetic."""
import json
import random

def issue_rate(tags, lifetimes):
    free_at = [0] * tags
    cycle = 0
    for lifetime in lifetimes:
        index = min(range(tags), key=lambda j: free_at[j])
        cycle = max(cycle, free_at[index])
        free_at[index] = cycle + lifetime
        cycle += 1
    return len(lifetimes) / max(free_at)

def run():
    cases = []
    for seed in (77, 181, 293):
        rng = random.Random(seed)
        shuffled = [2] * 5000 + [10] * 5000
        rng.shuffle(shuffled)
        fixed = [6] * 10000
        assert sum(shuffled) == sum(fixed)
        for tags in (2, 4, 6, 8, 12):
            a = issue_rate(tags, fixed)
            b = issue_rate(tags, shuffled)
            cases.append(dict(seed=seed, tags=tags, fixed=a, bimodal=b,
                              relative_loss=(a-b)/a))
    h7a = all(c['relative_loss'] > 0.08 for c in cases if c['tags'] == 6)
    h7b = all(c['relative_loss'] < 0.01 for c in cases if c['tags'] == 12)
    summary = dict(n=len(cases), h7a=h7a, h7b=h7b,
                   six_tag_loss=[c['relative_loss'] for c in cases if c['tags']==6],
                   twelve_tag_loss=[c['relative_loss'] for c in cases if c['tags']==12])
    assert h7a and h7b
    with open('research/065/results/variance_cliff_065.json', 'w') as f:
        json.dump(dict(preregistered='H7: 6 tags >8% relative loss; 12 tags <1% loss',
                       summary=summary, cases=cases), f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    run()
