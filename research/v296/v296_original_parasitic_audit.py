#!/usr/bin/env python3
"""Fail-closed paired SPEF load-tail audit of original V296 GitHub artifacts.
Requires only Python stdlib and the exact original ZIPs. No STA/power claims.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

HASHES = {
    'pairwise': '9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259',
    'serial_onehot': '5c0f7ef91a2151ac2069553cd93a34b97d38c939d6f1106ea95ef4cc8b85706e',
}

def percentile(v, q):
    v = sorted(v)
    if not v: raise ValueError('No nets')
    x = (len(v)-1)*q
    i = int(x)
    return v[i] + (v[min(i+1,len(v)-1)]-v[i])*(x-i)

def read(path, variant):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != HASHES[variant]:
        raise ValueError('Original ZIP SHA mismatch')
    with zipfile.ZipFile(path) as z:
        spef = z.read(variant+'.high.cts45.spef').decode()
        log = z.read(variant+'.high.log').decode()
        manifest = json.loads(z.read('in_situ_manifest.json'))
    if '*C_UNIT 1 PF' not in spef or '*R_UNIT 1 OHM' not in spef:
        raise ValueError('Unexpected SPEF units')
    caps = [float(x) for x in re.findall(r'^\*D_NET\s+\S+\s+([\d.eE+-]+)$',spef,re.M)]
    if len(caps)<1000: raise ValueError('Incomplete SPEF')
    def marked(stage):
        m = re.findall(r'^V296_IN_SITU_'+stage+r'_SLACK_BEGIN\nworst slack (-?[\d.]+)\nV296_IN_SITU_'+stage+r'_SLACK_END$',log,re.M)
        if len(m)!=1: raise ValueError('Missing extracted slack '+stage)
        return float(m[0])
    if 'V296_CTS45_DRC_COUNT 0' not in log or 'V296_CTS45_IS_ROUTED 1' not in log:
        raise ValueError('Not cleanly routed')
    tail=log[log.rfind('[INFO DRT-0198] Complete detail routing.'):]
    wire=re.findall(r'^Total wire length = (\d+) um\.$',tail,re.M)
    vias=re.findall(r'^Total number of vias = (\d+)\.$',tail,re.M)
    metric=re.findall(r'^V296_METRIC stage=cts45_extracted area_um2=([\d.]+) slew=(\d+) cap=(\d+)$',log,re.M)
    if len(wire)!=1 or len(vias)!=1 or len(metric)!=1:raise ValueError('Incomplete physical metrics')
    area,slew,capviol=metric[0]
    return {'zip_sha256':HASHES[variant], 'tcl_sha256':manifest['original_tcl_sha256'],
        'spef_net_count':len(caps), 'sum_reported_net_cap_pf':sum(caps),
        'p99_net_cap_ff':1000*percentile(caps,.99), 'max_net_cap_ff':1000*max(caps),
        'nets_above_50ff':sum(x>.05 for x in caps),
        'routed_wire_um':int(wire[0]), 'routed_vias':int(vias[0]),
        'area_um2':float(area), 'setup_ns':marked('SETUP'), 'hold_ns':marked('HOLD'),
        'slew_violations':int(slew), 'cap_violations':int(capviol)}

def run(pairwise,serial):
    p=read(pairwise,'pairwise');s=read(serial,'serial_onehot')
    if p['tcl_sha256']!=s['tcl_sha256']:raise ValueError('Unmatched physical Tcl')
    if p['setup_ns']>=.05 or s['setup_ns']>=.05 or p['cap_violations']==0 or s['cap_violations']==0:
        raise ValueError('Original failed gate unexpectedly changed')
    ratio=p['sum_reported_net_cap_pf']/s['sum_reported_net_cap_pf']
    return {'decision':'TAIL_FALSIFIES_UNIFORM_SCALING_BOTH_PHYSICALLY_INFEASIBLE',
        'source_run':40173311725,'pairwise':p,'serial_onehot':s,
        'relative_wire_reduction_pct':100*(1-p['routed_wire_um']/s['routed_wire_um']),
        'relative_cap_sum_reduction_pct':100*(1-ratio),
        'uniform_scaling_p99_prediction_ff':s['p99_net_cap_ff']*ratio,
        'observed_p99_ff':p['p99_net_cap_ff'],
        'p99_excess_over_uniform_null_pct':100*(p['p99_net_cap_ff']/(s['p99_net_cap_ff']*ratio)-1),
        'activity_ratio_break_even_toy':1/ratio,
        'limitations':'Not switched power, timing closure, critical-path attribution, equal consumed area, or GPU speedup.'}

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--pairwise',required=True)
    a.add_argument('--serial',required=True)
    a.add_argument('--output')
    x=a.parse_args()
    result=json.dumps(run(x.pairwise,x.serial),indent=2,sort_keys=True)+'\n'
    if x.output:Path(x.output).write_text(result)
    print(result)
