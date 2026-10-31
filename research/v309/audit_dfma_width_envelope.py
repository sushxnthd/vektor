#!/usr/bin/env python3
"""Independent DFMA width/bank-map redecoder and adversarial audit.
Does not import the primary parser or accounting functions.
"""
from __future__ import annotations
import argparse, copy, hashlib, io, json, re, tarfile
from collections import defaultdict
from pathlib import PurePosixPath

SHA='aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1'
CAP=67108864
KEYS=('active','zero_mask','dfma','dfma_with_three_sources','dfma_odd_base',
      'dfma_r255','dfma_duplicate','dfma_paired_p1','dfma_paired_p2',
      'dfma_raw_p1','dfma_raw_p2','dfma_no_bypass_paired_p1',
      'dfma_pair_mapping_disagreement','dfma_raw_mapping_disagreement',
      'trace_files','unsupported')
REG=re.compile(r'R([0-9]+)\Z')

def fresh():return {k:0 for k in KEYS}

def decode(s):
    t=s.split()
    if len(t)<9 or any(int(v)<0 for v in t[:4]):raise ValueError('bad row')
    int(t[4],16);mask=int(t[5],16)
    if mask<0 or mask>0xffffffff:raise ValueError('mask')
    n=int(t[6]);i=7
    if n<0 or n>16 or len(t[i:i+n])!=n or any(not REG.fullmatch(v) for v in t[i:i+n]):raise ValueError('dest')
    i+=n;op=t[i];i+=1
    if not re.fullmatch('[A-Za-z][A-Za-z0-9_.]*',op):raise ValueError('opcode')
    n=int(t[i]);i+=1
    if n<0 or n>16 or len(t[i:i+n])!=n or any(not REG.fullmatch(v) for v in t[i:i+n]):raise ValueError('src')
    regs=[int(v[1:]) for v in t[i:i+n]];i+=n
    width=int(t[i]);i+=1
    if width<0 or (width==0 and i!=len(t)):raise ValueError('payload')
    return mask,op,regs

