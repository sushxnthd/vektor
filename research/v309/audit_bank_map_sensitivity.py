#!/usr/bin/env python3
"""Independent V309 bank-map sensitivity conservation and mutation checker."""
import argparse,copy,json
from itertools import combinations

MAPS=('mod2','xor2','mod4','xor4','mod8','xor8')
METRICS=('isolated_extra_cycles_p1','isolated_extra_cycles_p2','rows_extra_p1','rows_extra_p2')
SHA='aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1'

def check(d):
    assert d['archive_sha256']==SHA,'archive SHA'
    assert d['evidence_tier']=='authenticated_V100_trace_hypothetical_bank_mapping_only'
    assert tuple(d['bank_maps'])==MAPS
    apps=d['applications'];g=d['global']
    assert len(apps)==11,'application count'
    assert g['active']==3937565,'active rows'
    assert g['unsupported']*100<=max(1,g['active']+g['unsupported'])
    for k in ('active','multisource','unique_reads_bypass','unique_reads_all','zero_mask','unsupported'):
        assert g[k]==sum(a[k] for a in apps.values()),'global conservation '+k
    assert 0<=g['multisource']<=g['active']
    assert 0<=g['unique_reads_bypass']<=g['unique_reads_all']
    for app,a in apps.items():
        assert a['active']>0
        assert 0<=a['multisource']<=a['active']
        assert 0<=a['unique_reads_bypass']<=a['unique_reads_all']
        for k in MAPS:
            x=a['map'][k];y=g['map'][k]
            for metric in METRICS:
                assert x[metric]>=0
                assert y[metric]==sum(v['map'][k][metric] for v in apps.values()),'metric conservation'
            assert x['isolated_extra_cycles_p2']<=x['isolated_extra_cycles_p1'],'port monotonicity'
            assert x['rows_extra_p2']<=x['rows_extra_p1'],'row port monotonicity'
            assert x['rows_extra_p1']<=a['active'] and x['rows_extra_p2']<=a['active']
            assert 0<=x['max_service_p1']<=16
        for p in (1,2):
            for b1,b2 in ((2,4),(4,8)):
                metric=f'isolated_extra_cycles_p{p}'
                assert a['map'][f'mod{b1}'][metric]>=a['map'][f'mod{b2}'][metric],'mod bank monotonicity'
    inversions={}
    for b in (2,4,8):
        pairs=0;inv=0;ties=0
        for a1,a2 in combinations(apps.values(),2):
            # Integer cross-products avoid floating-point ranking ambiguity.
            m=a1['map'][f'mod{b}']['isolated_extra_cycles_p1']*a2['active']-a2['map'][f'mod{b}']['isolated_extra_cycles_p1']*a1['active']
            x=a1['map'][f'xor{b}']['isolated_extra_cycles_p1']*a2['active']-a2['map'][f'xor{b}']['isolated_extra_cycles_p1']*a1['active']
            pairs+=1
            if m==0 or x==0:ties+=1
            elif (m>0)!=(x>0):inv+=1
        inversions[str(b)]={'inversions':inv,'pairs':pairs,'ties':ties}
    return {'independent_audit':'PASS','active_rows':g['active'],'applications':len(apps),
            'pairwise_mapping_rank_inversions':inversions,
            'decision':'mapping_independence_REJECTED' if any(v['inversions'] for v in inversions.values()) else 'mapping_independence_NOT_FALSIFIED_by_two_maps',
            'limitation':'model-only; no measured GPU RF stalls or architecture win'}

def selftest():
    apps={f'a{i}':{'active':1,'multisource':0,'unique_reads_bypass':0,'unique_reads_all':0,
                   'zero_mask':0,'unsupported':0,
                   'map':{k:{'isolated_extra_cycles_p1':0,'isolated_extra_cycles_p2':0,
                   'rows_extra_p1':0,'rows_extra_p2':0,'max_service_p1':0} for k in MAPS}} for i in range(11)}
    g={'active':3937565,'multisource':0,'unique_reads_bypass':0,'unique_reads_all':0,
       'zero_mask':0,'unsupported':0,
       'map':{k:{'isolated_extra_cycles_p1':0,'isolated_extra_cycles_p2':0,
       'rows_extra_p1':0,'rows_extra_p2':0,'max_service_p1':0} for k in MAPS}}
    d={'archive_sha256':SHA,'evidence_tier':'authenticated_V100_trace_hypothetical_bank_mapping_only',
       'bank_maps':list(MAPS),'applications':apps,'global':g}
    muts=[]
    x=copy.deepcopy(d);x['archive_sha256']='0'*64;muts.append(x)
    x=copy.deepcopy(d);x['global']['active']=0;muts.append(x)
    x=copy.deepcopy(d);x['bank_maps'].pop();muts.append(x)
    x=copy.deepcopy(d);x['applications']['a0']['map']['mod2']['isolated_extra_cycles_p2']=2;muts.append(x)
    x=copy.deepcopy(d);x['applications']['a0']['active']=-1;muts.append(x)
    x=copy.deepcopy(d);x['global']['unique_reads_all']=99;muts.append(x)
    for i,x in enumerate(muts):
        try:check(x)
        except AssertionError:continue
        raise AssertionError(f'corruption mutation {i} accepted')
    return {'selftest':'PASS','rejected_corrupt_reports':len(muts)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('report',nargs='?');p.add_argument('--selftest',action='store_true');a=p.parse_args()
    if a.selftest:print(json.dumps(selftest()))
    if a.report:print(json.dumps(check(json.load(open(a.report))),indent=2,sort_keys=True))
    elif not a.selftest:p.error('report required')
