#!/usr/bin/env python3
"""V292 E0 falsifier: same-resource conventional sector packer vs overlay."""
import json
import random
L=32
SEED=29220261023

def overlay(a,b,credits):
    aa=bool(a['valid'] and credits>0)
    ab=bool(aa and b['valid'] and credits>1 and not(a['mask']&b['mask']))
    bus=tuple(a['data'][i] if aa and (a['mask']>>i)&1 else
              b['data'][i] if ab and (b['mask']>>i)&1 else 0 for i in range(L))
    return (aa,ab,bus,a['mask'] if aa else 0,b['mask'] if ab else 0,
            a['tag'] if aa else 0,b['tag'] if ab else 0)

def conventional_sector_packer(a,b,credits):
    admitted=[]
    if a['valid'] and credits:
        admitted.append(a)
        if b['valid'] and credits>=2 and not(a['mask']&b['mask']):
            admitted.append(b)
    words=[0]*L
    for p in admitted:
        for lane in range(L):
            if p['mask']&(1<<lane):
                assert words[lane]==0
                words[lane]=p['data'][lane]
    return (len(admitted)>=1,len(admitted)==2,tuple(words),
            a['mask'] if len(admitted)>=1 else 0,
            b['mask'] if len(admitted)==2 else 0,
            a['tag'] if len(admitted)>=1 else 0,
            b['tag'] if len(admitted)==2 else 0)

def pkt(r,mask,valid=True):
    return {'mask':mask,'valid':valid,'tag':r.randrange(1,65536),
            'data':tuple(r.randrange(1,2**32) for _ in range(L))}

def check(a,b,credits):
    x=overlay(a,b,credits)
    y=conventional_sector_packer(a,b,credits)
    assert x==y,(x,y)
    return int(x[0])+int(x[1]),int(x[1])

def main():
    r=random.Random(SEED)
    cases=0
    for ma in range(256):
        for mb in range(256):
            check(pkt(r,ma),pkt(r,mb),2)
            cases+=1
    regimes=[]
    for q,credits,name in ((.08,2,'win_sparse'),(.70,2,'no_win_dense'),
                            (.08,1,'no_win_single_collector'),
                            (.2,2,'training_20'),(.5,2,'training_50')):
        paired=served=0
        n=40000
        for _ in range(n):
            ma=sum((r.random()<q)<<i for i in range(L))
            mb=sum((r.random()<q)<<i for i in range(L))
            grants,pair=check(pkt(r,ma),pkt(r,mb),credits)
            served+=grants
            paired+=pair
            cases+=1
        regimes.append({'name':name,'q':q,'collector_credits':credits,
                        'pairs':paired,'samples':n,'mean_packets_per_beat':served/n,
                        'overlay_over_matched_packer':1.0})
    print(json.dumps({'evidence_class':'E0','seed':SEED,'cases':cases,
                      'mismatches':0,'control':'same-resource conventional sector packer',
                      'result':'structurally equivalent on every tested packet',
                      'regimes':regimes,
                      'caveat':'Not RTL simulation, PPA, STA or an integrated GPU workload'},indent=2))

if __name__=='__main__':
    main()
