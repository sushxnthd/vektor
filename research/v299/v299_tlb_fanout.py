#!/usr/bin/env python3
"""V299 synthetic GPU translation-retention falsification.

Evidence tier: trace-level TLB hit/miss and non-overlapped warp-stall work only.
No real GPU traces, DRAM/TLB page-walk overlap, PPA, or IPC.
Run: python3 v299_tlb_fanout.py --selftest --evaluate
"""
import argparse
import json
import random
from dataclasses import dataclass
from statistics import mean

SEEDS = (503, 509, 521, 523)  # holdout, not exploratory seeds 11/17/23/31
REGIMES = ('phase', 'uniform', 'skew', 'scan', 'reverse', 'burst', 'ample')
POLICIES = ('lru', 'lfu', 'fanout_lru', 'fanout_lfu', 'v299')
CYCLES = 20000
WALK_LATENCY = 100  # cycles per miss; proxy, not physical overlap

@dataclass
class Entry:
    page: int
    last: int
    frequency: int
    fanout_bin: int

class TranslationCache:
    def __init__(self, policy, capacity):
        assert policy in POLICIES
        self.policy, self.capacity = policy, capacity
        self.entries = {}
        self.misses = self.stall_work = self.evictions = 0

    def victim(self, tick):
        assert len(self.entries) == self.capacity
        def key(e):
            age = tick - e.last
            if self.policy == 'lru':
                return (e.last, e.page)
            if self.policy == 'lfu':
                return (e.frequency, e.last, e.page)
            if self.policy == 'fanout_lru':
                return (int(e.fanout_bin >= 2), e.last, e.page)
            if self.policy == 'fanout_lfu':
                return (e.frequency * e.fanout_bin, e.last, e.page)
            # V299: two-bit frequency and two-bit fanout, decayed by age.
            # This integer right-shift is synthesizable; age is capped at 4 bins.
            return ((e.frequency * e.fanout_bin) >> min(4, age // 16), e.last, e.page)
        return min(self.entries.values(), key=key).page

    def access(self, page, fanout, tick):
        assert fanout >= 1
        fanout_bin = min(3, max(1, (fanout + 1) // 2))
        if page in self.entries:
            e = self.entries[page]
            e.last = tick
            e.frequency = min(3, e.frequency + 1)
            e.fanout_bin = fanout_bin
            return
        self.misses += 1
        self.stall_work += fanout * WALK_LATENCY
        if len(self.entries) >= self.capacity:
            del self.entries[self.victim(tick)]
            self.evictions += 1
        self.entries[page] = Entry(page, tick, 1, fanout_bin)

def generate(regime, seed, count=CYCLES):
    rng = random.Random(seed)
    hot_phase = False
    for t in range(count):
        if regime == 'uniform':
            yield rng.randrange(16), 1
        elif regime == 'ample':
            hot = rng.random() < .65
            yield (rng.randrange(4), 8) if hot else (100 + rng.randrange(10), 1)
        elif regime == 'burst':
            if t % 32 == 0:
                hot_phase = rng.random() < .65
            yield (rng.randrange(4), 8) if hot_phase else (100 + rng.randrange(40), 1)
        elif regime in ('skew', 'scan', 'reverse', 'phase'):
            hot = rng.random() < (.35 if regime == 'scan' else .65)
            if hot:
                page = (t // 3000 % 4) * 4 + rng.randrange(4) if regime == 'phase' else rng.randrange(4)
                yield page, (1 if regime == 'reverse' else 8)
            else:
                page = 100 + t if regime == 'scan' else 100 + rng.randrange(40)
                yield page, (8 if regime == 'reverse' else 1)
        else:
            raise ValueError(regime)

def evaluate():
    out = {'protocol': {'seeds': SEEDS, 'cycles_per_seed': CYCLES,
                        'walk_latency': WALK_LATENCY, 'policies': POLICIES}, 'regimes': {}}
    for regime in REGIMES:
        rows = []
        for seed in SEEDS:
            caches = {p: TranslationCache(p, 32 if regime == 'ample' else 8) for p in POLICIES}
            for tick, (page, fanout) in enumerate(generate(regime, seed)):
                for c in caches.values():
                    c.access(page, fanout, tick)
            rows.append({'seed': seed, 'policies': {p: {'misses': c.misses,
                           'stall_work': c.stall_work} for p, c in caches.items()}})
        means = {p: {'misses': mean(r['policies'][p]['misses'] for r in rows),
                      'stall_work': mean(r['policies'][p]['stall_work'] for r in rows)} for p in POLICIES}
        strongest = min((p for p in POLICIES if p != 'v299'),
                        key=lambda p: means[p]['stall_work'])
        advantage = 1 - means['v299']['stall_work'] / means[strongest]['stall_work']
        out['regimes'][regime] = {'per_seed': rows, 'means': means,
                                  'strongest_control': strongest,
                                  'v299_stall_advantage_fraction': advantage}
    return out

def selftest():
    # Small deterministic equivalence and invariants; no holdout generator used.
    for policy in POLICIES:
        c = TranslationCache(policy, 2)
        c.access(10, 8, 0)
        c.access(11, 1, 1)
        c.access(10, 8, 2)
        assert c.misses == 2 and len(c.entries) == 2
        c.access(12, 1, 3)
        assert c.misses == 3 and len(c.entries) == 2 and c.evictions == 1
        assert c.stall_work == (8 + 1 + 1) * WALK_LATENCY
        assert set(c.entries) <= {10, 11, 12}
    # V299 must evict stale expensive translations once their age bucket expires.
    c = TranslationCache('v299', 2)
    c.access(1, 8, 0); c.access(1, 8, 1)
    c.access(2, 1, 2)
    assert c.victim(3) == 2
    assert c.victim(100) == 1
    # No artificial 'win' on capacity-sufficient reference trace.
    for policy in POLICIES:
        c = TranslationCache(policy, 16)
        for t, (page, fan) in enumerate(generate('ample', 11, 200)):
            c.access(page, fan, t)
        assert c.misses <= 14
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        selftest()
        print('selftest: PASS')
    if args.evaluate:
        print(json.dumps(evaluate(), indent=2, sort_keys=True))
    if not args.selftest and not args.evaluate:
        parser.print_help()

if __name__ == '__main__':
    main()
