#!/usr/bin/env python3
"""Independent post-CTS slew-violator-to-SPEF-net audit; no timing repair."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

VIOLATOR = re.compile(r'^\s*(\S+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(-\d+(?:\.\d+)?)\s+\(VIOLATED\)\s*$')

def parse_violators(log):
    start, end = 'V296_CTS45_SLEW_VIOLATORS_BEGIN', 'V296_CTS45_SLEW_VIOLATORS_END'
    if log.count(start) != 1 or log.count(end) != 1:
        raise ValueError('missing or duplicate slew delimiters')
    block = log.split(start, 1)[1].split(end, 1)[0]
    hits = []
    for line in block.splitlines():
        m = VIOLATOR.match(line)
        if m:
            pin, limit, slew, slack = m.groups()
            if abs(float(limit) - float(slew) - float(slack)) > 0.000003:
                raise ValueError('inconsistent slew slack')
            hits.append({'pin': pin, 'limit_ns': float(limit), 'slew_ns': float(slew), 'excess_ns': -float(slack)})
    if len(hits) != len(set(x['pin'] for x in hits)):
        raise ValueError('duplicate violating pin')
    metric = re.findall(r'(?m)^V296_METRIC stage=cts45_extracted area_um2=\S+ slew=(\d+) cap=(\d+)\s*$', log)
    if len(metric) != 1 or len(hits) != int(metric[0][0]):
        raise ValueError('slew count disagrees with extracted stage')
    return hits

def parse_spef(spef):
    if '*NAME_MAP\n' not in spef or '*D_NET ' not in spef:
        raise ValueError('missing SPEF name map or D_NET')
    header = spef.split('*D_NET ', 1)[0]
    names = {int(a): b for a, b in re.findall(r'(?m)^\*(\d+)\s+(\S+)\s*$', header)}
    nets = {}
    pin_to_net = {}
    for chunk in spef.split('*D_NET ')[1:]:
        if '*CONN\n' not in chunk or '*CAP\n' not in chunk:
            raise ValueError('incomplete SPEF D_NET')
        key, cap = chunk.split(None, 2)[:2]
        conns = chunk.split('*CONN\n', 1)[1].split('*CAP\n', 1)[0]
        pins, drivers, loads, ports = [], [], [], []
        for line in conns.splitlines():
            m = re.match(r'^\*(I|P)\s+(\S+)\s+([IOB])(?:\s|$)', line)
            if not m:
                continue
            kind, ref, direction = m.groups()
            if kind == 'I':
                x = re.fullmatch(r'\*(\d+):(.+)', ref)
                if not x or int(x.group(1)) not in names:
                    raise ValueError('unresolved SPEF instance')
                ref = names[int(x.group(1))] + '/' + x.group(2)
            if ref in pin_to_net:
                raise ValueError('SPEF pin in multiple nets: ' + ref)
            pin_to_net[ref] = key
            pins.append(ref)
            if kind == 'P':
                ports.append(ref)
            elif direction == 'O':
                drivers.append(ref)
            elif direction == 'I':
                loads.append(ref)
        nets[key] = {'cap_pf': float(cap), 'pin_count': len(pins),
                     'load_count': len(loads), 'drivers': drivers, 'ports': ports}
    return nets, pin_to_net

def audit(log, spef):
    violations = parse_violators(log)
    nets, mapping = parse_spef(spef)
    missing = [v['pin'] for v in violations if v['pin'] not in mapping]
    if missing:
        raise ValueError('violating pins absent from SPEF: ' + repr(missing))
    counts = Counter(mapping[v['pin']] for v in violations)
    rows = []
    for key, count in counts.most_common():
        selected = [v for v in violations if mapping[v['pin']] == key]
        rows.append({'net_id': key, **nets[key], 'violating_pins': count,
                     'worst_excess_ps': round(max(v['excess_ns'] for v in selected)*1000, 6),
                     'worst_slew_ps': round(max(v['slew_ns'] for v in selected)*1000, 6)})
    return {'violator_count': len(violations), 'distinct_violating_nets': len(rows),
            'nets': rows, 'provenance': 'SPEF connectivity + extracted max-slew report; not repair/signoff'}

def self_test():
    sample = ('V296_METRIC stage=cts45_extracted area_um2=10 slew=1 cap=0\n'
              'V296_CTS45_SLEW_VIOLATORS_BEGIN\n'
              'U1/A 0.250000 0.270000 -0.020000 (VIOLATED)\n'
              'V296_CTS45_SLEW_VIOLATORS_END\n')
    spef = ('*SPEF "ieee 1481-1999"\n*NAME_MAP\n*1 U1\n*2 U2\n'
            '*D_NET *3 0.12\n*CONN\n*P out O\n*I *1:A I *D AND2_X1\n'
            '*I *2:ZN O *D INV_X32\n*CAP\n*END\n')
    result = audit(sample, spef)
    assert result['distinct_violating_nets'] == 1
    assert result['nets'][0]['drivers'] == ['U2/ZN']
    assert result['nets'][0]['load_count'] == 1
    for broken in (sample.replace('slew=1','slew=2'), sample.replace('U1/A','MISSING/A')):
        try:
            audit(broken, spef)
        except ValueError:
            pass
        else:
            raise AssertionError('fail-open on malformed evidence')
    print('CTS45_SLEW_SPEF_FORENSICS_SELFTEST_PASS')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--log', type=Path)
    p.add_argument('--spef', type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test()
    else:
        if not args.log or not args.spef:
            p.error('requires --log and --spef')
        print(json.dumps(audit(args.log.read_text(), args.spef.read_text()), indent=2))
