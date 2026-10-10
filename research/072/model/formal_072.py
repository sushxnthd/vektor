#!/usr/bin/env python3
"""Vektor-072: bounded atomic-event exploration, NOT unbounded RTL proof."""
from collections import deque
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class S:
    phase: int = 0  # E0 active/freeze/fenced, E1 active/freeze/fenced
    producer: tuple = ()  # (epoch, kind) 0=initial 1=replay
    fabric: tuple = ()  # physical copies
    admitted: int = 0
    ack: bool = False

CAP=2
BUDGET=2

def transitions(s, unsafe=False):
    p=s.phase
    epoch=0 if p<3 else 1
    if p in (0,3) and s.admitted<BUDGET and len(s.producer)<CAP:
        for kind in (0,1):
            yield f'admit {"replay" if kind else "initial"} E{epoch}', S(p,s.producer+((epoch,kind),),s.fabric,s.admitted+1,False),False
    if p in (0,3):
        yield 'freeze source',S(p+1,s.producer,s.fabric,s.admitted,False),False
    if s.producer:
        for copies in (1,2):
            if len(s.fabric)+copies<=CAP:
                tok=s.producer[0]
                yield f'emit {copies} copy E{tok[0]}',S(p,s.producer[1:],s.fabric+(tok,)*copies,s.admitted,s.ack),False
    if s.fabric:
        tok=s.fabric[0]
        for drop in (False,True):
            stale=(not drop) and p>=3 and tok[0]==0
            yield f'{"drop" if drop else "deliver"} E{tok[0]}',S(p,s.producer,s.fabric[1:],s.admitted,s.ack),stale
    if p in (1,4) and not s.producer and not s.ack:
        yield 'source fence ack',S(p,s.producer,s.fabric,s.admitted,True),False
    if p in (1,4) and s.ack and (unsafe or not s.fabric):
        yield 'retire epoch',S(p+1,s.producer,s.fabric,s.admitted,True),False
    if p==2:
        yield 'reuse UID=0 in E1',S(3,s.producer,s.fabric,0,False),False

def explore(unsafe=False):
    initial=S();todo=deque([initial]);parent={initial:None};edges=0;phases=set()
    while todo:
        s=todo.popleft();phases.add(s.phase)
        for action,t,stale in transitions(s,unsafe):
            edges+=1
            if stale:
                path=[action];cur=s
                while parent[cur] is not None:
                    cur,prev_action=parent[cur];path.append(prev_action)
                return {'safe':False,'states':len(parent),'edges':edges,'counterexample':list(reversed(path)),'phases':sorted(phases)}
            if t not in parent:
                parent[t]=(s,action);todo.append(t)
    return {'safe':True,'states':len(parent),'edges':edges,'counterexample':None,'phases':sorted(phases)}

def main():
    global CAP,BUDGET
    good=explore(False);bad=explore(True)
    assert good['safe'] and not bad['safe'] and good['states']==148 and good['edges']==389
    assert bad['states']==100 and bad['edges']==221 and 5 in good['phases']
    probes=[]
    for cap in (1,2,3,4):
        for budget in (1,2,3):
            CAP,BUDGET=cap,budget
            s=explore(False);u=explore(True)
            assert s['safe'] and not u['safe']
            probes.append({'capacity':cap,'budget':budget,'safe_states':s['states'],'safe_edges':s['edges'],
                           'unsafe_states_before_counterexample':u['states'],'unsafe_edges_before_counterexample':u['edges']})
    CAP,BUDGET=2,2
    output={'model':'atomic events; 2 source slots, 2 fabric slots, <=2 admissions/epoch, two epochs, reused UID=0',
            'safe':good,'unsafe':bad,'exploratory_probes':probes,
            'limitations':['finite abstract-state exploration, not unbounded RTL proof','no hidden replay sources','single clock/reset domain','no physical PPA']}
    Path(__file__).with_name('formal_results_072.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
