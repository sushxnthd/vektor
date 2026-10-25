#!/usr/bin/env python3
"""Independent fail-closed recovery of OpenSTA numeric-first path reports.

Original frozen physical run: 40203738175. No physical flow rerun or Tcl edits.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile

PINNED = {
    'pairwise': ('239a648829c41f5cd0229ec1ca6663463ca2a253d9186321bb476869223e640e',
                 -1.047895, -0.036622),
    'serial_onehot': ('d755641eba65a4b89c36f1226ae23e55ce647b390dc910e649d157360d538815',
                      -1.859922, -0.019796),
}
INSERTED = '''puts "V296_IN_SITU_SETUP_SLACK_BEGIN"
report_worst_slack -max -digits 6
puts "V296_IN_SITU_SETUP_SLACK_END"
puts "V296_IN_SITU_HOLD_SLACK_BEGIN"
report_worst_slack -min -digits 6
puts "V296_IN_SITU_HOLD_SLACK_END"
puts "V296_IN_SITU_SETUP_PATHS_BEGIN"
report_checks -path_delay max -digits 6
puts "V296_IN_SITU_SETUP_PATHS_END"
puts "V296_IN_SITU_HOLD_PATHS_BEGIN"
report_checks -path_delay min -digits 6
puts "V296_IN_SITU_HOLD_PATHS_END"
puts "V296_IN_SITU_DONE"

'''


def one(pattern, text):
    hits = re.findall(pattern, text, re.M)
    if len(hits) != 1:
        raise ValueError('missing/ambiguous evidence: ' + pattern)
    return hits[0]


def section(log, label):
    begin, end = ('V296_IN_SITU_' + label + '_' + x for x in ('BEGIN', 'END'))
    if log.splitlines().count(begin) != 1 or log.splitlines().count(end) != 1:
        raise ValueError('ambiguous markers: ' + label)
    a = log.index(begin) + len(begin)
    b = log.index(end)
    if b <= a:
        raise ValueError('inverted markers')
    return log[a:b]


def paths(log, kind, worst):
    block = section(log, kind + '_PATHS')
    starts = re.findall(r'^Startpoint:\s*(.+)$', block, re.M)
    ends = re.findall(r'^Endpoint:\s*(.+)$', block, re.M)
    # OpenSTA pinned binary emits NUMERIC-FIRST lines, not 'slack (VIOLATED) N'.
    suffix = re.findall(r'^\s*(-?(?:\d+(?:\.\d*)?|\.\d+))\s+slack\s+\((?:VIOLATED|MET)\)\s*$', block, re.M)
    prefix = re.findall(r'^\s*slack\s+\((?:VIOLATED|MET)\)\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s*$', block, re.M)
    values = suffix + prefix
    if not starts or len(starts) != len(ends) or len(starts) != len(values):
        raise ValueError('missing or ambiguous path endpoints/slack: ' + kind)
    slacks = [float(x) for x in values]
    if not all(math.isfinite(x) for x in slacks) or abs(min(slacks)-worst) > 0.005:
        raise ValueError('path does not reproduce measured worst slack: ' + kind)
    return [{'start':a.strip(),'end':b.strip(),'slack_ns':s} for a,b,s in zip(starts,ends,slacks)]


def analyze_one(path, variant):
    expected, setup, hold = PINNED[variant]
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError('artifact provenance SHA256 mismatch: ' + variant)
    with ZipFile(path) as z:
        def read(name): return z.read(name)
        manifest = json.loads(read('in_situ_manifest.json'))
        src = read('cts45_tile.tcl')
        probe = read('cts45_tile_in_situ.tcl')
        if hashlib.sha256(src).hexdigest() != manifest['original_tcl_sha256']:
            raise ValueError('original Tcl mismatch')
        if hashlib.sha256(probe).hexdigest() != manifest['probe_tcl_sha256']:
            raise ValueError('probe Tcl mismatch')
        if manifest.get('only_read_only_reports_added') is not True or manifest.get('same_tcl_both_variants') is not True:
            raise ValueError('unmatched probe declaration')
        anchor = b'v296_repair_metrics cts45_extracted\n'
        if src.count(anchor) != 1 or probe.count(anchor + INSERTED.encode()) != 1:
            raise ValueError('missing instrumentation anchor')
        if probe.replace(anchor + INSERTED.encode(), anchor) != src:
            raise ValueError('non-read-only physical changes')
        logbytes = read(variant + '.high.log')
        log = logbytes.decode(errors='replace')
        if log.splitlines().count('V296_IN_SITU_DONE') != 1 or log.splitlines().count('V296_CTS45_DONE') != 1:
            raise ValueError('incomplete physical run')
        physical = json.loads(read(variant + '.tile.audit.json'))
        if physical.get('complete') is not True:
            raise ValueError('incomplete physical audit')
        measured = {}
        for kind, original in (('SETUP',setup),('HOLD',hold)):
            v = float(one(r'^worst slack\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s*$', section(log,kind+'_SLACK')))
            if abs(v-original) > .005 or abs(v-physical['final'][kind.lower()+'_ns']) > .005:
                raise ValueError('measured slack not independently reproduced')
            measured[kind.lower()] = {'worst_slack_ns':v,'critical_paths':paths(log,kind,v)}
        return {'variant':variant,'artifact_sha256':digest,
                'log_sha256':hashlib.sha256(logbytes).hexdigest(),
                'original_tcl_sha256':hashlib.sha256(src).hexdigest(),
                'probe_tcl_sha256':hashlib.sha256(probe).hexdigest(),
                'area_um2':physical['final']['area_um2'],
                'cap_violations':physical['final']['cap'],
                'slew_violations':physical['final']['slew'],
                'feasible':physical['feasible'],**measured}


def self_test():
    sample = ('V296_IN_SITU_SETUP_PATHS_BEGIN\nStartpoint: A\nEndpoint: B\n'
              '             -1.047895   slack (VIOLATED)\nV296_IN_SITU_SETUP_PATHS_END\n')
    assert paths(sample,'SETUP',-1.047895)[0]['start']=='A'
    old = sample.replace('-1.047895   slack (VIOLATED)', 'slack (VIOLATED) -1.047895')
    assert paths(old,'SETUP',-1.047895)[0]['end']=='B'
    for corrupt in [sample.replace('-1.047895','-0.047895'),sample.replace('Endpoint: B',''),
                    sample.replace('slack (VIOLATED)','slack (UNKNOWN)')]:
        try: paths(corrupt,'SETUP',-1.047895)
        except ValueError: pass
        else: raise AssertionError('adversarial path falsely accepted')
    print('V296_IN_SITU_ARTIFACT_RECOVERY_SELFTEST_PASS')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pairwise-zip',type=Path)
    parser.add_argument('--serial-zip',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test: self_test()
    if args.pairwise_zip or args.serial_zip:
        if not args.pairwise_zip or not args.serial_zip:
            parser.error('both SHA-pinned artifacts required')
        rows={name:analyze_one(path,name) for name,path in
              [('pairwise',args.pairwise_zip),('serial_onehot',args.serial_zip)]}
        if rows['pairwise']['original_tcl_sha256'] != rows['serial_onehot']['original_tcl_sha256']:
            raise ValueError('unmatched physical source')
        if rows['pairwise']['probe_tcl_sha256'] != rows['serial_onehot']['probe_tcl_sha256']:
            raise ValueError('unmatched probe source')
        print(json.dumps({'decision':'EXTRACTED_CRITICAL_PATHS_IDENTIFIED_BOTH_INFEASIBLE',
                          'physical_run_id':40203738175,
                          'setup_lead_ns':rows['pairwise']['setup']['worst_slack_ns']-rows['serial_onehot']['setup']['worst_slack_ns'],
                          'gpu_speedup':'NOT_ESTABLISHED','rows':rows},indent=2,sort_keys=True))
    if not args.self_test and not args.pairwise_zip:
        parser.error('choose --self-test or both --*-zip')


if __name__=='__main__': main()
