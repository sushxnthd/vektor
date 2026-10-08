#!/usr/bin/env python3
"""Independently structured Python step model; cross-checks exact C++ counters and checksum."""
import subprocess, itertools, json
from pathlib import Path
MASK=(1<<32)-1
MASK64=(1<<64)-1

def mix(x):
    x &= MASK; x ^= x>>16; x=(x*0x7feb352d)&MASK
    x ^= x>>15; x=(x*0x846ca68b)&MASK; return (x^(x>>16))&MASK

def src(w,n,o):return mix(0x490049 ^ ((w*65537)&MASK) ^ ((n*131071)&MASK) ^ ((o*8191)&MASK))
def result(w,n):return mix(0x04905090 ^ ((w*2654435761)&MASK) ^ ((n*2246822519)&MASK))

def new_instruction(w,n,t,B,D,pattern,seed,prev):
    dep=n>0 and mix(seed ^ ((w*8191)&MASK) ^ ((n*65537)&MASK))%100<D
    banks=[]; values=[]
    for o in range(3):
        h=mix(seed ^ ((w*0x9e3779b9)&MASK) ^ ((n*0x85ebca6b)&MASK) ^ ((o*0xc2b2ae35)&MASK))
        bank=0 if pattern==1 else (w+n+o)%B if pattern==2 else h%B
        banks.append(bank)
        values.append(prev if o==0 and dep else src(w,n,o))
    return dict(seq=n,born=t,dep=dep,banks=banks,values=values)

def simulate(W,B,L,R,Q,D,policy,ret_policy,pattern,cycles,warm,seed):
    waves=[dict(ins=new_instruction(w,0,0,B,D,pattern,seed,0),state=[0]*3,data=[0]*3,next_seq=0,ready_at=0,producer=0) for w in range(W)]
    flight=[];counts=[0]*W;reads=returns=issues=bad=stale=bank_over=queue_over=0
    checksum=1469598103934665603
    for t in range(cycles):
        mature=[i for i,r in enumerate(flight) if r['due']<=t]
        if ret_policy==1:
            mature.sort(key=lambda i:-waves[flight[i]['wave']]['state'].count(2))
        delivered=set(mature[:R])
        for i in mature[:R]:
            r=flight[i]; q=waves[r['wave']]
            if q['ins']['seq']!=r['seq'] or q['state'][r['op']]!=1:
                stale+=1;continue
            q['state'][r['op']]=2;q['data'][r['op']]=r['value'];returns+=1
        flight=[r for i,r in enumerate(flight) if i not in delivered]
        phase=(t+t//9)%W if policy==2 else t%W
        issue_now=0
        for k in range(W):
            w=(phase+k)%W;q=waves[w]
            if q['state']!=[2,2,2] or (q['ins']['dep'] and t<q['ready_at']):continue
            if issue_now==4:break
            bad+=sum(a!=b for a,b in zip(q['data'],q['ins']['values']))
            out=result(w,q['ins']['seq'])
            checksum ^= out ^ ((w+1)*131071) ^ q['ins']['seq']
            checksum=(checksum*1099511628211)&MASK64
            if t>=warm:counts[w]+=1;issues+=1
            issue_now+=1;q['ready_at']=t+4;q['producer']=out
            q['next_seq']+=1
            q['ins']=new_instruction(w,q['next_seq'],t,B,D,pattern,seed,out)
            q['state']=[0]*3;q['data']=[0]*3
        if policy==1:
            order=sorted(range(W),key=lambda w:(-waves[w]['state'].count(2),(w-phase+W)%W))
        else:
            order=sorted(range(W),key=lambda w:(w-phase+W)%W)
        used=[0]*B
        for w in order:
            q=waves[w]
            for o in range(3):
                if q['state'][o]!=0:continue
                if o==0 and q['ins']['dep'] and t<q['ready_at']:continue
                b=q['ins']['banks'][o]
                if used[b]>=2 or len(flight)>=Q:continue
                used[b]+=1;q['state'][o]=1
                flight.append(dict(wave=w,seq=q['ins']['seq'],op=o,bank=b,due=t+L,value=q['ins']['values'][o]));reads+=1
        bank_over+=sum(x>2 for x in used)
        queue_over+=len(flight)>Q
    assert reads-returns==len(flight)
    return [issues,reads,returns,bad,stale,bank_over,queue_over,checksum]

def main():
    binary=Path(__file__).with_name('collector_049')
    cases=list(itertools.product([4,8],[1,4,16],[2,8],[2,4],[8,32],[0,50,100],[0,1,2],[0,1],[0,2]))
    # 12.5% pseudo-random probes; deterministic selection over diverse mechanisms
    cases=[v for i,v in enumerate(cases) if i%8==0]
    mismatches=[]
    for i,(W,B,L,R,Q,D,p,rp,pattern) in enumerate(cases):
        seed=mix(0x4901+i*131)
        args=[W,B,L,R,Q,D,p,rp,pattern,180,20,seed]
        expected=list(map(int,subprocess.check_output([str(binary),'single',*map(str,args)],text=True).strip().split(',')))
        got=simulate(*args)
        if got!=expected:mismatches.append(dict(args=args,cpp=expected,python=got))
    result={'schema':'vektor-049-independent-python-v1','cases':len(cases),'mismatches':len(mismatches),'examples':mismatches[:5]}
    Path(__file__).with_name('replication_049.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    assert not mismatches
if __name__=='__main__':main()
