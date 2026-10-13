#!/usr/bin/env python3
"""Exhaustive V144 arbiter capacity, bank and work-conservation checks."""
import itertools,csv,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from response_arbiter import choose_responses
class Op:
    def __init__(self,src):self.src=src
count=0
rows=[]
for banks in itertools.product(range(3),repeat=4):
 for mask in range(1,16):
  for bus in [1,2,3]:
   for policy in ['oldest_scan','finish_first']:
    reads=[(0,i,0,i) for i in range(4)]
    ops=[Op((i,i+4,i+8)) for i in range(4)]
    pc=[0,1,2,3]
    active={i:{'values':{1:11,2:22} if i%2 else {}} for i in range(4)}
    ready=[i for i in range(4) if mask&(1<<i)]
    chosen=choose_responses(reads,ready,active,ops,pc,list(banks)+[0]*12,10,bus,1,False,policy)
    assert chosen.issubset(ready)
    assert len(chosen)==min(bus,len({banks[i] for i in ready}))
    assert len({banks[i] for i in chosen})==len(chosen)
    rows.append([*banks,mask,bus,int(policy=='finish_first'),sum(1<<i for i in chosen)])
    count+=1
out=ROOT/'verification'/'selector_vectors.csv'
with out.open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['bank0','bank1','bank2','bank3','ready','bus','finish_first','grant']);w.writerows(rows)
print('PASS',count,'exhaustive selector cases')
