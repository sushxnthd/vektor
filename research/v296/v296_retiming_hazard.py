#!/usr/bin/env python3
"""V296 two-port RF delayed-read semantic falsification, not RTL/STA evidence."""
import itertools, json, random

def delayed(rf, reads, write, mode):
    after = list(rf)
    old = {}
    if write is not None:
        addr, value = write
        if mode == 'global' or (mode == 'selective' and addr in reads):
            old[addr] = rf[addr]
        after[addr] = value
    return tuple(old[a] if a in old else after[a] for a in reads)

def exhaustive():
    counts = dict(cases=0, collisions=0, naive_bad=0, global_bad=0, selective_bad=0)
    for rf in itertools.product(range(4), repeat=4):
        for reads in itertools.product(range(4), repeat=2):
            expected = tuple(rf[a] for a in reads)
            for write in (None, *itertools.product(range(4), repeat=2)):
                counts['cases'] += 1
                counts['collisions'] += write is not None and write[0] in reads
                for mode in ('naive', 'global', 'selective'):
                    counts[mode+'_bad'] += delayed(rf, reads, write, mode) != expected
    assert counts['cases'] == 69632 and counts['naive_bad'] == 21504
    assert counts['global_bad'] == counts['selective_bad'] == 0
    return counts

def synthetic(seed=2961028, cycles=50000):
    rng = random.Random(seed)
    rf = [rng.randrange(256) for _ in range(128)]
    result = dict(seed=seed, cycles=cycles, operands=0, collisions=0,
                  naive_bad=0, global_bad=0, selective_bad=0)
    for _ in range(cycles):
        bank_counts = [0]*16
        reads = []
        for _ in range(rng.randrange(9)):
            bank = rng.choice([b for b in range(16) if bank_counts[b]<2])
            bank_counts[bank] += 1
            reads.append(bank*8+rng.randrange(8))
        result['operands'] += len(reads)
        expected = tuple(rf[a] for a in reads)
        write = (rng.randrange(128),rng.randrange(256)) if rng.randrange(5) else None
        result['collisions'] += write is not None and write[0] in reads
        for mode in ('naive','global','selective'):
            result[mode+'_bad'] += delayed(rf,reads,write,mode) != expected
        if write is not None:
            rf[write[0]] = write[1]
    assert result['global_bad'] == result['selective_bad'] == 0
    return result

def bounds():
    return [dict(N=n,B=b,base=min(4,b,n),retimed=min(4,b,n/2))
            for n in (1,2,4,8) for b in (1,2,4)]

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--output')
    args=p.parse_args()
    result=dict(evidence='reduced-state exhaustive and synthetic Python reference models',
        exhaustive=exhaustive(),synthetic=synthetic(),
        port_counterexample=dict(bank=0,operand_words=[0,1],write_word=2,
                                 needed_distinct_reads=3,allowed_reads=2),
        upper_bound_sensitivity=bounds(),
        verdict='naive delay invalid; global old-value log requires non-free third port in some cases; selective snapshot retains same-cycle RF data path',
        rtl=False,physical=False,matched=False,gpu_speedup=False,holdouts='SEALED')
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:
        with open(args.output,'w') as f:f.write(payload)
    else:print(payload)
if __name__=='__main__':main()
