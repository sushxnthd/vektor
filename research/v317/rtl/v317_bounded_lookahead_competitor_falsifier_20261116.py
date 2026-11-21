#!/usr/bin/env python3
"""Independent bounded-lookahead falsifier for the V296 adjacent fusion model.

Synthetic bank-queue model, NOT RTL, routed timing, or a physically matched
alternative. Lookahead preserves per-bank FIFO for indistinguishable requests.
Lookahead implementation area/timing must be measured before a fair hardware
comparison; equal bank-port count alone is NOT equal total resources.
"""
from fractions import Fraction
from itertools import product

def run(banks, policy, service=1, issue=4, overhead=1, window=4):
    assert policy in ('single', 'adjacent', 'lookahead')
    assert service > 0 and issue > 0 and overhead >= 0 and window >= 2
    pending = list(enumerate(banks))
    free = [0] * (max(banks, default=1)+1)
    t = 0
    while pending:
        if policy == 'single':
            chosen = [0]
        elif policy == 'adjacent':
            chosen = [0]
            if len(pending)>1 and pending[0][1]!=pending[1][1]:
                chosen.append(1)
        else:
            chosen = [0]
            second = next((j for j in range(1,min(window,len(pending)))
                           if pending[j][1]!=pending[0][1]),None)
            if second is not None:
                chosen.append(second)
        if policy != 'single':
            t += overhead
        selected = [pending[j] for j in chosen]
        for j in reversed(chosen):
            del pending[j]
        for _, b in selected:
            free[b] = max(free[b],t)+service
        t += issue
    return max([t]+free)

def audit():
    # These cases are model checks, not prospective hardware holdouts.
    cases = {
        'adjacent_alternating': ((0,1)*64, 'WIN'),
        'clustered_pairs': ((0,0,1,1)*32, 'WIN'),
        'single_bank': ((0,)*128, 'NO_WIN'),
    }
    for name,(seq,pred) in cases.items():
        b=run(seq,'single'); a=run(seq,'adjacent'); l=run(seq,'lookahead')
        ratio=Fraction(b,a)*Fraction(1000,1001)**2
        actual='WIN' if ratio>1 else 'NO_WIN'
        assert actual==pred,(name,b,a,l,actual)
        print(name,'single',b,'adjacent',a,'lookahead',l,
              'adjacent_hypothetical_area_clock_adjusted',float(ratio))
    better = worse = equal = 0
    example = None
    for n in range(2,11):
        for seq in product(range(2),repeat=n):
            a=run(seq,'adjacent')
            l=run(seq,'lookahead')
            better += l<a
            worse += l>a
            equal += l==a
            if l<a and example is None:
                example=(seq,a,l)
    assert better>0
    print('lookahead comparisons better/worse/equal',better,worse,equal,
          'first strict improvement',example)
    print('WARNING: no synthesis, equal-total-area, electrical, or GPU evidence')

if __name__=='__main__':
    audit()
