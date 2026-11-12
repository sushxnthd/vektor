#!/usr/bin/env python3
"""Fail-closed matched-resource physicality gate for Vektor.

Input: JSON with baseline/candidate measurements, each containing:
  area_um2, delay_ns, dynamic_power_mw, leakage_power_mw,
  useful_ops, cycles, clock_ns, traffic_bytes, wire_load_scale,
  electrical_violations, provenance (nonempty artifact hash).
Measurements must be from the same library, corner, constraints, and workload.
This is an evidence validator, not a replacement for RTL/STA.
"""
import argparse
import json
import math

FIELDS = ('area_um2','delay_ns','dynamic_power_mw','leakage_power_mw',
          'useful_ops','cycles','clock_ns','traffic_bytes','wire_load_scale')
MATCH = ('library','corner','constraints_sha256','workload_sha256','resource_budget_sha256')

def evaluate(doc):
    errors=[]
    a,b=doc.get('baseline',{}),doc.get('candidate',{})
    for label,x in [('baseline',a),('candidate',b)]:
        for key in FIELDS:
            v=x.get(key)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0:
                errors.append(f'{label}.{key}: missing/nonpositive/nonfinite')
        if not isinstance(x.get('electrical_violations'),int) or x.get('electrical_violations')<0:
            errors.append(f'{label}.electrical_violations: missing/invalid')
        if not isinstance(x.get('provenance'),str) or len(x['provenance'])<16:
            errors.append(f'{label}.provenance: missing/short')
    for k in MATCH:
        if not a.get(k) or a.get(k)!=b.get(k):
            errors.append(f'{k}: not matched')
    if errors: return {'pass':False,'errors':errors}
    if a['electrical_violations'] or b['electrical_violations']:
        errors.append('electrical violations')
    if b['delay_ns']>b['clock_ns'] or a['delay_ns']>a['clock_ns']:
        errors.append('timing not closed at declared clock')
    if b['area_um2']>a['area_um2']:
        errors.append('candidate exceeds matched baseline area')
    if b['wire_load_scale']<a['wire_load_scale']:
        errors.append('candidate uses more favorable wire/load assumption')
    ta=a['useful_ops']/(a['cycles']*a['clock_ns'])
    tb=b['useful_ops']/(b['cycles']*b['clock_ns'])
    gain=tb/ta-1
    if gain<=0: errors.append('no positive useful-throughput gain')
    if b['traffic_bytes']/b['useful_ops']>a['traffic_bytes']/a['useful_ops']:
        errors.append('candidate traffic per useful operation increased; bandwidth re-evaluation required')
    return {'pass':not errors,'gain':gain,'errors':errors,
            'note':'Power numbers are proxies; independent PPA and workload evidence still required.'}

def selftest():
    shared=dict(library='testlib',corner='testcorner',constraints_sha256='c'*64,
                workload_sha256='w'*64,resource_budget_sha256='r'*64,
                area_um2=100,delay_ns=0.8,dynamic_power_mw=10,leakage_power_mw=1,
                useful_ops=100,cycles=100,clock_ns=1,traffic_bytes=1000,
                wire_load_scale=1,electrical_violations=0,provenance='a'*64)
    candidate=dict(shared,cycles=90,provenance='b'*64)
    assert evaluate(dict(baseline=shared,candidate=candidate))['pass']
    for change in [dict(area_um2=101),dict(delay_ns=1.1),dict(electrical_violations=1),
                   dict(cycles=110),dict(wire_load_scale=.9),dict(traffic_bytes=1100),
                   dict(library='other'),dict(provenance='')]:
        assert not evaluate(dict(baseline=shared,candidate=dict(candidate,**change)))['pass'],change
    assert not evaluate(dict(baseline={},candidate={}))['pass']
    print('PASS: positive fixture, 8 negative controls, missing-data control')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('json',nargs='?')
    p.add_argument('--selftest',action='store_true')
    args=p.parse_args()
    if args.selftest: selftest()
    else:
        if not args.json: p.error('provide measurement JSON or --selftest')
        with open(args.json) as f: result=evaluate(json.load(f))
        print(json.dumps(result,indent=2))
        raise SystemExit(0 if result['pass'] else 1)
