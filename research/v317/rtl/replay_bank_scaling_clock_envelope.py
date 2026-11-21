#!/usr/bin/env python3
"""Replay frozen B8/16/24/32 synthetic bank scaling and conditional clock sweep."""
import json
import random
from fractions import Fraction
from research.v317.rtl.exact_bank_partition_transfer import outcome

BANKS=(8,16,24,32)
SEEDS=(1103,2113,3119)
N=8000

def run():
    rows={}
    for b in BANKS:
        seeds={}
        for s in SEEDS:
            rng=random.Random(s)
            g=o=0
            for _ in range(N):
                x,y=outcome(tuple((rng.randrange(b),rng.randrange(b)) for i in range(4)))
                g+=x;o+=y
            seeds[str(s)]={'greedy':g,'oracle':o,'opportunities':o-g}
        g=sum(x['greedy'] for x in seeds.values())
        o=sum(x['oracle'] for x in seeds.values())
        ratio=Fraction(o,g)
        rows[str(b)]={'seeds':seeds,'greedy':g,'oracle':o,
                      'opportunities':o-g,'gain':float(ratio-1),
                      'max_added_delay_ps_at_2ns':float(2000*(ratio-1)),
                      'rate_ratio_with_0p5pct_delay':float(ratio/Fraction(1005,1000))}
    return {'schema':'vektor.v317.replay_bank_scaling_clock_envelope.v1',
            'frozen_protocol':'FROZEN_BANK_SCALING_CLOCK_ENVELOPE_20261103.md',
            'evidence_tier':'synthetic two-cycle oracle, not GPU performance',
            'bank_counts':BANKS,'seeds':SEEDS,'samples_per_seed':N,'by_bank':rows}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
