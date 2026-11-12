#!/usr/bin/env python3
"""Independent V309 full-archive SASS redecoder and FFMA-gate checker.

Does NOT import the primary parser or its accounting functions.
"""
from __future__ import annotations
import argparse,copy,hashlib,io,json,re,tarfile
from collections import defaultdict
from pathlib import PurePosixPath

SHA='aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1'
CAP=67108864
REG=re.compile(r'^R([0-9]+)$')
FIELDS=('active','zero_mask','ffma_rows','ffma_three_distinct','ffma_three_same_bank',
        'ffma_more_than_three','ffma_p1_extra','ffma_p2_extra','nonffma_p2_extra',
        'all_p1_extra','all_p2_extra','source_occurrences','unique_source_reads',
        'r255_occurrences','unsupported','trace_files')

def parse_independent(line):
    t=line.split()
    if len(t)<9:raise ValueError('short row')
    if any(int(v)<0 for v in t[:4]):raise ValueError('negative CTA/warp')
    int(t[4],16)
    mask=int(t[5],16)
    if not 0<=mask<=0xffffffff:raise ValueError('mask')
    n=int(t[6]);i=7
    if not 0<=n<=16:raise ValueError('ndst')
    if len(t[i:i+n])!=n or any(not REG.fullmatch(x) for x in t[i:i+n]):raise ValueError('dest')
    i+=n
    op=t[i];i+=1
    if not re.fullmatch('[A-Za-z][A-Za-z0-9_.]*',op):raise ValueError('opcode')
    n=int(t[i]);i+=1
    if not 0<=n<=16:raise ValueError('nsrc')
    src=t[i:i+n];i+=n
    if len(src)!=n or any(not REG.fullmatch(x) for x in src):raise ValueError('src')
    width=int(t[i]);i+=1
    if width<0 or (width==0 and i!=len(t)):raise ValueError('width/payload')
    return mask,op,[int(x[1:]) for x in src]

def fresh():
    return {k:0 for k in FIELDS}

