#!/usr/bin/env python3
"""V309: DFMA source-pair mapping sensitivity on SHA-pinned V100 SASS.
Conditional register-service envelopes only; never interpret as hardware stalls.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib, io, json, tarfile
from pathlib import PurePosixPath
from v100_sass_profile import parse_row, EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name

KEYS = ('active','zero_mask','dfma','dfma_with_three_sources','dfma_odd_base',
        'dfma_r255','dfma_duplicate','dfma_paired_p1','dfma_paired_p2',
        'dfma_raw_p1','dfma_raw_p2','dfma_no_bypass_paired_p1',
        'dfma_pair_mapping_disagreement','dfma_raw_mapping_disagreement',
        'trace_files','unsupported')

def fresh():
    return {k:0 for k in KEYS}

def service(src, mapping, ports, bypass=True):
    if ports < 1: raise ValueError('ports must be positive')
    if mapping not in ('pair','raw'): raise ValueError('unknown mapping')
    unique = set(src)
    if bypass: unique.discard(255)
    banks = [0,0]
    for reg in unique:
        bank = (reg//2 if mapping == 'pair' else reg) % 2
        banks[bank] += 1
    return max(0, (max(banks)+ports-1)//ports-1)

def account(a, opcode, src, mask):
    if not mask:
        a['zero_mask'] += 1
        return
    a['active'] += 1
    if opcode.split('.',1)[0] != 'DFMA': return
    a['dfma'] += 1
    unique = set(src)-{255}
    a['dfma_with_three_sources'] += (len(unique)==3)
    a['dfma_odd_base'] += any(r%2 for r in unique)
    a['dfma_r255'] += 255 in src
    a['dfma_duplicate'] += len(src) != len(set(src))
    for m in ('pair','raw'):
        for p in (1,2):
            a[f'dfma_{"paired" if m=="pair" else "raw"}_p{p}'] += service(src,m,p)
    a['dfma_no_bypass_paired_p1'] += service(src,'pair',1,bypass=False)
    a['dfma_pair_mapping_disagreement'] += service(src,'pair',1) != service(src,'raw',1)
    a['dfma_raw_mapping_disagreement'] += service(src,'pair',2) != service(src,'raw',2)

def profile(path):
    with open(path,'rb') as f: blob=f.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE or hashlib.sha256(blob).hexdigest()!=EXPECTED_SHA:
        raise ValueError('archive cap or frozen SHA mismatch')
    apps=defaultdict(fresh)
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for m in tar:
            validate_name(m.name)
            if m.isdev(): raise ValueError('device entry')
            if not m.isfile() or not m.name.endswith('.traceg'): continue
            if m.size>2*1024**3: raise ValueError('oversized member')
            parts=PurePosixPath(m.name).parts
            if len(parts)<5: raise ValueError('unrecognized trace path')
            a=apps[parts[2]]; a['trace_files']+=1
            f=tar.extractfile(m)
            if f is None: raise ValueError('unreadable member')
            for raw in f:
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or not s[0].isdigit(): continue
                try:mask,opcode,src,_=parse_row(s)
                except ValueError: a['unsupported']+=1; continue
                account(a,opcode,src,mask)
    g=fresh()
    for a in apps.values():
        for k in KEYS:g[k]+=a[k]
    if g['active']!=3937565 or g['unsupported'] or g['dfma']==0:
        raise ValueError('unexpected active count, unsupported rows, or absent DFMA')
    fraction=g['dfma_paired_p1']/g['active']
    return {
        'evidence_tier':'V100_authentic_SASS_conditional_DFMA_width_mapping_sensitivity_NOT_stalls',
        'archive_sha256':EXPECTED_SHA,
        'assumptions':['DFMA sources represented by 64-bit register pairs, not verified',
                       'pair mapping=(R//2)%2; alternative raw mapping=R%2',
                       'free within-instruction source broadcast','R255 bypass assumed and sensitivity counted',
                       '1 or 2 hypothetical 64-bit operand reads per bank per cycle',
                       'no measured counters, collector arbitration, latency hiding or timing'],
        'global':g,'applications':dict(sorted(apps.items())),
        'conditional_paired_p1_extra_per_instruction':fraction,
        'gate':'COUNTERS_AND_PHYSICAL_MODEL_REQUIRED' if fraction>=0.01 else 'RETIRE_DFMA_ONLY',
        'prospective_holdout_status':'NONE: all Rodinia families previously examined'
    }

def selftest():
    a=fresh()
    account(a,'DFMA.RN',(0,2,4),0xffffffff)
    assert a['dfma_paired_p1']==1 and a['dfma_raw_p1']==2
    assert a['dfma_paired_p2']==0 and a['dfma_raw_p2']==1
    account(a,'DFMA',(0,0,2,255),0xffffffff)
    assert a['dfma_duplicate']==1 and a['dfma_r255']==1
    assert a['dfma_no_bypass_paired_p1']>=a['dfma_paired_p1']
    account(a,'FFMA',(0,2,4),0xffffffff)
    account(a,'DFMA',(0,2,4),0)
    assert a['active']==3 and a['zero_mask']==1 and a['dfma']==2
    for mapping in ('pair','raw'):
        for p in (1,2,3):
            for n in range(5):
                regs=tuple(2*i for i in range(n))
                assert service(regs,mapping,p)>=0
                assert service(regs,mapping,p)>=service(regs,mapping,p+1)
    for invalid in ('bad','',None):
        try:service((0,2),invalid,1)
        except ValueError:pass
        else:raise AssertionError('invalid mapping accepted')
    return {'selftest':'PASS','active_fixture':3,'zero_mask':1,'dfma_fixture':2}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',nargs='?');p.add_argument('--selftest',action='store_true')
    args=p.parse_args()
    if args.selftest:print(json.dumps(selftest(),sort_keys=True))
    if args.archive:print(json.dumps(profile(args.archive),indent=2,sort_keys=True))
    elif not args.selftest:p.error('archive required')
