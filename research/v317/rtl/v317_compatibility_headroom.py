#!/usr/bin/env python3
"""V317 necessary headroom bound; not a measured speedup or performance prediction.

For N baseline completions in T cycles, physical capacity C completions/cycle,
M externally identified compatible opportunities, each worth at most one
additional completion, and H whole cycles reserved exclusively for control:
candidate additions <= min(M, C*(T-H)-N). This requires exclusive control
cycles; overlapping control must NOT be charged as H. Negative upper bound
means baseline service cannot be maintained. M must come from an independent
trace rather than a scheduler self-report.
"""
from fractions import Fraction

def ceiling(T, C, N, M, H=0):
    assert all(isinstance(x, int) and not isinstance(x, bool)
               for x in (T,C,N,M,H))
    assert T>0 and C>0 and 0<N<=T*C and M>=0 and 0<=H<=T
    return min(M, C*(T-H)-N)

def gain_upper(T,C,N,M,H=0):
    return Fraction(ceiling(T,C,N,M,H),N)

def independent_enumeration(T,C,N,M,H):
    permitted=[k for k in range(C*(T-H)+1) if k-N<=M]
    return Fraction(max(permitted)-N,N)

def run():
    assert gain_upper(100,1,100,100)==0  # frozen saturated no-win
    assert gain_upper(100,1,80,100)==Fraction(1,4) # possible, not observed
    assert gain_upper(100,1,80,5)==Fraction(1,16)
    assert gain_upper(100,1,80,100,20)==0
    assert gain_upper(100,1,80,100,21)==Fraction(-1,80)
    cases=0
    for T in range(1,7):
      for C in range(1,4):
       for N in range(1,T*C+1):
        for M in range(T*C+2):
         for H in range(T+1):
          assert gain_upper(T,C,N,M,H)==independent_enumeration(T,C,N,M,H)
          cases+=1
    print(f'PASS: {cases} exhaustive capacity/opportunity/control cases')
    print('Necessary bound only; no physical or unseen-workload validation.')
if __name__=='__main__': run()
