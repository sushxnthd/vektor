#!/usr/bin/env python3
"""Independent fail-closed audit of hosted V296 operand-capture artifacts.

Usage: python3 operand_capture_hosted_audit.py MAPPED.zip PAIRWISE.zip SERIAL.zip
Evidence: Nangate45 mapped and pre-CTS global-route estimated parasitics only.
"""
import hashlib
import json
import re
import sys
import zipfile

ARTIFACTS = {
    'mapped': '0de959a98a7185bde3bbcebbb7412c0cfb56900c4e18cdef497ff3468b181a74',
    'pairwise': 'a3d96cfd3967c535531e7ef9ebb0cb8d0bfe5dfeadf6005b424e34646a6c9c6e',
    'serial': '60e63f1d7f330bd8d3786a511830c80c7e55f5c069a69252cdafd09432b52a15',
}
EXPECT = {
    'original_pairwise': 8880.676,
    'original_serial': 9589.300,
    'retimed_pairwise': 9374.106,
    'retimed_serial': 10217.858,
}

def check(cond, why):
    if not cond:
        raise ValueError(why)

def one(text, pattern, why):
    matches = re.findall(pattern, text, re.M)
    check(len(matches) == 1, f'{why}: expected exactly one match, got {len(matches)}')
    return matches[0]

def audit(paths):
    data = {}
    for name, path in zip(ARTIFACTS, paths):
        with open(path, 'rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        check(digest == ARTIFACTS[name], f'{name}: ZIP SHA256 mismatch')
        with zipfile.ZipFile(path) as z:
            check(z.testzip() is None, f'{name}: damaged ZIP')
            data[name] = {entry: z.read(entry).decode('utf-8') for entry in z.namelist()
                          if entry.endswith(('.log', '.json', '.v', '.sha256'))}
    result = {'evidence_tier': 'PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS_NOT_SIGNOFF',
              'source_run': 40288329940, 'artifact_sha256': ARTIFACTS, 'mapped_um2': {}, 'physical': {}}
    for key, area in EXPECT.items():
        log = data['mapped'][key + '.log']
        observed = float(one(log, r"Chip area for module '[^']+':\s*([0-9.]+)", key+' mapped area'))
        check(abs(observed - area) < 1e-5, f'{key}: unexpected mapped area')
        result['mapped_um2'][key] = observed
    check('PRECTS_ESTIMATED_ONLY_NOT_SIGNOFF' in data['pairwise']['operand_capture_manifest.json'], 'pairwise tier')
    check('PRECTS_ESTIMATED_ONLY_NOT_SIGNOFF' in data['serial']['operand_capture_manifest.json'], 'serial tier')
    check(data['pairwise']['operand_capture_manifest.json'] == data['serial']['operand_capture_manifest.json'], 'nonidentical matched protocol')
    for name, filebase, expected_start, expected_end in [
        ('pairwise', 'pairwise', '_12667_', '_12646_'),
        ('serial', 'serial_onehot', '_13413_', '_13363_'),
    ]:
        log = data[name][filebase+'.high.log']
        metric = one(log, r'V296_METRIC stage=cts45_fourth_routed area_um2=([0-9.]+) slew=(\d+) cap=(\d+)', name+' physical metrics')
        area, slew, cap = float(metric[0]), int(metric[1]), int(metric[2])
        setup_match = re.search(r'V296_FOURTH_CONE_SETUP_PATH_BEGIN\s*(.*?)\s*V296_FOURTH_CONE_SETUP_PATH_END', log, re.S)
        check(setup_match is not None, name+' missing setup path')
        section = setup_match.group(1)
        start = one(section, r'^Startpoint: (\S+)', name+' start')
        end = one(section, r'^Endpoint: (\S+)', name+' end')
        check((start,end) == (expected_start,expected_end), name+' unexpected critical cone')
        slack = float(one(section, r'^\s*(-?\d+\.\d+)\s+slack \(VIOLATED\)', name+' setup slack'))
        hold_match = re.search(r'V296_FOURTH_CONE_HOLD_PATH_BEGIN\s*(.*?)\s*V296_FOURTH_CONE_HOLD_PATH_END', log, re.S)
        check(hold_match is not None, name+' missing hold path')
        hold = float(one(hold_match.group(1), r'^\s*(-?\d+\.\d+)\s+slack \(MET\)', name+' hold slack'))
        check(slew == 0 and cap == 0, name+' nonzero intermediate electrical violations')
        check(slack < 0 and hold > 0, name+' unexpectedly changed feasibility')
        netlist = data[name][filebase+'.v']
        for n, signal in [(expected_start, 'scheduler.rr'), (expected_end, 'staged_operand_data')]:
            match = re.search(r'DFFR_X1\s+'+re.escape(n)+r'\s*\((.*?)\);', netlist, re.S)
            check(match is not None and signal in match.group(1), name+': endpoint attribution failed '+n)
        result['physical'][name] = {'area_um2':area,'setup_slack_ns':slack,'hold_slack_ns':hold,
                                    'slew_violations':slew,'cap_violations':cap,
                                    'critical_start':start,'critical_end':end}
    a,b = result['physical']['pairwise'],result['physical']['serial']
    result['relative'] = {
        'candidate_mapped_area_saving_pct':100*(1-result['mapped_um2']['retimed_pairwise']/result['mapped_um2']['retimed_serial']),
        'candidate_prects_area_saving_pct':100*(1-a['area_um2']/b['area_um2']),
        'candidate_setup_lead_ps':(a['setup_slack_ns']-b['setup_slack_ns'])*1000,
        'candidate_guard_deficit_ps':(0.05-a['setup_slack_ns'])*1000,
        'serial_guard_deficit_ps':(0.05-b['setup_slack_ns'])*1000,
        'candidate_retiming_mapped_area_cost_pct':100*(result['mapped_um2']['retimed_pairwise']/result['mapped_um2']['original_pairwise']-1),
        'serial_retiming_mapped_area_cost_pct':100*(result['mapped_um2']['retimed_serial']/result['mapped_um2']['original_serial']-1),
    }
    return result

if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    try:
        print(json.dumps(audit(sys.argv[1:]), indent=2, sort_keys=True))
    except (ValueError, KeyError, zipfile.BadZipFile) as exc:
        raise SystemExit(f'AUDIT_FAIL_CLOSED: {exc}') from exc
