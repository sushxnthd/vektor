#!/usr/bin/env python3
"""Independent, SHA-pinned falsification of V296 post-CTS diagnostic artifacts.

This analyzes frozen GitHub Actions ZIPs, not GitHub job status summaries. It
fails closed if provenance, checkpoint order, expected failure, or slack differs.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED = {
    'pairwise': {
        'sha256': '6c1d43d33dab96fd67721479f5987ad68c12f323aeede396df31cc8b4eccacc5',
        'stage': 'cts45_postcts_global',
        'failure': 'STA-0563',
        'expected_area': 16509.556388655255,
        'expected_slack': -0.270312,
    },
    'serial_onehot': {
        'sha256': 'ba1ab686ea81720bed3c4cf9cd9988ee0607e527b3670286e08be80eba234570',
        'stage': 'cts45_clock_tree',
        'failure': 'CENSORED_TIMEOUT_70_MIN',
        'expected_area': 18785.451416647447,
        'expected_slack': -1.003700,
    },
}
STAGE = re.compile(r'V296_METRIC stage=(\S+) area_um2=([\d.]+) slew=(\d+) cap=(\d+)\s+worst slack ([+-]?[\d.]+)')

def analyze(path,variant,check_sha=True):
    expected=EXPECTED[variant]
    raw=Path(path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if check_sha and digest != expected['sha256']:
        raise ValueError('Artifact SHA-256 mismatch: '+variant)
    with zipfile.ZipFile(path) as z:
        name=variant+'.high.log'
        if name not in z.namelist():raise ValueError('Missing original OpenROAD log')
        log=z.read(name).decode('utf-8')
    stages={m.group(1):{'area_um2':float(m.group(2)),'slew_violations':int(m.group(3)),
                         'cap_violations':int(m.group(4)),'worst_slack_ns':float(m.group(5))}
            for m in STAGE.finditer(log)}
    if expected['stage'] not in stages:raise ValueError('Missing required physical checkpoint')
    row=stages[expected['stage']]
    if abs(row['area_um2']-expected['expected_area'])>1e-6 or abs(row['worst_slack_ns']-expected['expected_slack'])>1e-6:
        raise ValueError('Physical checkpoint mismatch')
    if 'V296_ENDPOINT_DIAG_DONE' in log:raise ValueError('Completed diagnostic unexpectedly')
    if variant=='pairwise':
        if '[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag.' not in log:
            raise ValueError('Missing pinned invalid-flag tool failure')
        if 'V296_ENDPOINT_DIAG_BEGIN' not in log:raise ValueError('No diagnostic entry')
        if 'V296_ENDPOINT_DIAG_SETUP_PATHS_END' in log:raise ValueError('Unexpected completed path report')
    else:
        if 'V296_CTS45_CTS_END' not in log:raise ValueError('Serial CTS never completed')
        if 'V296_ENDPOINT_DIAG_BEGIN' in log:raise ValueError('Serial diagnostic actually started')
        if 'V296_CTS45_SETUP_MARGIN 0.250' not in log:raise ValueError('Missing stalled repair marker')
        if 'V296_STAGE_END cts45_postcts_repaired' in log:raise ValueError('Serial postCTS repair actually completed')
    return {'artifact_sha256':digest,'checkpoint':expected['stage'],**row,
            'diagnostic_status':expected['failure'],
            'post_route_signoff':False}

def self_test():
    assert set(EXPECTED)=={'pairwise','serial_onehot'}
    assert STAGE.search('V296_METRIC stage=foo area_um2=1.0 slew=0 cap=0\nworst slack -0.2')
    assert not STAGE.search('wrong format')
    print('V296_ENDPOINT_TIMEOUT_FORENSICS_SELFTEST_PASS')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pairwise-zip',type=Path)
    p.add_argument('--serial-zip',type=Path)
    p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if args.self_test:self_test()
    if args.pairwise_zip or args.serial_zip:
        if not(args.pairwise_zip and args.serial_zip):p.error('Both artifacts required')
        a=analyze(args.pairwise_zip,'pairwise')
        b=analyze(args.serial_zip,'serial_onehot')
        with zipfile.ZipFile(args.pairwise_zip) as z:sa=z.read('pairwise.high.log').decode()
        with zipfile.ZipFile(args.serial_zip) as z:sb=z.read('serial_onehot.high.log').decode()
        def common(s):
            matches=[m for m in STAGE.finditer(s) if m.group(1)=='cts45_fourth_routed']
            if len(matches)!=1:raise ValueError('Missing or duplicate common fourth stage')
            m=matches[0]
            return {'area_um2':float(m.group(2)),'slack_ns':float(m.group(5))}
        ca,cb=common(sa),common(sb)
        result={'evidence_tier':'INCOMPLETE_PRECTS_POSTCTS_NO_SIGNOFF',
                'hosted_run':40263375059,'pairwise':a,'serial_onehot':b,
                'common_fourth_stage':{'pairwise':ca,'serial_onehot':cb,
                'candidate_area_reduction_pct':100*(cb['area_um2']-ca['area_um2'])/cb['area_um2'],
                'candidate_setup_slack_lead_ns':ca['slack_ns']-cb['slack_ns']},
                'matched_postcts_comparison_available':False,
                'no_speedup_or_electrical_claim':True}
        print(json.dumps(result,indent=2,sort_keys=True))
        print('V296_ENDPOINT_DIAGNOSTIC_BOTH_FAIL_CLOSED')
    elif not args.self_test:p.error('Supply both artifacts or --self-test')

if __name__=='__main__':main()
