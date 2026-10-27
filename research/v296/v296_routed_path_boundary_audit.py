#!/usr/bin/env python3
"""SHA-pinned path topology audit. Pre-CTS paths are NOT routed paths."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

SHA = {
    'pairwise': 'c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7',
    'serial_onehot': '928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4',
}
PATH = re.compile(r'Startpoint: (\S+).*?Endpoint: (\S+).*?Path Type: max\s+(.*?)(?=\nV296_|\nStartpoint:|\Z)', re.S)
CELL = re.compile(r'^\s*\d+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s+[\^v]\s+(\S+)\s+\(([^)]+)\)', re.M)
FLOP = re.compile(r'\bDFF\w*\s+(\S+)\s*\(\s*\.CK\([^)]*\),\s*\.D\([^)]*\),\s*\.Q\(([^)]+)\)', re.S)
STAGE = re.compile(r'V296_STAGE_BEGIN (\w+)\nV296_METRIC stage=\1 area_um2=([\d.]+) slew=(\d+) cap=(\d+)\nworst slack (-?[\d.]+)')


def chain(cells):
    best = (0, 0.0, None, None)
    run = []
    for delay, name, kind in cells + [(0, '', 'END')]:
        if re.match(r'(?:CLK)?BUF_', kind):
            run.append((delay, name))
        else:
            if run and len(run) > best[0]:
                best = (len(run), sum(x[0] for x in run), run[0][1], run[-1][1])
            run = []
    return dict(count=best[0], cell_delay_ns=round(best[1], 6), first=best[2], last=best[3])


def audit(blob, variant):
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA[variant]:
        raise ValueError('Original artifact SHA-256 mismatch')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        log = z.read(variant + '.high.log').decode()
        net = z.read(variant + '.v').decode()
    if f'V296_CTS45_VARIANT {variant}' not in log or 'V296_CTS45_DONE' not in log or 'V296_CTS45_DRC_COUNT 0' not in log:
        raise ValueError('Incomplete routed provenance')
    stages = {m[1]: dict(area_um2=float(m[2]), slew=int(m[3]), cap=int(m[4]), slack_ns=float(m[5])) for m in STAGE.finditer(log)}
    if not {'cts45_postcts_global', 'cts45_extracted', 'cts45_postcts_repaired'} <= stages.keys():
        raise ValueError('Missing timing stages')
    flops = {name: q.replace('\\', '') for name, q in FLOP.findall(net)}
    paths = []
    for m in PATH.finditer(log):
        cells = [(float(d), n, t) for d, n, t in CELL.findall(m[3])]
        if len(cells) < 8:
            raise ValueError('Malformed pre-CTS path')
        paths.append(dict(start=flops.get(m[1], m[1]), end=flops.get(m[2], m[2]),
                          reported_cells=len(cells), buffer_cells=sum(bool(re.match(r'(?:CLK)?BUF_', c[2])) for c in cells),
                          longest_buffer_chain=chain(cells)))
    if len(paths) != 2 or not all('staged_operand_data' in p['end'] for p in paths):
        raise ValueError('Unexpected pre-CTS path provenance')
    glob = stages['cts45_postcts_global']['slack_ns']
    extracted = stages['cts45_extracted']['slack_ns']
    if abs(extracted - {'pairwise': -.220829, 'serial_onehot': -.711405}[variant]) > 1e-6:
        raise ValueError('Extracted timing drift')
    return dict(sha256=digest, pre_CTS_paths=paths, post_CTS_global_slack_ns=glob,
                extracted_RC_worst_slack_ns=extracted, slack_change_ns=round(extracted-glob, 6),
                required_setup_improvement_ns=round(max(0, .05-extracted), 6),
                extracted_cap_violations=stages['cts45_extracted']['cap'],
                extracted_critical_path_available=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pairwise', type=Path)
    p.add_argument('--serial', type=Path)
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        assert chain([(.1, 'x', 'BUF_X1'), (.2, 'y', 'BUF_X2'), (.3, 'z', 'AND2_X1')])['count'] == 2
        try:
            audit(b'bad', 'pairwise')
        except ValueError:
            pass
        else:
            raise AssertionError('Accepted corrupt evidence')
        print('V296_PATH_BOUNDARY_SELFTEST_PASS')
    if a.pairwise or a.serial:
        if not a.pairwise or not a.serial:
            p.error('Both ZIPs required')
        result = {v: audit(f.read_bytes(), v) for v, f in [('pairwise', a.pairwise), ('serial_onehot', a.serial)]}
        print(json.dumps(dict(source_run=40427986118, evidence='ORIGINAL_SHA_PINNED_ARTIFACTS',
                              extracted_path_traces_missing=True, contestants=result), indent=2, sort_keys=True))
    elif not a.self_test:
        p.error('Supply ZIPs or --self-test')


if __name__ == '__main__':
    main()
