#!/usr/bin/env python3
"""Standalone synthetic Vektor-057 collector model; not physical GPU evidence."""
from collections import defaultdict
import json,random
OPS={'A':(0,0),'B':(0,1),'C':(0,1,2)}
def simulate(seq,cycles=12000,slots=2,latency=3,returns=1,banks=1,ports=2,
             dedup=True,policy='fifo'):
    live={};due=defaultdict(list);ready=[]
    head=done=reads=backlog=0;first_done=None;max_wait=0
    for clock in range(cycles):
        ready.extend(due.pop(clock,[]))
        for _ in range(min(returns,len(ready))):
            if policy=='fifo':idx=0
            else:
                urgent=[i for i,r in enumerate(ready) if clock-r[2]>=4]
                if policy=='age_guard' and urgent:
                    idx=min(urgent,key=lambda i:(ready[i][2],i))
                else:
                    idx=min(range(len(ready)),key=lambda i:(
                        len(live[ready[i][0]]['roots'])-len(live[ready[i][0]]['got']),
                        ready[i][0],i))
            iid,root,arrived=ready.pop(idx)
            assert root in live[iid]['sent'] and root not in live[iid]['got']
            live[iid]['got'].add(root)
            max_wait=max(max_wait,clock-arrived)
        backlog+=len(ready)
        if ready:max_wait=max(max_wait,max(clock-r[2] for r in ready))
        if policy=='age_guard':
            assert max_wait<=4+(3*slots+returns-1)//returns
        for iid in list(live):
            if len(live[iid]['got'])==len(live[iid]['roots']):
                if iid==0:first_done=clock
                del live[iid];done+=1
        if head<len(seq) and len(live)<slots:
            src=seq[head]
            roots=tuple(dict.fromkeys(src)) if dedup else tuple(range(len(src)))
            regs={r:r for r in roots} if dedup else dict(enumerate(src))
            live[head]=dict(roots=roots,regs=regs,sent=set(),got=set())
            head+=1
        budget=[ports]*banks
        for iid,item in live.items():
            for root in item['roots']:
                if root in item['sent']:continue
                bank=item['regs'][root]%banks
                if budget[bank]:
                    budget[bank]-=1;item['sent'].add(root)
                    due[clock+latency].append((iid,root,clock+latency))
                    reads+=1;break
    return dict(completed=done,reads=reads,first_done=first_done,
                backlog_area=backlog,max_wait=max_wait)
def pattern(s,n):
    return [OPS[x] for x in s]*(n//len(s)+50)
def main():
    seq=pattern('BACB',12000)
    b=simulate(seq,dedup=False)
    d=simulate(seq,dedup=True)
    p=simulate(seq,dedup=True,policy='near_done')
    a=simulate(seq,dedup=True,policy='age_guard')
    assert (b['completed'],d['completed'],p['completed'],a['completed'])==(5332,4798,5332,5332)
    assert (b['reads'],d['reads'])==(12000,9600)
    assert simulate(pattern('BACB',48000),cycles=48000)['completed']==19198
    adv=[OPS['C']]+[OPS['A']]*1500
    starved=simulate(adv,cycles=1000,slots=8,policy='near_done')
    guarded=simulate(adv,cycles=1000,slots=8,policy='age_guard')
    assert starved['first_done'] is None and guarded['first_done']==9
    rng=random.Random(570400);wins=losses=ties=0
    for _ in range(96):
        pat=''.join(rng.choice('ABC') for _ in range(rng.randint(2,10)))
        if 'A' not in pat:pat='A'+pat[1:]
        s=pattern(pat,3000)
        x=simulate(s,cycles=3000)['completed']
        y=simulate(s,cycles=3000,policy='age_guard')['completed']
        wins+=(y>x);losses+=(y<x);ties+=(y==x)
    assert (wins,losses,ties)==(29,0,67)
    print(json.dumps(dict(baseline=b,dedup=d,completion=p,guard=a,
      starved_first=starved['first_done'],guard_first=guarded['first_done'],
      holdout_wins=wins,holdout_losses=losses,holdout_ties=ties),indent=2))
if __name__=='__main__':main()
