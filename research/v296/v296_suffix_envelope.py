#!/usr/bin/env python3
"""SHA-pinned extracted V296 critical-path suffix bounds; NOT physical repair."""
import argparse
import json
from decimal import Decimal as D
from pathlib import Path
from deep_bank_extracted_path_locality import E, require_zip, section, numeric_worst

GUARD = D('0.050')


def parse_rows(log, case):
    c = E[case]
    if numeric_worst(section(log, 'SETUP_WORST')) != c['setup']:
        raise ValueError('Pinned routed setup slack changed')
    s = section(log, 'SETUP_PATHS')
    rows = []
    for line in s.splitlines():
        f = line.split()
        a = [i for i, v in enumerate(f) if v in ('v', '^')]
        if len(a) != 1 or a[0] < 2 or a[0] + 2 >= len(f):
            continue
        j = a[0]
        try:
            inc, arrival = D(f[j-2]), D(f[j-1])
        except Exception:
            continue
        if '/' in f[j+1]:
            rows.append(dict(inc=inc, arrival=arrival,
                             pin=f[j+1], cell=f[j+2].strip('()')))
    launch = [i for i, r in enumerate(rows) if r['pin'] == c['start'] + '/Q']
    capture = [i for i, r in enumerate(rows) if r['pin'] == c['end'] + '/D']
    if len(launch) != 1 or len(capture) != 1 or capture[0] <= launch[0]:
        raise ValueError('Pinned register-to-register path missing')
    data = rows[launch[0]:capture[0]+1]
    if len(rows) != c['npins']:
        raise ValueError('Path pin count changed')
    for a, b in zip(data, data[1:]):
        if abs((b['arrival'] - a['arrival']) - b['inc']) > D('0.000002'):
            raise ValueError('OpenSTA increments do not reconcile')
    return data


def cellclass(cell):
    if cell.startswith(('BUF', 'CLKBUF')):
        return 'buffer'
    if cell.startswith('MUX'):
        return 'mux'
    if cell.startswith('INV'):
        return 'inverter'
    return 'other_logic'


def analyze(case, zip_path):
    c = E[case]
    with require_zip(zip_path, c['replay_sha']) as z:
        log = z.read('replay.log').decode('utf-8')
        evidence = json.loads(z.read('extracted_paths.json'))
    if (evidence['artifact_id'] != c['source_artifact'] or
            evidence['original_zip_sha256'] != c['source_sha'] or
            evidence['physical_gate'] != 'FAIL' or
            evidence['matched_comparison'] is not False):
        raise ValueError('Source evidence provenance changed')
    rows = parse_rows(log, case)
    deficit = GUARD - c['setup']
    mux = [i for i, r in enumerate(rows) if cellclass(r['cell']) == 'mux']
    if not mux or mux[0] == 0:
        raise ValueError('No final mux tail found')
    tail = rows[-1]['arrival'] - rows[mux[0]-1]['arrival']
    categories = {k: sum((r['inc'] for r in rows[1:] if cellclass(r['cell']) == k), D(0))
                  for k in ('buffer', 'mux', 'inverter', 'other_logic')}
    if abs(sum(categories.values()) - (rows[-1]['arrival'] - rows[0]['arrival'])) > D('0.000003'):
        raise ValueError('Path delay decomposition failed')
    cuts = {}
    for speed in (D('1.5'), D('2'), D('3'), D('4')):
        needed = deficit/(1-1/speed)
        valid = [i for i in range(len(rows)-1)
                 if rows[-1]['arrival']-rows[i]['arrival'] >= needed]
        if valid:
            i = valid[-1]
            cuts[str(speed)] = dict(pin=rows[i]['pin'],
                                    arrival_ns=str(rows[i]['arrival']),
                                    affected_following_rows=len(rows)-1-i,
                                    suffix_ns=str(rows[-1]['arrival']-rows[i]['arrival']),
                                    minimum_suffix_ns=str(needed))
        else:
            cuts[str(speed)] = dict(status='NO_ELIGIBLE_SUFFIX')
    return dict(case=case, source_sha256=c['replay_sha'],
                setup_slack_ns=str(c['setup']), setup_recovery_ns=str(deficit),
                data_path_delay_ns=str(rows[-1]['arrival']-rows[0]['arrival']),
                final_mux_start=rows[mux[0]]['pin'], final_mux_tail_ns=str(tail),
                remaining_deficit_if_zero_mux_tail_ns=str(max(D(0), deficit-tail)),
                mux_tail_only_sufficient=tail>=deficit,
                path_class_delay_ns={k:str(v) for k,v in categories.items()},
                cuts=cuts, physical_gate='FAIL', matched_depth=False,
                repair_demonstrated=False, gpu_speedup=False)


def selftest():
    assert D('0.050')-D('-0.684592') == D('0.734592')
    assert D('0.050')-D('-1.316510') == D('1.366510')
    assert cellclass('MUX2_X1') == 'mux'
    assert cellclass('CLKBUF_X2') == 'buffer'
    try:
        parse_rows('bad', 'D8_pairwise')
    except ValueError:
        pass
    else:
        raise AssertionError('Malformed path accepted')
    print('V296_SUFFIX_ENVELOPE_SELFTEST_PASS')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--d8',type=Path)
    p.add_argument('--d4',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test:
        selftest()
    if a.d8 and a.d4:
        out=dict(evidence_tier='SHA-pinned extracted OpenSTA fixed-path counterfactual',
                 prospective=False, holdouts='SEALED', physical_gate='FAIL',
                 matched_architecture_comparison=False,
                 cases=[analyze('D8_pairwise',a.d8),analyze('D4_serial_onehot',a.d4)])
        s=json.dumps(out,indent=2,sort_keys=True)+'\n'
        if a.output:
            a.output.write_text(s)
        else:
            print(s)
    elif not a.self_test:
        p.error('Both original replay ZIPs are required')

if __name__=='__main__':
    main()
