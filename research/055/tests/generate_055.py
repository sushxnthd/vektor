#!/usr/bin/env python3
"""Vektor-055 reference model. PTX mix is static-uniform, not a dynamic GPU trace."""
import random
from pathlib import Path

PTX_MIX=((247,2,False),(10,2,True),(21,3,False))
def pack(vals,width):
    return sum(int(v)<<(i*width) for i,v in enumerate(vals))

class Reference:
    def __init__(self,dedup):
        self.dedup=bool(dedup);self.slots=[None,None];self.rr=0;self.error=0
        self.reads=0;self.completions=0;self.fanout=0
    def outputs(self,issue_tag):
        free=next((i for i,x in enumerate(self.slots) if x is None),None)
        ready=int(free is not None and all(x['tag']!=issue_tag for x in self.slots if x))
        req=None
        for i in (self.rr,1-self.rr):
            x=self.slots[i]
            if x is None:continue
            for op in range(3):
                if not (x['mask']>>op)&1 or op in x['sent']:continue
                if self.dedup and any(((x['mask']>>j)&1) and x['regs'][j]==x['regs'][op] for j in range(op)):continue
                req=(i,x['tag'],op,x['regs'][op]);break
            if req is not None:break
        done=next(((i,x) for i,x in enumerate(self.slots) if x is not None and all(not ((x['mask']>>j)&1) or j in x['got'] for j in range(3))),None)
        return ready,free,req,done
    def step(self,stim,out):
        ready,free,req,done=out
        if done is not None and stim['complete_ready']:
            self.slots[done[0]]=None;self.completions+=1
        if stim['issue_valid'] and ready:
            self.slots[free]={'tag':stim['issue_tag'],'regs':stim['regs'],'mask':stim['mask'],'sent':set(),'got':{}}
        if req is not None and stim['req_ready']:
            self.slots[req[0]]['sent'].add(req[2]);self.rr=(req[0]+1)%2;self.reads+=1
        if stim['resp'] is not None:
            tag,op,reg,value=stim['resp']
            x=next((x for x in self.slots if x is not None and x['tag']==tag),None)
            if x is None or op not in x['sent'] or op in x['got'] or x['regs'][op]!=reg:self.error=1
            else:
                indices=[j for j in range(3) if (x['mask']>>j)&1 and x['regs'][j]==reg] if self.dedup else [op]
                for j in indices:x['got'][j]=value;self.fanout+=1

def make_instruction(rng,mode,n):
    if mode=='ptx':
        choice=rng.randrange(sum(x[0] for x in PTX_MIX))
        for weight,count,aliased in PTX_MIX:
            if choice<weight:break
            choice-=weight
        mask=(1<<count)-1;regs=rng.sample(range(64),count)
        if aliased:regs[1]=regs[0]
    elif mode=='zero':
        count=rng.choice([2,3]);mask=(1<<count)-1;regs=rng.sample(range(64),count)
    elif mode=='maskstress':
        mask=(0,1,2,4,6,5,7,7)[n%8];regs=rng.sample(range(64),3)
        if n%8==4:regs[0]=regs[1]
        elif n%8==5:regs[2]=regs[0]
        elif n%8==6:regs[1]=regs[2]=regs[0]
        return n%256,regs,mask
    else:
        count=3;mask=7;regs=rng.sample(range(64),count);p=int(mode.replace('synth',''))
        for i in (1,2):
            if rng.randrange(100)<p:regs[i]=rng.choice(regs[:i])
    regs+=rng.sample([v for v in range(64) if v not in regs],3-len(regs))
    return n%256,regs,mask

def generate(path,dedup,seed,cycles,mode):
    rng=random.Random(seed);srng=random.Random(seed+1000000);ref=Reference(dedup)
    stream=[make_instruction(srng,mode,i) for i in range(cycles+20)]
    next_inst=0;candidate=None;future=[];offered=accepted=0;lines=[]
    for cycle in range(cycles):
        if candidate is None and rng.random()<0.85:candidate=stream[next_inst];next_inst+=1
        due=[x for x in future if x[0]<=cycle];resp=None
        if due and rng.random()<0.9:q=rng.choice(due);future.remove(q);resp=q[1:]
        if cycle==cycles//2:
            if resp is not None:future.append((cycle+1,*resp))
            resp=(255,3,255,0xBAD0BAD0)
        tag,regs,mask=candidate if candidate is not None else (0,[0,0,0],0)
        stim={'issue_valid':int(candidate is not None),'issue_tag':tag,'regs':regs,'mask':mask,'req_ready':int(rng.random()<0.80),'resp':resp,'complete_ready':int(rng.random()<0.75)}
        out=ref.outputs(tag);ready,free,req,done=out
        if stim['issue_valid']:offered+=1
        if stim['issue_valid'] and ready:accepted+=1;candidate=None
        if req is not None and stim['req_ready']:
            _,qtag,op,reg=req
            value=((qtag*0x9E3779B1)^(reg*0x85EBCA6B)^0xABCDEF12)&0xffffffff
            future.append((cycle+rng.randrange(2,13),qtag,op,reg,value))
        rt,rop,rr,rv=resp if resp is not None else (0,0,0,0)
        ct=done[1]['tag'] if done else 0
        cd=pack([done[1]['got'].get(j,0) for j in range(3)],32) if done else 0
        fields=[1,stim['issue_valid'],f'{tag:x}',f'{pack(regs,8):x}',f'{mask:x}',stim['req_ready'],int(resp is not None),f'{rt:x}',rop,f'{rr:x}',f'{rv:x}',stim['complete_ready'],ready,int(req is not None),f'{req[1]:x}' if req else '0',req[2] if req else 0,f'{req[3]:x}' if req else '0',int(done is not None),f'{ct:x}',f'{cd:x}',ref.error]
        lines.append(' '.join(map(str,fields)));ref.step(stim,out)
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text('\n'.join(lines)+'\n')
    return dict(mode=mode,seed=seed,dedup=dedup,cycles=cycles,offered=offered,accepted=accepted,reads=ref.reads,completions=ref.completions,fanout=ref.fanout,error=ref.error,pending=len(future))
