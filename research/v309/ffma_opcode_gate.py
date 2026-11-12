#!/usr/bin/env python3
"""Opcode-aware authentic V100 SASS FFMA bank-demand screen; NOT GPU stalls."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib, io, json, tarfile
from pathlib import PurePosixPath
from v100_sass_profile import parse_row, EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name

FIELDS=('active','zero_mask','ffma_rows','ffma_three_distinct','ffma_three_same_bank',
        'ffma_more_than_three','ffma_p1_extra','ffma_p2_extra','nonffma_p2_extra',
        'all_p1_extra','all_p2_extra','source_occurrences','unique_source_reads',
        'r255_occurrences','unsupported','trace_files')

def fresh():
    return {k:0 for k in FIELDS}

def demand(src):
    unique=set(src)-{255}  # Assumed bypass, not verified silicon semantics.
    return sum(r%2==0 for r in unique),sum(r%2==1 for r in unique)

def extras(d,ports):
    if ports<1:raise ValueError('invalid ports')
    return max(0,(max(d)+ports-1)//ports-1)

def account(a,op,src,mask):
    if not mask:
        a['zero_mask']+=1
        return
    a['active']+=1
    a['source_occurrences']+=len(src)
    a['unique_source_reads']+=len(set(src)-{255})
    a['r255_occurrences']+=src.count(255)
    d=demand(src)
    p1,p2=extras(d,1),extras(d,2)
    a['all_p1_extra']+=p1
    a['all_p2_extra']+=p2
    if op.split('.',1)[0]=='FFMA':
        a['ffma_rows']+=1
        n=sum(d)
        a['ffma_three_distinct']+=(n==3)
        a['ffma_three_same_bank']+=(n==3 and max(d)==3)
        a['ffma_more_than_three']+=(n>3)
        a['ffma_p1_extra']+=p1
        a['ffma_p2_extra']+=p2
    else:
        a['nonffma_p2_extra']+=p2

def profile(path):
    with open(path,'rb') as f:blob=f.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE:raise ValueError('compressed archive over cap')
    sha=hashlib.sha256(blob).hexdigest()
    if sha!=EXPECTED_SHA:raise ValueError('archive SHA mismatch')
    apps=defaultdict(fresh)
    bases=defaultdict(fresh)
    examples=[]
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():raise ValueError('device member')
            if not member.isfile() or not member.name.endswith('.traceg'):continue
            if member.size>2*1024**3:raise ValueError('oversized member')
            parts=PurePosixPath(member.name).parts
            if len(parts)<5:raise ValueError('unexpected trace path')
            app=parts[2]
            apps[app]['trace_files']+=1
            f=tar.extractfile(member)
            if f is None:raise ValueError('unreadable member')
            for lineno,raw in enumerate(f,1):
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or not s[0].isdigit():continue
                try:mask,op,src,_width=parse_row(s)
                except ValueError as exc:
                    apps[app]['unsupported']+=1
                    if len(examples)<12:examples.append([app,member.name,lineno,str(exc)])
                    continue
                account(apps[app],op,src,mask)
                if mask:account(bases[op.split('.',1)[0]],op,src,mask)
    g=fresh()
    for a in apps.values():
        for k in FIELDS:g[k]+=a[k]
    if not g['active'] or g['unsupported']:raise ValueError('empty or unsupported active trace rows')
    if g['all_p2_extra']!=g['ffma_p2_extra']+g['nonffma_p2_extra']:
        raise AssertionError('P2 conservation failed')
    return {'evidence_tier':'authentic_V100_dynamic_SASS_conditional_opcode_bank_service_NOT_GPU_stalls',
            'archive_sha256':sha,
            'model':'mod2; two 32-bit reads per 64-bit bank idealization; free intra-instruction broadcast; assumed R255 bypass; no collectors or latency hiding',
            'global':g,'applications':dict(sorted(apps.items())),
            'opcode_bases':dict(sorted(bases.items())),'unsupported_examples':examples,
            'conditional_ffma_serial_throughput_gain_fraction':g['ffma_p2_extra']/g['active'],
            'conditional_all_opcode_serial_gain_fraction':g['all_p2_extra']/g['active'],
            'pre_registered_ffma_gate':'RETIRE' if g['ffma_p2_extra']<0.01*g['active'] else 'COUNTERS_REQUIRED_NO_HARDWARE_PROMOTION'}

def selftest():
    a=fresh()
    account(a,'FFMA.RN',(0,2,4),0xffffffff)
    assert a['ffma_rows']==1 and a['ffma_three_same_bank']==1 and a['ffma_p2_extra']==1 and a['ffma_p1_extra']==2
    account(a,'FFMA',(0,1,2),0xffffffff)
    assert a['ffma_p2_extra']==1
    account(a,'FFMA',(0,0,2,255),0xffffffff)
    assert a['ffma_p2_extra']==1 and a['unique_source_reads']==8 and a['r255_occurrences']==1
    account(a,'DFMA',(0,2,4),0xffffffff)
    assert a['nonffma_p2_extra']==1 and a['ffma_rows']==3
    account(a,'FFMA',(0,2,4),0)
    assert a['zero_mask']==1 and a['active']==4
    account(a,'FFMA',(0,2,4,6),0xffffffff)
    assert a['ffma_more_than_three']==1 and a['ffma_p2_extra']==2
    assert a['all_p2_extra']==a['ffma_p2_extra']+a['nonffma_p2_extra']
    return {'selftest':'PASS','fixture_active':5,'zero_mask':1,'ffma_p2_extra':2}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('archive',nargs='?')
    p.add_argument('--selftest',action='store_true')
    x=p.parse_args()
    if x.selftest:print(json.dumps(selftest()))
    if x.archive:print(json.dumps(profile(x.archive),sort_keys=True,indent=2))
    elif not x.selftest:p.error('archive required')
