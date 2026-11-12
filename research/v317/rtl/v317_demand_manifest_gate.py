#!/usr/bin/env python3
"""Independent offered-demand conservation gate. Accounting, NOT GPU timing."""
import csv, json, argparse
from collections import defaultdict

def load(path, fields):
    with open(path,newline='') as f:
        reader=csv.DictReader(f)
        if set(reader.fieldnames or ()) != set(fields): raise ValueError('schema mismatch')
        return [{k:int(r[k]) for k in fields} for r in reader]

def audit(manifest, trace, *, cycles, banks, reads, returns, words, registered=True):
    if min(cycles,banks,reads,returns)<=0 or words<0: raise ValueError('invalid resource')
    offered={}
    for r in load(manifest,('request_id','arrival_cycle','bank0','bank1')):
        rid=r['request_id']
        if rid<0 or rid in offered or not 0<=r['arrival_cycle']<cycles or not 0<=r['bank0']<banks or not 0<=r['bank1']<banks:
            raise ValueError('invalid offered demand')
        offered[rid]=r
    by_cycle=defaultdict(list)
    for r in load(trace,('cycle','request_id','bank','operand','complete','retained_words')):
        if not 0<=r['cycle']<cycles: raise ValueError('outside horizon')
        by_cycle[r['cycle']].append(r)
    acquired=defaultdict(set); completed={}; peak=0
    for cycle in range(cycles):
        rows=by_cycle[cycle]; ports=defaultdict(int); retiring=set()
        samples={r['retained_words'] for r in rows}
        if len(samples)>1: raise ValueError('inconsistent storage samples')
        for r in rows:
            rid,bank,op,done=(r[k] for k in ('request_id','bank','operand','complete'))
            if rid==-1:
                if (bank,op,done)!=(-1,-1,0): raise ValueError('invalid idle row')
                continue
            if rid not in offered: raise ValueError('unoffered service')
            o=offered[rid]
            if cycle<o['arrival_cycle'] or rid in completed or op not in (0,1) or bank!=o['bank'+str(op)]:
                raise ValueError('early/retired/wrong-bank service')
            if op in acquired[rid] or done not in (0,1): raise ValueError('duplicate/invalid grant')
            acquired[rid].add(op); ports[bank]+=1
            if done:
                if rid in retiring: raise ValueError('duplicate completion')
                retiring.add(rid)
        if any(v>reads for v in ports.values()) or len(retiring)>returns:
            raise ValueError('physical ports exceeded')
        if any(acquired[rid]!={0,1} for rid in retiring):
            raise ValueError('premature completion')
        pre=sum(len(v) for rid,v in acquired.items() if rid not in completed)
        if registered and pre>words: raise ValueError('registered storage exceeded')
        for rid in retiring: completed[rid]=cycle
        live=sum(len(v) for rid,v in acquired.items() if rid not in completed)
        if live>words or (rows and samples!={live}): raise ValueError('storage mismatch')
        peak=max(peak,live)
    pending=set(offered)-set(completed)
    return {'offered':len(offered),'completed':len(completed),'pending':len(pending),
            'partially_served':sum(bool(acquired[r]) for r in pending),
            'completion_cycles':completed,'peak_retained_words':peak}

def compare(manifest,base,candidate,*,cycles,banks,reads,returns,words,
            base_period_ns,candidate_period_ns,registered=True,warmup=0):
    if not 0<=warmup<cycles or min(base_period_ns,candidate_period_ns)<=0:
        raise ValueError('invalid horizon or clock')
    args=dict(cycles=cycles,banks=banks,reads=reads,returns=returns,words=words,registered=registered)
    b=audit(manifest,base,**args); c=audit(manifest,candidate,**args)
    tb=sum(v>=warmup for v in b['completion_cycles'].values())/((cycles-warmup)*base_period_ns)
    tc=sum(v>=warmup for v in c['completion_cycles'].values())/((cycles-warmup)*candidate_period_ns)
    return {'baseline':b,'candidate':c,'ratio':tc/tb if tb else None,
            'policy':'same immutable manifest, fixed horizon, no drain beyond horizon'}

def selftest():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        m,b,c=[Path(d)/x for x in ('m.csv','b.csv','c.csv')]
        m.write_text('request_id,arrival_cycle,bank0,bank1\n0,0,0,1\n1,2,0,1\n')
        h='cycle,request_id,bank,operand,complete,retained_words\n'
        b.write_text(h+'0,0,0,0,0,1\n1,0,1,1,1,0\n2,1,0,0,0,1\n')
        c.write_text(h+'0,0,0,0,0,1\n1,0,1,1,1,0\n')
        kw=dict(cycles=4,banks=2,reads=1,returns=1,words=2,base_period_ns=3,candidate_period_ns=3)
        r=compare(m,b,c,**kw)
        assert r['ratio']==1 and r['baseline']['partially_served']==1 and r['candidate']['partially_served']==0
        for bad in (h+'0,2,0,0,0,1\n',h+'0,1,0,0,0,1\n',h+'0,0,1,0,0,1\n'):
            c.write_text(bad)
            try: compare(m,b,c,**kw)
            except ValueError: pass
            else: raise AssertionError('accepted invalid demand or bank')
        c.write_text(h+'0,0,0,0,0,1\n1,0,1,1,1,0\n2,1,0,0,0,1\n3,1,1,1,1,0\n')
        assert compare(m,b,c,**kw)['ratio']==2
        assert compare(m,b,b,**kw)['ratio']==1
    print('PASS: immutable arrivals, bank mapping, conservation, pending state, fixed horizon')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('manifest','baseline','candidate'): p.add_argument('--'+name)
    for name,default in (('cycles',1000),('banks',16),('reads',2),('returns',2),('words',4),('warmup',0)):
        p.add_argument('--'+name,type=int,default=default)
    p.add_argument('--base-period-ns',type=float,default=3)
    p.add_argument('--candidate-period-ns',type=float,default=3)
    p.add_argument('--bypass',action='store_true')
    a=p.parse_args(); selftest()
    if any((a.manifest,a.baseline,a.candidate)):
        if not all((a.manifest,a.baseline,a.candidate)): p.error('all three inputs required')
        print(json.dumps(compare(a.manifest,a.baseline,a.candidate,cycles=a.cycles,
            banks=a.banks,reads=a.reads,returns=a.returns,words=a.words,
            warmup=a.warmup,registered=not a.bypass,base_period_ns=a.base_period_ns,
            candidate_period_ns=a.candidate_period_ns),indent=2))
