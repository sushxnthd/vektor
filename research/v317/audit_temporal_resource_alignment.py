#!/usr/bin/env python3
"""Independent falsification: whole-horizon min-of-sums need not predict service.

Synthetic necessary-condition audit, not GPU performance or RTL evidence.
"""
from itertools import product

def whole_horizon_upper(eligible, bank, output):
    return min(sum(bank), sum(output), sum(eligible))

def aligned_upper(eligible, bank, output):
    return sum(min(int(e), b, o) for e, b, o in zip(eligible, bank, output))

def run():
    n=8
    e=(True,)*n
    bank=(1,)*4+(0,)*4
    output=(0,)*4+(1,)*4
    assert whole_horizon_upper(e,bank,output)==4
    assert aligned_upper(e,bank,output)==0
    checked=0; loose=0; tight=0
    for es in product((False,True),repeat=4):
        for bs in product((0,1),repeat=4):
            for os in product((0,1),repeat=4):
                a=aligned_upper(es,bs,os)
                w=whole_horizon_upper(es,bs,os)
                assert 0<=a<=w
                loose+=(w>a)
                tight+=(w==a)
                checked+=1
    assert checked==4096 and loose>0 and tight>0
    print({'status':'PASS','cases':checked,'loose_cases':loose,'tight_cases':tight,
           'counterexample_whole_horizon':4,'counterexample_aligned':0,
           'interpretation':'Marginal resource totals cannot establish positive throughput without temporal coincidence. Synthetic only.'})
if __name__=='__main__': run()
