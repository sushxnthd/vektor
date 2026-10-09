#!/usr/bin/env python3
"""Independent transaction-level reference; emits cycle vectors for SV differential testing."""
import argparse, random, json

class Reference:
    def __init__(self,dedup):
        self.dedup=dedup
        self.slots=[None,None]
        self.rr=0
        self.error=0
        self.reads=0
        self.completions=0
        self.fanouts=0

    def outputs(self,issue_tag):
        free=next((i for i,x in enumerate(self.slots) if x is None),None)
        ready=int(free is not None and all(x['tag']!=issue_tag for x in self.slots if x))
        req=None
        for i in ((self.rr)%2,(self.rr+1)%2):
            x=self.slots[i]
            if x is None: continue
            for op,reg in enumerate(x['regs']):
                if op in x['sent']: continue
                if self.dedup and reg in x['regs'][:op]: continue
                req=(i,x['tag'],op,reg)
                break
            if req is not None: break
        done=next(((i,x) for i,x in enumerate(self.slots) if x is not None and len(x['got'])==3),None)
        return ready,free,req,done

    def step(self,stim,out):
        ready,free,req,done=out
        if done is not None and stim['complete_ready']:
            self.slots[done[0]]=None
            self.completions+=1
        if stim['issue_valid'] and ready:
            self.slots[free]={'tag':stim['issue_tag'],'regs':stim['regs'], 'sent':set(),'got':{}}
        if req is not None and stim['req_ready']:
            self.slots[req[0]]['sent'].add(req[2]); self.rr=(req[0]+1)%2;self.reads+=1
        if stim['resp'] is not None:
            tag,op,reg,val=stim['resp']
            matched=next((x for x in self.slots if x is not None and x['tag']==tag),None)
            if matched is None or op not in matched['sent'] or op in matched['got'] or matched['regs'][op]!=reg:
                self.error=1
            else:
                indices=[j for j,r in enumerate(matched['regs']) if r==reg] if self.dedup else [op]
                for j in indices:
                    matched['got'][j]=val
                    self.fanouts+=1

def pack(vals,bits):
    return sum(int(x)<<(bits*i) for i,x in enumerate(vals))

def generate(path,dedup,seed,cycles,alias_pct):
    rng=random.Random(seed)
    ref=Reference(dedup)
    future=[]
    candidate=None
    next_tag=0
    stream_rng=random.Random(seed+1000000)
    stream=[]
    for n in range(cycles+10):
        regs=[stream_rng.randrange(0,32)]
        for j in (1,2):
            if stream_rng.randrange(100)<alias_pct:
                regs.append(stream_rng.choice(regs))
            else:
                unused=[x for x in range(32) if x not in regs]
                regs.append(stream_rng.choice(unused))
        stream.append((n%256,regs))
    attempted=accepted=0
    lines=[]
    for cycle in range(cycles):
        if candidate is None:
            if rng.random()<0.82:
                candidate=stream[next_tag];next_tag+=1
        resp=None
        due=[q for q in future if q[0]<=cycle]
        if due and rng.random()<0.88:
            q=rng.choice(due);future.remove(q);resp=q[1:]
        if cycle==cycles//2:
            if resp is not None:future.append((cycle+1,*resp))
            resp=(255,3,255,0xBAD0BAD0)
        stim={
            'issue_valid':int(candidate is not None),
            'issue_tag':candidate[0] if candidate else 0,
            'regs':candidate[1] if candidate else [0,0,0],
            'req_ready':int(rng.random()<0.80),
            'resp':resp,
            'complete_ready':int(rng.random()<0.72)
        }
        out=ref.outputs(stim['issue_tag']);ready,free,req,done=out
        if stim['issue_valid']:attempted+=1
        if stim['issue_valid'] and ready:
            accepted+=1;candidate=None
        if req is not None and stim['req_ready']:
            _,tag,op,reg=req
            val=((tag*0x9E3779B1)^(reg*0x85EBCA6B)^0xABCDEF12)&0xffffffff
            future.append((cycle+rng.randrange(2,13),tag,op,reg,val))
        rtag,rop,rreg,rdata=(resp if resp is not None else (0,0,0,0))
        ctag=done[1]['tag'] if done else 0
        cdata=pack([done[1]['got'][i] for i in range(3)],32) if done else 0
        fields=[1,stim['issue_valid'],f'{stim["issue_tag"]:x}',f'{pack(stim["regs"],8):x}',
                stim['req_ready'],int(resp is not None),f'{rtag:x}',rop,f'{rreg:x}',f'{rdata:x}',
                stim['complete_ready'],ready,int(req is not None),f'{req[1]:x}' if req else '0',
                req[2] if req else 0,f'{req[3]:x}' if req else '0',int(done is not None),
                f'{ctag:x}',f'{cdata:x}',ref.error]
        lines.append(' '.join(map(str,fields)))
        ref.step(stim,out)
    with open(path,'w') as f:f.write('\n'.join(lines)+'\n')
    return dict(seed=seed,dedup=dedup,alias_pct=alias_pct,cycles=cycles,attempted=attempted,accepted=accepted,
                reads=ref.reads,completions=ref.completions,fanout_writes=ref.fanouts,
                pending_returns=len(future),error=ref.error)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('out');p.add_argument('--dedup',type=int,required=True)
    p.add_argument('--seed',type=int,default=540054);p.add_argument('--cycles',type=int,default=4000)
    p.add_argument('--alias',type=int,default=50);a=p.parse_args()
    print(json.dumps(generate(a.out,a.dedup,a.seed,a.cycles,a.alias),indent=2))
