"""Vektor-062: deterministic synthetic transaction-tag lifetime experiment.
A 'strong fence' is an ASSUMED fabric quiescence oracle, not implemented RTL.
"""
from collections import defaultdict
from random import Random
import json

def jobs(seed, n=2000, p=.02):
    r=Random(seed)
    return [(a:=r.randint(1,6), max(a,128 if r.random()<p else r.randint(a,9))) for _ in range(n)]

def simulate(work, tags, mode, ttl, ack, broken=False, limit=20000):
    free=set(range(tags)); live={}; events=defaultdict(list)
    issued=done=bad=reject=0
    for t in range(limit):
        for kind,tag,owner in events.pop(t,[]):
            if kind=='data':
                if tag in live and live[tag][0]!=owner:
                    if not live[tag][1]: bad+=1
                    else:reject+=1
                elif tag not in live:reject+=1
                elif not live[tag][1]:live[tag][1]=True;done+=1
                else:reject+=1
            else:
                assert tag in live and live[tag][0]==owner
                del live[tag];free.add(tag)
        if issued<len(work) and free:
            tag=min(free);free.remove(tag);first,replay=work[issued]
            issued+=1;live[tag]=[issued,False]
            events[t+first].append(('data',tag,issued))
            if replay>first:events[t+replay].append(('data',tag,issued))
            release=t+ttl+1 if mode=='ttl' else t+(first if broken else replay)+ack+1
            events[release].append(('release',tag,issued))
        if issued==len(work) and not live:
            return (issued,done,t+1,bad,reject)
    return (issued,done,limit,bad,reject)

def independent(work,tags,mode,ttl,ack,limit=20000):
    ready=[0]*tags;issued=0;completions=[]
    for t in range(limit):
        if issued<len(work):
            free=[k for k,v in enumerate(ready) if v<=t]
            if free:
                k=min(free);first,replay=work[issued];issued+=1
                ready[k]=t+(ttl+1 if mode=='ttl' else replay+ack+1)
                completions.append(t+first)
        if issued==len(work) and t>=max(ready):
            end=t+1;break
    else:end=limit
    return (issued,sum(x<end for x in completions),end)

def main():
    bad=simulate([(1,10),(9,9)],1,'fence',10,0,broken=True)
    good=simulate([(1,10),(9,9)],1,'fence',10,0)
    assert bad[3]==1 and good[3]==0,(bad,good)
    rows=[];tight=[];checks=0
    for seed in (2,17,101):
      for p in (0.,.02,.1):
       work=jobs(seed,p=p)
       for tags in (1,2,4,8):
        for ack in (0,2,16,64,192):
         a=simulate(work,tags,'ttl',128,ack)
         b=simulate(work,tags,'fence',128,ack)
         for mode,obs in (('ttl',a),('fence',b)):
          assert obs[:3]==independent(work,tags,mode,128,ack)
          assert obs[3]==0
          checks+=1
         rows.append({'p':p,'tags':tags,'ack':ack,
                      'ratio':(b[1]/b[2])/(a[1]/a[2])})
       if p==0.:
        for tags in (1,2,4,8):
         for ack in (0,2,8,16):
          a=simulate(work,tags,'ttl',9,ack)
          b=simulate(work,tags,'fence',9,ack)
          assert a[3]==b[3]==0
          tight.append({'tags':tags,'ack':ack,
                        'ratio':(b[1]/b[2])/(a[1]/a[2])})
    summary={'pairs':len(rows),'replica_checks':checks,'tight_pairs':len(tight),
             'fence_wins':sum(x['ratio']>1.000001 for x in rows),
             'ttl_wins':sum(x['ratio']<.999999 for x in rows),
             'tight_fence_wins':sum(x['ratio']>1.000001 for x in tight),
             'tight_ttl_wins':sum(x['ratio']<.999999 for x in tight),
             'broken_ack_false_credits':bad[3],
             'strong_fence_false_credits':good[3]}
    assert summary=={'pairs':180,'replica_checks':360,'tight_pairs':48,
                     'fence_wins':144,'ttl_wins':36,
                     'tight_fence_wins':23,'tight_ttl_wins':24,
                     'broken_ack_false_credits':1,'strong_fence_false_credits':0}
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
