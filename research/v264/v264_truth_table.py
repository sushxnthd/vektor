#!/usr/bin/env python3
from itertools import product
def dut(v0,v1,i0,i1,a0,a1,ready,wv,wa):
    addr=a0 if v0 else a1
    fire=ready and not(wv and wa==addr)
    same=v0 and v1 and i0==i1 and a0==a1
    g0=bool(v0 and fire)
    g1=bool(v1 and fire and (not v0 or same))
    return g0,g1,bool(g0 or g1),addr
def oracle(v0,v1,i0,i1,a0,a1,ready,wv,wa):
    addr=a0 if v0 else a1
    if not ready or (wv and wa==addr):return False,False,False,addr
    if not v0 and not v1:return False,False,False,addr
    if not v0:return False,True,True,addr
    if not v1:return True,False,True,addr
    if (i0,a0)==(i1,a1):return True,True,True,addr
    return True,False,True,addr
n=0
for x in product((0,1),(0,1),range(4),range(4),range(4),range(4),(0,1),(0,1),range(4)):
    assert dut(*x)==oracle(*x),x
    n+=1
print('PASS',n,'control combinations (software oracle, not RTL simulation)')
