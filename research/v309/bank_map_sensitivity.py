#!/usr/bin/env python3
"""V309 authenticated V100 SASS bank-map sensitivity; NOT measured RF stalls."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib,io,json,tarfile
from pathlib import PurePosixPath
from v100_sass_profile import parse_row,EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE,validate_name

MAPS=('mod2','xor2','mod4','xor4','mod8','xor8')

def bank(reg,name):
    b=int(name[-1])
    if name.startswith('mod'):return reg%b
    if name.startswith('xor'):return (reg^(reg>>(b.bit_length()-1)))%b
    raise ValueError('unsupported bank map')

def service(src,name,ports=1,bypass_r255=True):
    """Exact minimum bank-read cycles for an isolated instruction in this model."""
    if ports<=0:raise ValueError('invalid port count')
    unique=set(src)
    if bypass_r255:unique.discard(255)
    if not unique:return 0
    c=Counter(bank(r,name) for r in unique)
    return (max(c.values())+ports-1)//ports

def fresh():
    return {'active':0,'multisource':0,'unique_reads_bypass':0,'unique_reads_all':0,
            'zero_mask':0,'unsupported':0,'map':{
            k:{'isolated_extra_cycles_p1':0,'isolated_extra_cycles_p2':0,
               'rows_extra_p1':0,'rows_extra_p2':0,'max_service_p1':0}
            for k in MAPS}}

def account(a,src):
    a['active']+=1
    unique=set(src)
    a['multisource']+=(len(unique)>=2)
    a['unique_reads_all']+=len(unique)
    a['unique_reads_bypass']+=len(unique-{255})
    for k in MAPS:
        s1=service(src,k,1);s2=service(src,k,2)
        x=a['map'][k]
        e1=max(0,s1-1);e2=max(0,s2-1)
        x['isolated_extra_cycles_p1']+=e1
        x['isolated_extra_cycles_p2']+=e2
        x['rows_extra_p1']+=(e1>0)
        x['rows_extra_p2']+=(e2>0)
        x['max_service_p1']=max(x['max_service_p1'],s1)

def profile(path):
    with open(path,'rb') as f:blob=f.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE:raise ValueError('archive exceeds byte cap')
    sha=hashlib.sha256(blob).hexdigest()
    if sha!=EXPECTED_SHA:raise ValueError('archive SHA mismatch')
    apps=defaultdict(fresh)
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for m in tar:
            validate_name(m.name)
            if m.isdev():raise ValueError('device member')
            if not m.isfile() or not m.name.endswith('.traceg'):continue
            if m.size>2*1024**3:raise ValueError('oversized member')
            parts=PurePosixPath(m.name).parts
            if len(parts)<5:raise ValueError('unexpected trace path')
            a=apps[parts[2]]
            f=tar.extractfile(m)
            if f is None:raise ValueError('unreadable trace')
            for raw in f:
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or not s[0].isdigit():continue
                try:mask,opcode,src,width=parse_row(s)
                except ValueError:
                    a['unsupported']+=1;continue
                if not mask:a['zero_mask']+=1;continue
                account(a,src)
    g=fresh()
    for a in apps.values():
        for k in ('active','multisource','unique_reads_bypass','unique_reads_all','zero_mask','unsupported'):
            g[k]+=a[k]
        for k in MAPS:
            for metric in a['map'][k]:
                if metric=='max_service_p1':g['map'][k][metric]=max(g['map'][k][metric],a['map'][k][metric])
                else:g['map'][k][metric]+=a['map'][k][metric]
    if not g['active']:raise ValueError('empty active corpus')
    if g['unsupported']*100>max(1,g['active']+g['unsupported']):
        raise ValueError('more than 1% unsupported rows')
    return {'evidence_tier':'authenticated_V100_trace_hypothetical_bank_mapping_only',
            'archive_sha256':sha,'bank_maps':list(MAPS),
            'model':'isolated bank read-service; unique-source free broadcast; assumed R255 bypass; no collectors, overlap or memory latency',
            'applications':dict(sorted(apps.items())),'global':g}

def selftest():
    assert bank(2,'mod2')==0 and bank(2,'xor2')==1
    assert bank(4,'mod4')==0 and bank(4,'xor4')==1
    assert service((0,2),'mod2')==2 and service((0,2),'xor2')==1
    assert service((0,2),'mod2',ports=2)==1
    assert service((0,0,2),'mod2')==2
    assert service((255,255),'mod2')==0
    assert service((255,255),'mod2',bypass_r255=False)==1
    assert service((0,2,4),'mod2')==3 and service((0,2,4),'mod2',ports=2)==2
    a=fresh()
    for src in ((0,2),(0,0,2),(255,)):account(a,src)
    assert a['active']==3 and a['map']['mod2']['isolated_extra_cycles_p1']==2
    assert a['map']['xor2']['isolated_extra_cycles_p1']==0
    for k in MAPS:
        assert a['map'][k]['isolated_extra_cycles_p2']<=a['map'][k]['isolated_extra_cycles_p1']
    return {'selftest':'PASS','fixture_rows':3,'maps':len(MAPS)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',nargs='?');p.add_argument('--selftest',action='store_true');x=p.parse_args()
    if x.selftest:print(json.dumps(selftest()))
    if x.archive:print(json.dumps(profile(x.archive),indent=2,sort_keys=True))
    elif not x.selftest:p.error('archive required')
