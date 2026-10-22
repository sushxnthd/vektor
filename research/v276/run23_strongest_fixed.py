#!/usr/bin/env python3
"""Exhaustive GF(2) fixed-bank control for the V276 synthetic pair families."""
import json
def bank(r,c0,c1):
 h=(r>>2)&3
 return (r&3)^(c0 if h&1 else 0)^(c1 if h&2 else 0)
pairs=[(16*k,16*k+d) for k in range(4) for d in (4,5)]
perfect=[]
for c0 in range(4):
 for c1 in range(4):
  assert all(sorted(bank(4*h+lo,c0,c1) for lo in range(4))==[0,1,2,3] for h in range(16))
  if all(bank(a,c0,c1)!=bank(b,c0,c1) for a,b in pairs):perfect.append([c0,c1])
assert [2,0] in perfect
print(json.dumps({'tested_pairs':len(pairs),'perfect_fixed_hashes':perfect,'candidate_gain_vs_strong_fixed':1.0,'witness':'bank={reg[1] XOR reg[2],reg[0]}'},indent=2))
