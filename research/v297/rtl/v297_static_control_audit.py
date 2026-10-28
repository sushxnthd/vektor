#!/usr/bin/env python3
"""Independent symbolic and bank-level oracle for optimized V297 rotating control.

Checks abstract pair compatibility (including combinations impossible under bank
semantics), then concrete two-read-port bank constraints and temporal phase.
This is not a substitute for Verilog simulation or physical STA.
"""
import itertools
import random

PAIRS=((0,1),(0,2),(1,2))

def serial(valid, compatibility, phase):
    accepted=[]
    for offset in range(3):
        i=(phase+offset)%3
        if not (valid & (1<<i)):
            continue
        if len(accepted)<2 and all(compatibility[tuple(sorted((i,j)))] for j in accepted):
            accepted.append(i)
    return sum(1<<i for i in accepted)

def static(valid, compatibility, phase):
    p01=bool((valid&3)==3 and compatibility[(0,1)])
    p02=bool((valid&5)==5 and compatibility[(0,2)])
    p12=bool((valid&6)==6 and compatibility[(1,2)])
    if phase==0:
        return 3 if p01 else 5 if p02 else 1 if valid&1 else 6 if p12 else 2 if valid&2 else 4 if valid&4 else 0
    if phase==1:
        return 6 if p12 else 3 if p01 else 2 if valid&2 else 5 if p02 else 4 if valid&4 else 1 if valid&1 else 0
    return 5 if p02 else 6 if p12 else 4 if valid&4 else 3 if p01 else 1 if valid&1 else 2 if valid&2 else 0

def fits_pair(x,y):
    return all((x+y).count(bank)<=2 for bank in set(x+y))

def check():
    symbolic=0
    for valid in range(8):
        for phase in range(3):
            for bits in itertools.product((False,True),repeat=3):
                comp=dict(zip(PAIRS,bits))
                assert serial(valid,comp,phase)==static(valid,comp,phase), (valid,phase,bits)
                symbolic+=1
    rng=random.Random(0x2972026)
    concrete=0
    negative_detected=False
    for n in range(120000):
        # Alternate uniform, single-hot, and adversarial two-bank regimes.
        banks=16 if n%3==0 else 1 if n%3==1 else 2
        operands=[(rng.randrange(banks),rng.randrange(banks)) for _ in range(3)]
        valid=rng.randrange(8)
        phase=n%3
        comp={ij:fits_pair(operands[ij[0]],operands[ij[1]]) for ij in PAIRS}
        expect=serial(valid,comp,phase)
        got=static(valid,comp,phase)
        assert expect==got,(n,valid,phase,operands,expect,got)
        # Negative control: a broken fixed-phase controller must be caught.
        if expect!=static(valid,comp,0):negative_detected=True
        concrete+=1
    assert negative_detected, 'negative control was not detected'
    print(f'V297_STATIC_ROTATION_ORACLE_PASS symbolic={symbolic} concrete={concrete} negative_control_detected=1')

if __name__=='__main__':check()
