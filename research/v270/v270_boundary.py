#!/usr/bin/env python3
from itertools import product
import json
def eligible(a,b,mode,compatible=True):
 if not compatible or a+b>8: return False
 if mode=='static44': return a<=4 and b<=4
 if mode=='adaptive': return (a<=4 and b<=4) or (a<=6 and b<=2) or (b<=6 and a<=2)
 if mode=='full': return True
 raise ValueError(mode)
if __name__=='__main__':
 rows=[dict(a=a,b=b,static44=int(eligible(a,b,'static44')),adaptive=int(eligible(a,b,'adaptive')),full=int(eligible(a,b,'full'))) for a,b in product(range(1,9),repeat=2)]
 print(json.dumps(dict(law='T=r*(1+p_pair) under continuously offered precollected compatible warps; NOT GPU throughput',training_boundary=rows,counts=dict(adaptive_only_vs_static=sum(x['adaptive'] and not x['static44'] for x in rows),full_only_vs_adaptive=sum(x['full'] and not x['adaptive'] for x in rows))),indent=2))
