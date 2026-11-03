#!/usr/bin/env python3
"""Independent frozen B8/16/24/32 replay using separate enumerating oracle."""
import json
import random
import sys
from fractions import Fraction
from research.v317.rtl.audit_exact_bank_partition_transfer import solve

def audit(result):
    assert tuple(result['bank_counts'])==(8,16,24,32)
    assert tuple(result['seeds'])==(1103,2113,3119)
    assert result['samples_per_seed']==8000
    n=0
    for b in (8,16,24,32):
        row=result['by_bank'][str(b)]
        for seed in (1103,2113,3119):
            rng=random.Random(seed)
            g=o=0
            for _ in range(8000):
                batch=tuple((rng.randrange(b),rng.randrange(b)) for _ in range(4))
                x,y=solve(batch)
                g+=x;o+=y
                n+=1
            assert row['seeds'][str(seed)]=={'greedy':g,'oracle':o,'opportunities':o-g}
        g=sum(x['greedy'] for x in row['seeds'].values())
        o=sum(x['oracle'] for x in row['seeds'].values())
        assert row['greedy']==g and row['oracle']==o and row['opportunities']==o-g
        assert abs(row['rate_ratio_with_0p5pct_delay']-float(Fraction(o,g)/Fraction(1005,1000)))<1e-14
    return {'status':'PASS','independent_vectors':n}

if __name__=='__main__':
    with open(sys.argv[1]) as f:r=json.load(f)
    print(json.dumps(audit(r),indent=2))
