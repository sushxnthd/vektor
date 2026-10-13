#!/usr/bin/env python3
"""Independent transaction-level V146 model. This is not RTL verification."""
import argparse
import json
import random

class Collector:
    def __init__(self):
        self.active = False
        self.tag = 0
        self.regs = (0, 0, 0)
        self.vals = [None] * 3

    def step(self, enq, rsp, wb, dispatch_ready, reset=False):
        if reset:
            self.__init__()
            return (False, False, (False, False), None)
        enq_ready = not self.active
        dispatch = self.active and all(v is not None for v in self.vals)
        ready_regs = set()
        if self.active and not dispatch:
            ready_regs = {r for r, v in zip(self.regs, self.vals) if v is None}
        elig = [valid and reg in ready_regs and not (wb and wb[0] == reg)
                for valid, reg, bank, data in rsp]
        accept = (elig[0], elig[1] and not (elig[0] and rsp[0][2] == rsp[1][2]))
        observed = (enq_ready, dispatch, accept,
                    (self.tag, tuple(self.vals)) if dispatch else None)
        if not self.active:
            if enq:
                self.active, self.tag, self.regs = True, enq[0], enq[1]
                self.vals = [None] * 3
        elif dispatch and dispatch_ready:
            self.active = False
        elif not dispatch:
            for i, reg in enumerate(self.regs):
                if self.vals[i] is not None:
                    continue
                if wb and wb[0] == reg:
                    self.vals[i] = wb[1]
                else:
                    for j in (1, 0):
                        if accept[j] and rsp[j][1] == reg:
                            self.vals[i] = rsp[j][3]
                            break
        return observed

class IndependentOracle:
    def __init__(self):
        self.job = None

    def step(self, enq, rsp, wb, dispatch_ready, reset=False):
        if reset:
            self.job = None
            return (False, False, (False, False), None)
        j = self.job
        done = j is not None and len(j['got']) == 3
        missing = [] if j is None or done else [
            j['src'][k] for k in range(3) if k not in j['got']]
        accepted = [False, False]
        for port in (0, 1):
            valid, reg, bank, data = rsp[port]
            if not valid or reg not in missing or (wb is not None and reg == wb[0]):
                continue
            if port == 1 and accepted[0] and bank == rsp[0][2]:
                continue
            accepted[port] = True
        observed = (j is None, done, tuple(accepted),
                    (j['tag'], tuple(j['got'][k] for k in range(3))) if done else None)
        if j is None:
            if enq is not None:
                self.job = {'tag': enq[0], 'src': enq[1], 'got': {}}
        elif done:
            if dispatch_ready:
                self.job = None
        else:
            for k, reg in enumerate(j['src']):
                if k in j['got']:
                    continue
                if wb is not None and wb[0] == reg:
                    j['got'][k] = wb[1]
                else:
                    matches = [p for p in (0, 1) if accepted[p] and rsp[p][1] == reg]
                    if matches:
                        j['got'][k] = rsp[matches[-1]][3]
        return observed

def run(seed=146, cycles=50000):
    rng = random.Random(seed)
    a, b = Collector(), IndependentOracle()
    stats = dict(cycles=cycles, seed=seed, matched=0, retired=0,
                 accepted_rf=0, blocked_same_bank=0, wb_cycles=0,
                 dispatch_stalls=0, duplicate_jobs=0, resets=0)
    for t in range(cycles):
        reset = (t % 10003 == 0)
        regs = tuple(rng.randrange(64) for _ in range(3))
        if t % 3 == 0:
            regs = (regs[0], regs[0], regs[2])
        if t % 7 == 0:
            regs = (regs[0], regs[1], regs[0])
        enq = (t % 256, regs) if rng.random() < .8 else None
        src = b.job['src'] if b.job is not None else regs
        rsp = []
        for port in range(2):
            reg = rng.choice(src) if rng.random() < .8 else rng.randrange(64)
            rsp.append((rng.random() < .8, reg, reg % 16, rng.getrandbits(1024)))
        wb = None
        if rng.random() < .35:
            reg = rng.choice(src) if rng.random() < .8 else rng.randrange(64)
            wb = (reg, rng.getrandbits(1024))
        dispatch_ready = rng.random() < .75
        out_a = a.step(enq, rsp, wb, dispatch_ready, reset)
        out_b = b.step(enq, rsp, wb, dispatch_ready, reset)
        if out_a != out_b:
            raise AssertionError((t, out_a, out_b, enq, rsp, wb))
        stats['matched'] += 1
        if out_a[1] and dispatch_ready:
            stats['retired'] += 1
        if out_a[1] and not dispatch_ready:
            stats['dispatch_stalls'] += 1
        if out_a[0] and enq and len(set(enq[1])) < 3:
            stats['duplicate_jobs'] += 1
        stats['accepted_rf'] += sum(out_a[2])
        if (rsp[0][0] and rsp[1][0] and rsp[0][2] == rsp[1][2]
                and out_a[2][0] and not out_a[2][1]):
            stats['blocked_same_bank'] += 1
        stats['wb_cycles'] += wb is not None
        stats['resets'] += reset
    assert stats['retired'] > 100 and stats['blocked_same_bank'] > 10
    assert stats['dispatch_stalls'] > 10 and stats['duplicate_jobs'] > 100
    return stats

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=146)
    p.add_argument('--cycles', type=int, default=50000)
    args = p.parse_args()
    print(json.dumps(run(args.seed, args.cycles), indent=2, sort_keys=True))