def add(a,op,src,mask):
    if not mask:
        a['zero_mask']+=1
        return
    a['active']+=1
    a['source_occurrences']+=len(src)
    a['r255_occurrences']+=sum(r==255 for r in src)
    unique={r for r in src if r!=255}
    a['unique_source_reads']+=len(unique)
    even=sum(r%2==0 for r in unique)
    maximum=max(even,len(unique)-even)
    p1=max(0,maximum-1)
    p2=max(0,(maximum-1)//2)
    a['all_p1_extra']+=p1
    a['all_p2_extra']+=p2
    if op.split('.')[0]=='FFMA':
        a['ffma_rows']+=1
        a['ffma_three_distinct']+=len(unique)==3
        a['ffma_three_same_bank']+=(len(unique)==3 and maximum==3)
        a['ffma_more_than_three']+=len(unique)>3
        a['ffma_p1_extra']+=p1
        a['ffma_p2_extra']+=p2
    else:
        a['nonffma_p2_extra']+=p2

def recompute(path):
    with open(path,'rb') as f:blob=f.read(CAP+1)
    if len(blob)>CAP or hashlib.sha256(blob).hexdigest()!=SHA:raise ValueError('archive integrity')
    apps=defaultdict(fresh);bases=defaultdict(fresh)
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for m in tar:
            if m.name.startswith('/') or '..' in m.name.split('/') or m.isdev():raise ValueError('unsafe member')
            if not m.isfile() or not m.name.endswith('.traceg'):continue
            if m.size>2*1024**3:raise ValueError('oversized member')
            parts=PurePosixPath(m.name).parts
            if len(parts)<5:raise ValueError('bad trace path')
            app=parts[2];apps[app]['trace_files']+=1
            f=tar.extractfile(m)
            if f is None:raise ValueError('unreadable member')
            for raw in f:
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or not s[0].isdigit():continue
                try:mask,op,src=parse_independent(s)
                except (ValueError,IndexError):apps[app]['unsupported']+=1;continue
                add(apps[app],op,src,mask)
                if mask:add(bases[op.split('.')[0]],op,src,mask)
    g=fresh()
    for row in apps.values():
        for k in FIELDS:g[k]+=row[k]
    return {'global':g,'applications':dict(sorted(apps.items())),'opcode_bases':dict(sorted(bases.items()))}

def audit(report,expected):
    for k in ('global','applications','opcode_bases'):
        if report.get(k)!=expected[k]:
            if isinstance(report.get(k),dict) and isinstance(expected[k],dict):
                keys=sorted(set(report[k])|set(expected[k]))
                for item in keys:
                    left=report[k].get(item);right=expected[k].get(item)
                    if left!=right:
                        if isinstance(left,dict) and isinstance(right,dict):
                            for metric in sorted(set(left)|set(right)):
                                if left.get(metric)!=right.get(metric):
                                    raise ValueError('independent '+k+' mismatch '+str(item)+'/'+str(metric)+': primary='+str(left.get(metric))+' audit='+str(right.get(metric)))
                        raise ValueError('independent '+k+' mismatch '+str(item)+': primary='+str(left)+' audit='+str(right))
            raise ValueError('independent '+k+' mismatch')
    g=expected['global']
    if not g['active'] or g['unsupported']:raise ValueError('unsupported rows')
    if g['all_p2_extra']!=g['ffma_p2_extra']+g['nonffma_p2_extra']:raise ValueError('P2 conservation')
    f=g['ffma_p2_extra']/g['active'];a=g['all_p2_extra']/g['active']
    if report.get('conditional_ffma_serial_throughput_gain_fraction')!=f:raise ValueError('FFMA ratio')
    if report.get('conditional_all_opcode_serial_gain_fraction')!=a:raise ValueError('all-opcode ratio')
    gate='RETIRE' if f<0.01 else 'COUNTERS_REQUIRED_NO_HARDWARE_PROMOTION'
    if report.get('pre_registered_ffma_gate')!=gate:raise ValueError('gate')
    if report.get('archive_sha256')!=SHA:raise ValueError('digest')
    return {'independent_audit':'PASS','active':g['active'],'ffma_rows':g['ffma_rows'],
            'ffma_p2_extra':g['ffma_p2_extra'],'all_p2_extra':g['all_p2_extra'],
            'ffma_fraction':f,'pre_registered_gate':gate}

def selftest():
    samples=['0 0 0 0 0001 ffffffff 0 FFMA.RN 3 R0 R2 R4 0',
             '0 0 0 0 0001 ffffffff 0 FFMA 3 R0 R1 R2 0',
             '0 0 0 0 0001 ffffffff 0 DFMA 3 R0 R2 R4 0',
             '0 0 0 0 0001 00000000 0 FFMA 3 R0 R2 R4 0']
    a=fresh();bases=defaultdict(fresh)
    for s in samples:
        mask,op,src=parse_independent(s)
        add(a,op,src,mask)
        if mask:add(bases[op.split('.')[0]],op,src,mask)
    assert a['active']==3 and a['zero_mask']==1 and a['ffma_p2_extra']==1 and a['nonffma_p2_extra']==1
    expected={'global':a,'applications':{'fixture':a},'opcode_bases':dict(bases)}
    report={'global':copy.deepcopy(a),'applications':{'fixture':copy.deepcopy(a)},
            'opcode_bases':copy.deepcopy(dict(bases)),
            'conditional_ffma_serial_throughput_gain_fraction':1/3,
            'conditional_all_opcode_serial_gain_fraction':2/3,
            'pre_registered_ffma_gate':'COUNTERS_REQUIRED_NO_HARDWARE_PROMOTION','archive_sha256':SHA}
    audit(report,expected)
    mutants=[]
    for k in ('active','ffma_rows','ffma_p2_extra','nonffma_p2_extra','all_p2_extra'):
        x=copy.deepcopy(report);x['global'][k]+=1;mutants.append(x)
    x=copy.deepcopy(report);x['applications']['fixture']['ffma_rows']+=1;mutants.append(x)
    x=copy.deepcopy(report);x['opcode_bases']['FFMA']['ffma_p2_extra']+=1;mutants.append(x)
    x=copy.deepcopy(report);x['pre_registered_ffma_gate']='RETIRE';mutants.append(x)
    for x in mutants:
        try:audit(x,expected)
        except ValueError:pass
        else:raise AssertionError('mutant accepted')
    return {'selftest':'PASS','mutants_rejected':len(mutants),'fixture_active':3}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('archive',nargs='?')
    p.add_argument('report',nargs='?')
    p.add_argument('--selftest',action='store_true')
    x=p.parse_args()
    if x.selftest:print(json.dumps(selftest()))
    if x.archive and x.report:
        with open(x.report) as f:r=json.load(f)
        print(json.dumps(audit(r,recompute(x.archive)),indent=2,sort_keys=True))
    elif not x.selftest:p.error('archive and report required')
