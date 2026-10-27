#!/usr/bin/env python3
"""Independently map extracted STA flop instances to SHA-pinned synthesized RTL nets."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ORIGINAL = {
    'pairwise': {
        'zip_sha256': 'c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7',
        'start': '_13159_', 'end': '_13098_',
    },
    'serial_onehot': {
        'zip_sha256': '928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4',
        'start': '_13099_', 'end': '_13046_',
    },
}


def get_ff(netlist, name):
    pattern = r'(?m)^\s*(DFF\w+)\s+' + re.escape(name) + r'\s*\((.*?)\);'
    matches = re.findall(pattern, netlist, re.S)
    if len(matches) != 1:
        raise ValueError(f'{name}: expected exactly one DFF instance, got {len(matches)}')
    cell, body = matches[0]
    pins = dict(re.findall(r'\.([A-Za-z]+)\s*\(([^()]*)\)', body))
    if not all(k in pins for k in ('CK', 'D', 'Q')):
        raise ValueError(f'{name}: missing clock/data/Q')
    return {'instance': name, 'cell': cell, 'clock': pins['CK'].strip(),
            'data': pins['D'].strip(), 'q': pins['Q'].strip()}


def audit_one(path, variant):
    original = ORIGINAL[variant]
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != original['zip_sha256']:
        raise ValueError('Original artifact ZIP SHA mismatch: ' + variant)
    with zipfile.ZipFile(path) as z:
        netlist = z.read(variant + '.v').decode('utf-8')
    start = get_ff(netlist, original['start'])
    end = get_ff(netlist, original['end'])
    if 'scheduler.rr1' not in start['q'] or 'staged_operand_data' not in end['q']:
        raise ValueError('Source-level cone attribution not established')
    if start['clock'] != 'clk' or end['clock'] != 'clk':
        raise ValueError('Unexpected FF clock')
    return {'variant': variant, 'original_zip_sha256': original['zip_sha256'],
            'startpoint': start, 'endpoint': end}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pairwise-zip', type=Path, required=True)
    p.add_argument('--serial-zip', type=Path, required=True)
    a = p.parse_args()
    rows = [audit_one(a.pairwise_zip, 'pairwise'),
            audit_one(a.serial_zip, 'serial_onehot')]
    print(json.dumps({'decision': 'SYNTHESIZED_SCHEDULER_TO_OPERAND_CONE_MAPPED',
                      'physical_closure': False, 'gpu_speedup_claim': False,
                      'results': rows}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
