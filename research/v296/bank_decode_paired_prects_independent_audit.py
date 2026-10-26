#!/usr/bin/env python3
"""Fail-closed independent audit of both original V296 bank-decode pre-CTS ZIPs.

Checks exact ZIP digests, common source/constraints, stage provenance,
per-variant final markers and stage metrics. Not CTS/routed signoff.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED = {
    'pairwise': 'c5ec1f863b0cd23cc88fc9f0f468de87a90e1cb1dc0a3698e2af5d872a01cd2c',
    'serial_onehot': '52fd64575ac2124b171ecea3bcb27857b249589a11dc1624daeed179b33138b4',
}
STAGE = 'cts45_fourth_routed'
GUARD = 0.05

def one(path, variant):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED[variant]:
        raise ValueError(f'{variant}: ZIP digest mismatch')
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP entries')
        manifest = json.loads(z.read('fourth_diag_manifest.json'))
        decode = json.loads(z.read('bank_decode_manifest.json'))
        tile = json.loads(z.read('tile_manifest.json'))
        if not (manifest['clock_ns'] == 3.5 and manifest['extracted_rc'] is False
                and manifest['postcts'] is False and manifest['routed'] is False
                and manifest['shared_fourth_stage'] is True
                and manifest['serial_fifth_control_repair_excluded'] is True
                and decode['both_contestants_same_retiming'] is True
                and decode['serial_fifth_stage_excluded'] is True
                and tile['same_tcl_for_both'] is True):
            raise ValueError('physical provenance not pre-CTS or not symmetric')
        tcl_sha = hashlib.sha256(z.read('cts45_fourth_diag.tcl')).hexdigest()
        if tcl_sha != decode['unchanged_fourth_tcl_sha256'] or tcl_sha != manifest['generated_tcl_sha256']:
            raise ValueError('constraint Tcl SHA mismatch')
        log = z.read(f'{variant}.high.log').decode('utf-8')
        if log.count('V296_FOURTH_CONE_DONE') != 1 or 'V296_FOURTH_CONE_TIER PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS' not in log:
            raise ValueError('missing or duplicated final pre-CTS marker')
        area = re.findall(r'V296_METRIC stage=' + STAGE + r' area_um2=([0-9.]+) slew=(\d+) cap=(\d+)', log)
        if len(area) != 1:
            raise ValueError('missing or duplicated final stage metric')
        a, slew, cap = area[0]
        def worst(label):
            m = re.findall(r'V296_FOURTH_CONE_WORST_' + label + r'_BEGIN\s+worst slack\s+(-?[0-9.]+)\s+V296_FOURTH_CONE_WORST_' + label + r'_END', log)
            if len(m) != 1:
                raise ValueError('missing or duplicated worst slack')
            return float(m[0])
        setup, hold = worst('SETUP'), worst('HOLD')
        if float(a) <= 0 or int(slew) != 0 or int(cap) != 0:
            raise ValueError('final stage electrical or area failure')
        return {
            'artifact_sha256': digest, 'variant': variant,
            'stage': 'PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS_NOT_SIGNOFF',
            'area_um2': float(a), 'setup_slack_ns': setup, 'hold_slack_ns': hold,
            'max_slew_violations': int(slew), 'max_cap_violations': int(cap),
            'meets_50ps_prects_setup_guard': setup >= GUARD,
            'common_manifest': manifest, 'decode_manifest': decode,
            'tile_manifest': tile,
            'common_platform_hashes': '\n'.join(z.read(f'{variant}.inputs.sha256').decode().splitlines()[:5]),
        }

def audit(pairwise, serial):
    p = one(pairwise, 'pairwise')
    s = one(serial, 'serial_onehot')
    for key in ('common_manifest', 'decode_manifest', 'tile_manifest', 'common_platform_hashes'):
        if p[key] != s[key]:
            raise ValueError('unmatched source/constraints: ' + key)
    if not (p['setup_slack_ns'] > s['setup_slack_ns'] and p['area_um2'] < s['area_um2']):
        raise ValueError('unexpected comparison, inspect artifacts')
    return {
        'evidence_tier': 'PAIRED_PRECTS_ESTIMATED_PARASITICS_NOT_ROUTED_SIGNOFF',
        'source_run_id': 40337484954,
        'candidate': {k:v for k,v in p.items() if k not in ('common_manifest','decode_manifest','tile_manifest','common_platform_hashes')},
        'serial': {k:v for k,v in s.items() if k not in ('common_manifest','decode_manifest','tile_manifest','common_platform_hashes')},
        'area_saving_pct': 100*(s['area_um2']-p['area_um2'])/s['area_um2'],
        'setup_slack_advantage_ns': p['setup_slack_ns']-s['setup_slack_ns'],
        'candidate_margin_above_50ps_guard_ps': (p['setup_slack_ns']-GUARD)*1000,
        'serial_shortfall_to_50ps_guard_ps': (GUARD-s['setup_slack_ns'])*1000,
        'mapped_area_order_reverses_at_prects': True,
        'fifth_stage_serial_not_included': True,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pairwise',required=True)
    ap.add_argument('--serial',required=True)
    ap.add_argument('--output')
    args=ap.parse_args()
    out=audit(args.pairwise,args.serial)
    if args.output: Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('candidate','serial')},indent=2))
    print('V296_BANK_DECODE_PAIRED_PRECTS_INDEPENDENT_AUDIT_PASS')

if __name__=='__main__': main()
