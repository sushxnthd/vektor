#!/usr/bin/env python3
"""Independent SHA-pinned audit of OpenSTA extracted-SPEF worst-path topology.

Reads completed OpenROAD replay logs, not synthetic timing or generated paths.
No RTL, clock, RC, placement, or timing repair is performed.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

INPUTS = {
    'pairwise': ('06f0807c85f0d4e073bf9654cebaabe94d0f97472e67f6335cff88f48fc26da9', -0.220829, -0.010023),
    'serial_onehot': ('ca2929b12d123af888f13772cc2ad3dc2ff3f53d7f50323b27417f845dfec6a6', -0.711405, -0.013032),
}
NUM = r'-?(?:\d+(?:\.\d*)?|\.\d+)'
SLACK = re.compile(r'^\s*(' + NUM + r')\s+slack(?:\s+\([^)]*\))?\s*$', re.M)
CELL = re.compile(r'\s[\^v]\s+(\S+)\s+\(([^()]+)\)\s*$')
TIME = re.compile(r'^\s*\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\^v]')


def audit_one(path, variant):
    expected, setup, hold = INPUTS[variant]
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(variant + ': ZIP SHA256 mismatch')
    with zipfile.ZipFile(path) as z:
        log = z.read(variant + '.postroute.replay.log').decode('utf-8')
    if log.splitlines().count('V296_REPLAY_DONE') != 1:
        raise ValueError(variant + ': incomplete OpenROAD replay')
    out = {'variant': variant, 'replay_zip_sha256': expected,
           'evidence_tier': 'ONE_WORST_EXTRACTED_PATH_ONLY'}
    for mode, original in [('SETUP', setup), ('HOLD', hold)]:
        a = 'V296_REPLAY_' + mode + '_PATHS_BEGIN'
        b = 'V296_REPLAY_' + mode + '_PATHS_END'
        if log.splitlines().count(a) != 1 or log.splitlines().count(b) != 1:
            raise ValueError(variant + ': missing path markers')
        section = log.split(a, 1)[1].split(b, 1)[0]
        starts = re.findall(r'^Startpoint:\s*(.+)$', section, re.M)
        ends = re.findall(r'^Endpoint:\s*(.+)$', section, re.M)
        slacks = SLACK.findall(section)
        if len(starts) != 1 or len(ends) != 1 or len(slacks) != 1:
            raise ValueError(variant + ': ambiguous path')
        observed = float(slacks[0])
        if abs(observed - original) > 0.001:
            raise ValueError(variant + ': path slack differs from original >1ps')
        cells = []
        for line in section.splitlines():
            m = CELL.search(line)
            if m:
                t = TIME.match(line)
                cells.append({'pin': m[1], 'cell': m[2],
                              'time_ns': float(t[1]) if t else None})
        if not cells:
            raise ValueError(variant + ': no timed cell path')
        best, run = [], []
        for c in cells + [{'cell': 'END'}]:
            if 'BUF_' in c['cell']:
                run.append(c)
            else:
                if len(run) > len(best):
                    best = run[:]
                run = []
        inc = None
        if best:
            i = next(i for i, c in enumerate(cells) if c is best[0])
            if i > 0 and cells[i - 1]['time_ns'] is not None and best[-1]['time_ns'] is not None:
                inc = round(best[-1]['time_ns'] - cells[i - 1]['time_ns'], 6)
        out[mode.lower()] = {
            'startpoint': starts[0], 'endpoint': ends[0], 'slack_ns': observed,
            'timed_cell_pin_rows': len(cells),
            'buffer_pin_rows': sum('BUF_' in c['cell'] for c in cells),
            'longest_consecutive_buffer_chain': len(best),
            'chain_incremental_path_delay_ns': inc,
            'chain_first_pin': best[0]['pin'] if best else None,
            'chain_last_pin': best[-1]['pin'] if best else None,
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pairwise-zip', type=Path, required=True)
    p.add_argument('--serial-zip', type=Path, required=True)
    a = p.parse_args()
    out = [audit_one(a.pairwise_zip, 'pairwise'),
           audit_one(a.serial_zip, 'serial_onehot')]
    print(json.dumps({'decision': 'REPRODUCED_EXTRACTED_WORST_PATH_TOPOLOGY_NOT_SIGNOFF',
                      'physically_feasible': False, 'gpu_speedup_claim': False,
                      'results': out}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
