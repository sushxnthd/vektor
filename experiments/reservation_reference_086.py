"""Independent absolute-cycle event calendar for Vektor-086 reservation RTL.
No dependence on RTL shift-register representation; no hardware PPA claim.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from random import Random

class Calendar:
    def __init__(self, banks, requests, max_latency, ports):
        self.banks, self.requests = banks, requests
        self.max_latency, self.ports = max_latency, ports
        self.cycle = 0
        self.events = defaultdict(int)

    def step(self, reset, valid, bank, latency):
        if reset:
            self.events.clear()
            grants = [0] * self.requests
            due = [0] * self.banks
        else:
            due = [self.events.get((self.cycle, b), 0) for b in range(self.banks)]
            grants = [0] * self.requests
            for i in range(self.requests):
                b, l = bank[i], latency[i]
                if valid[i] and 0 <= b < self.banks and 1 <= l <= self.max_latency:
                    target = (self.cycle + l, b)
                    if self.events[target] < self.ports:
                        grants[i] = 1
                        self.events[target] += 1
            assert all(0 <= x <= self.ports for x in due)
        self.cycle += 1
        return grants, due

def pack(values, width):
    return sum(v << (i * width) for i, v in enumerate(values))

def stimulus(c, rng, banks, reqs, max_latency, cycles):
    if c < cycles // 32:
        return [1]*reqs, [0]*reqs, [1]*reqs, 'hot'
    if c < cycles // 16:
        return [1]*reqs, [i % banks for i in range(reqs)], [1]*reqs, 'spread'
    if c < cycles * 3 // 32:
        return [1]*reqs, [0]*reqs, [(i % max_latency)+1 for i in range(reqs)], 'staggered'
    if c < cycles // 8:
        return [1]*reqs, [i % banks for i in range(reqs)], [0]*reqs, 'invalid'
    if c >= cycles * 7 // 8:
        return ([rng.randrange(2) for _ in range(reqs)],
                [rng.randrange(banks) for _ in range(reqs)],
                [rng.randrange(1 << max(1, (max_latency+1).bit_length())) for _ in range(reqs)],
                'surprise')
    return ([rng.randrange(2) for _ in range(reqs)],
            [rng.randrange(banks) for _ in range(reqs)],
            [rng.randrange(max_latency+2) for _ in range(reqs)],
            'random')

def generate(out, banks=4, reqs=4, max_latency=4, ports=1, cycles=4096, seed=20261010):
    assert 1 <= banks <= 4 and 1 <= reqs <= 6 and 1 <= max_latency <= 5
    assert 1 <= ports <= 3
    bank_w = max(1, (banks-1).bit_length())
    lat_w = max(1, (max_latency+1).bit_length())
    count_w = max(1, ports.bit_length())
    rng = Random(seed)
    ref = Calendar(banks, reqs, max_latency, ports)
    counts = defaultdict(lambda: [0, 0])
    resets = {0, 17, 103, cycles//2, cycles*3//4}
    with out.open('w') as f:
        for c in range(cycles):
            valids, bs, ls, phase = stimulus(c, rng, banks, reqs, max_latency, cycles)
            reset = c in resets
            grants, due = ref.step(reset, valids, bs, ls)
            if not reset:
                counts[phase][0] += sum(valids)
                counts[phase][1] += sum(grants)
            f.write('%d %x %x %x %x %x\n' % (
                0 if reset else 1, pack(valids, 1), pack(bs, bank_w),
                pack(ls, lat_w), pack(grants, 1), pack(due, count_w)))
    result = dict(seed=seed, banks=banks, requests=reqs, max_latency=max_latency,
                  write_ports=ports, cycles=cycles, surprise_probes=cycles//8,
                  surprise_fraction=0.125, reset_cycles=sorted(resets),
                  by_phase={k:dict(offered=v[0], accepted=v[1]) for k,v in sorted(counts.items())})
    out.with_suffix('.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result

def self_test():
    x=Calendar(4,4,4,1)
    g,d=x.step(False,[1]*4,[0]*4,[1,2,3,4]); assert g==[1]*4 and d==[0]*4
    for _ in range(4):
        g,d=x.step(False,[0]*4,[0]*4,[1]*4); assert d[0]==1
    x=Calendar(4,4,4,1)
    x.step(False,[1]*4,[0]*4,[1,2,3,4]); x.step(True,[1]*4,[0]*4,[1]*4)
    for _ in range(6):
        _,d=x.step(False,[0]*4,[0]*4,[1]*4); assert d==[0]*4
    x=Calendar(4,4,4,1)
    g,_=x.step(False,[1]*4,[0]*4,[2]*4); assert g==[1,0,0,0]
    x=Calendar(4,4,4,1)
    x.step(False,[1,0,0,0],[0]*4,[2]*4)
    g,_=x.step(False,[1,0,0,0],[0]*4,[1]*4); assert g==[0]*4
    x=Calendar(3,6,5,2)
    g,_=x.step(False,[1]*6,[0]*6,[2]*6); assert g==[1,1,0,0,0,0]

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('output',type=Path)
    p.add_argument('--banks',type=int,default=4)
    p.add_argument('--reqs',type=int,default=4)
    p.add_argument('--max-latency',type=int,default=4)
    p.add_argument('--ports',type=int,default=1)
    p.add_argument('--cycles',type=int,default=4096)
    p.add_argument('--seed',type=int,default=20261010)
    a=p.parse_args()
    self_test()
    print(json.dumps(generate(a.output,a.banks,a.reqs,a.max_latency,a.ports,a.cycles,a.seed),sort_keys=True))