def extra(regs,port,by_pair,remove255=True):
    vals=set(regs)
    if remove255:vals.discard(255)
    c=[0,0]
    for r in vals:c[((r//2) if by_pair else r)&1]+=1
    return max(0,(max(c)-1)//port)

def add(a,mask,op,regs):
    if mask==0:a['zero_mask']+=1;return
    a['active']+=1
    if op.split('.')[0]!='DFMA':return
    a['dfma']+=1
    vals=set(regs)-{255}
    a['dfma_with_three_sources']+=len(vals)==3
    a['dfma_odd_base']+=any(r&1 for r in vals)
    a['dfma_r255']+=255 in regs
    a['dfma_duplicate']+=len(set(regs))!=len(regs)
    pp1=extra(regs,1,True);pp2=extra(regs,2,True)
    rp1=extra(regs,1,False);rp2=extra(regs,2,False)
    a['dfma_paired_p1']+=pp1;a['dfma_paired_p2']+=pp2
    a['dfma_raw_p1']+=rp1;a['dfma_raw_p2']+=rp2
    a['dfma_no_bypass_paired_p1']+=extra(regs,1,True,False)
    a['dfma_pair_mapping_disagreement']+=pp1!=rp1
    a['dfma_raw_mapping_disagreement']+=pp2!=rp2

def recompute(path):
    with open(path,'rb') as f:blob=f.read(CAP+1)
    if len(blob)>CAP or hashlib.sha256(blob).hexdigest()!=SHA:raise ValueError('digest')
    apps=defaultdict(fresh)
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for m in tar:
            if m.name.startswith('/') or '..' in m.name.split('/') or m.isdev():raise ValueError('unsafe member')
            if not m.isfile() or not m.name.endswith('.traceg'):continue
            if m.size>2*1024**3:raise ValueError('member size')
            parts=PurePosixPath(m.name).parts
            if len(parts)<5:raise ValueError('path')
            a=apps[parts[2]];a['trace_files']+=1
            f=tar.extractfile(m)
            if f is None:raise ValueError('unreadable')
            for raw in f:
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or not s[0].isdigit():continue
                try:add(a,*decode(s))
                except (ValueError,IndexError):a['unsupported']+=1
    g=fresh()
    for a in apps.values():
        for k in KEYS:g[k]+=a[k]
    return {'global':g,'applications':dict(sorted(apps.items()))}

def audit(report,expected,expected_active=3937565):
    for field in ('global','applications'):
        if report.get(field)!=expected[field]:raise ValueError('independent mismatch: '+field)
    g=expected['global']
    if g['active']!=expected_active or g['unsupported'] or not g['dfma']:raise ValueError('coverage')
    frac=g['dfma_paired_p1']/g['active']
    if report.get('conditional_paired_p1_extra_per_instruction')!=frac:raise ValueError('fraction')
    if report.get('gate')!=('COUNTERS_AND_PHYSICAL_MODEL_REQUIRED' if frac>=0.01 else 'RETIRE_DFMA_ONLY'):
        raise ValueError('gate')
    if report.get('archive_sha256')!=SHA:raise ValueError('sha')
    if report.get('prospective_holdout_status')!='NONE: all Rodinia families previously examined':raise ValueError('holdout')
    return {'audit':'PASS','active':g['active'],'dfma':g['dfma'],
            'paired_p1':g['dfma_paired_p1'],'raw_p1':g['dfma_raw_p1'],
            'paired_p2':g['dfma_paired_p2'],'raw_p2':g['dfma_raw_p2'],
            'odd_base':g['dfma_odd_base'],'conditional_fraction':frac}

def selftest():
    a=fresh()
    for s in ('0 0 0 0 0001 ffffffff 0 DFMA 3 R0 R2 R4 0',
              '0 0 0 0 0001 ffffffff 0 DFMA 3 R0 R0 R255 0',
              '0 0 0 0 0001 ffffffff 0 FFMA 3 R0 R2 R4 0',
              '0 0 0 0 0001 00000000 0 DFMA 3 R0 R2 R4 0'):
        add(a,*decode(s))
    assert a['active']==3 and a['dfma']==2 and a['zero_mask']==1
    assert a['dfma_paired_p1']==1 and a['dfma_raw_p1']==2
    assert a['dfma_r255']==1 and a['dfma_duplicate']==1
    expected={'global':a,'applications':{'fixture':a}}
    report={**copy.deepcopy(expected),'archive_sha256':SHA,
            'conditional_paired_p1_extra_per_instruction':a['dfma_paired_p1']/a['active'],
            'gate':'COUNTERS_AND_PHYSICAL_MODEL_REQUIRED',
            'prospective_holdout_status':'NONE: all Rodinia families previously examined'}
    audit(report,expected,expected_active=3)
    mutants=[]
    for key in KEYS:
        m=copy.deepcopy(report);m['global'][key]+=1;mutants.append(m)
    m=copy.deepcopy(report);m['applications']['fixture']['dfma_paired_p1']+=1;mutants.append(m)
    for key,value in [('archive_sha256','bad'),('gate','RETIRE_DFMA_ONLY'),
                      ('conditional_paired_p1_extra_per_instruction',0),
                      ('prospective_holdout_status','CLAIMED_UNSEEN')]:
        m=copy.deepcopy(report);m[key]=value;mutants.append(m)
    for m in mutants:
        try:audit(m,expected,expected_active=3)
        except ValueError:pass
        else:raise AssertionError('mutant accepted')
    return {'selftest':'PASS','mutants_rejected':len(mutants),'fixture_dfma':2}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',nargs='?');p.add_argument('report',nargs='?');p.add_argument('--selftest',action='store_true')
    x=p.parse_args()
    if x.selftest:print(json.dumps(selftest(),sort_keys=True))
    if x.archive and x.report:
        with open(x.report) as f:report=json.load(f)
        print(json.dumps(audit(report,recompute(x.archive)),indent=2,sort_keys=True))
    elif not x.selftest:p.error('archive and report required')
