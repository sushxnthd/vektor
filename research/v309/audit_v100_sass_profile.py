#!/usr/bin/env python3
"""Independent conservation and nested-bank-map audit for V309 trace descriptors."""
import argparse
import copy
import json

BASE=('rows','zero_mask','active','active_lanes','memory','source_occurrences',
      'unique_sources','duplicate_sources','r255_occurrences','multi_source','unsupported','files')
BANKS=(2,4,8)
COUNTS=BASE+tuple(f'collide_mod{b}_{suffix}' for b in BANKS for suffix in ('all','without_r255'))


def check(d):
    assert d['evidence_tier']=='authentic_V100_SASS_dynamic_instruction_demand_NOT_measured_stalls'
    assert len(d['archive_sha256'])==64
    apps=d['applications']; g=d['global']
    assert d['application_count']==len(apps)>=1
    assert d['trace_files']==sum(a['files'] for a in apps.values())
    for k in COUNTS:
        assert g[k]==sum(a[k] for a in apps.values()), ('sum',k)
    for name,a in [('GLOBAL',g),*apps.items()]:
        assert all(isinstance(a[k],int) and a[k]>=0 for k in COUNTS),name
        assert a['rows']==a['active']+a['zero_mask'],name
        assert a['source_occurrences']==a['unique_sources']+a['duplicate_sources'],name
        assert a['memory']<=a['active'] and a['multi_source']<=a['active'],name
        assert a['r255_occurrences']<=a['source_occurrences'],name
        assert a['active_lanes']<=32*a['active'] and a['active_lanes']>=a['active'],name
        for suffix in ('all','without_r255'):
            rates=[a[f'collide_mod{b}_{suffix}'] for b in BANKS]
            assert a['multi_source']>=rates[0]>=rates[1]>=rates[2]>=0,(name,suffix,rates)
        assert all(a[f'collide_mod{b}_without_r255']<=a[f'collide_mod{b}_all'] for b in BANKS),name
        if name!='GLOBAL':
            assert sum(v for _,v in a['top_opcodes'])<=a['active'],name
    assert g['active']>0
    assert len(d['unsupported_examples'])<=12
    return {'independent_audit':'PASS','application_count':len(apps),
            'active_rows':g['active'],'trace_files':d['trace_files']}


def selftest():
    a={k:0 for k in COUNTS}
    a.update({'rows':1,'active':1,'active_lanes':32,'source_occurrences':2,
              'unique_sources':2,'multi_source':1,'files':1,
              'collide_mod2_all':1,'collide_mod2_without_r255':1})
    d={'evidence_tier':'authentic_V100_SASS_dynamic_instruction_demand_NOT_measured_stalls',
       'archive_sha256':'a'*64,'application_count':1,'trace_files':1,'global':dict(a),
       'applications':{'fixture':{**a,'top_opcodes':[('ADD',1)]}},'unsupported_examples':[]}
    check(d)
    mutants=[]
    for field,value in [('duplicate_sources',1),('active',2),('collide_mod4_all',2),
                        ('r255_occurrences',3),('active_lanes',33),('trace_files',2)]:
        m=copy.deepcopy(d)
        if field=='trace_files':m[field]=value
        else:m['global'][field]=value
        mutants.append(m)
    for m in mutants:
        try:check(m)
        except AssertionError:pass
        else:raise AssertionError('mutant escaped')
    return {'selftest':'PASS','mutation_tests':len(mutants)}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('json_file',nargs='?')
    p.add_argument('--selftest',action='store_true')
    x=p.parse_args()
    if x.selftest:print(json.dumps(selftest()))
    if x.json_file:
        with open(x.json_file) as f:d=json.load(f)
        print(json.dumps(check(d),sort_keys=True))
    elif not x.selftest:p.error('JSON file required')
