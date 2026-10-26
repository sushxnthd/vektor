#!/usr/bin/env python3
"""SHA-pinned independent DRC-convergence audit; candidate timeout is censored."""
import argparse
import hashlib
import json
import re
import zipfile
from decimal import Decimal
from pathlib import Path

SHA = {
    'pairwise': '34fc90009fdb35954e66b8e87065404721fa3679adc834a22c24b69fc095a295',
    'serial_onehot': '36c9ce00caadf2416082510a6b9a84cbbd5c8a4b26dce646b7ecb19ed7682713',
}
START = re.compile(r'\[INFO DRT-0195\] Start (\d+)(?:st|nd|rd|th) (?:optimization|stubborn tiles) iteration\.')
VIOL = re.compile(r'\[INFO DRT-0199\]\s+Number of violations = (\d+)\.')
WIRE = re.compile(r'Total wire length = (\d+) um\.')
VIA = re.compile(r'Total number of vias = (\d+)\.')


def read(path, variant):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA[variant]:
        raise ValueError('Original ZIP SHA256 mismatch: ' + variant)
    with zipfile.ZipFile(path) as z:
        m = json.loads(z.read('bank_decode_postcts_manifest.json'))
        if (m['frozen_clock_ns'], m['frozen_rc_multiplier'], m['rtl_top']) != (3.5, 2.0, 'v296_tile_slice_bank_decode'):
            raise ValueError('Frozen physical constraints or top changed')
        if m['serial_fifth_stage_control_repair_required'] is not True:
            raise ValueError('Missing strong serial control')
        for name, key in [('cts45_tile.tcl', 'unchanged_generated_physical_tcl_sha256'),
                          ('run_bank_decode_postcts.sh', 'derived_runner_sha256')]:
            if hashlib.sha256(z.read(name)).hexdigest() != m[key]:
                raise ValueError('Mutated physical input: ' + name)
        if m['source_rtl_sha256'] + '  research/v296/v296_tile_slice_bank_decode.sv' not in z.read(variant + '.inputs.sha256').decode():
            raise ValueError('Unpinned decoded RTL')
        log = z.read(variant + '.high.log').decode(errors='replace')
    extra = '1' if variant == 'serial_onehot' else '0'
    for marker in ['V296_CTS45_EXTRA_REPAIR ' + extra, 'V296_CTS45_CLOCKS_PROPAGATED 1', 'V296_CTS45_DETAIL_BEGIN']:
        if marker not in log:
            raise ValueError('Missing physical provenance: ' + marker)
    chunks = START.split(log)
    rows = []
    for i in range(1, len(chunks), 2):
        k, segment = int(chunks[i]), chunks[i+1]
        v, w, n = VIOL.findall(segment), WIRE.findall(segment), VIA.findall(segment)
        if rows and k != rows[-1]['iteration'] + 1:
            raise ValueError('Missing route iteration')
        if not v:
            rows.append({'iteration': k, 'complete': False})
            break
        if len(v) != 1 or not w or not n:
            raise ValueError('Incomplete route iteration')
        short = re.search(r'^\s*Short\s+([\d\s]+)$', segment, re.M)
        if not short and int(v[0]) != 0:
            raise ValueError('Missing layer-level shorts')
        counts = list(map(int, short.group(1).split())) if short else [0]*5
        if len(counts) < 5 and k <= 8:
            raise ValueError('Incomplete layer-level shorts at frozen checkpoint')
        counts += [0] * max(0, 5-len(counts))
        rows.append({'iteration': k, 'complete': True, 'drc': int(v[0]),
                     'wire_um': int(w[0]), 'vias': int(n[0]),
                     'metal2_metal3_shorts': counts[2] + counts[4]})
    if not rows or rows[0].get('drc') is None:
        raise ValueError('No completed route evidence')
    return {'rows': rows, 'source': m['source_rtl_sha256'],
            'extracted': 'V296_CTS45_DONE' in log and 'V296_CTS45_RC_MULTIPLIER 2.0' in log}


def evaluate(pair, serial):
    a, b = read(pair, 'pairwise'), read(serial, 'serial_onehot')
    if a['source'] != b['source'] or a['extracted'] or not b['extracted']:
        raise ValueError('Wrong source or censoring status')
    ar = {r['iteration']: r for r in a['rows'] if r['complete']}
    br = {r['iteration']: r for r in b['rows'] if r['complete']}
    if any(i not in ar or i not in br for i in range(9)):
        raise ValueError('Frozen iteration 0..8 not complete')
    x, y = ar[8], br[8]
    d = Decimal
    return {'run_id': 40359299905, 'checkpoint_iteration': 8,
            'candidate_drc': x['drc'], 'serial_drc': y['drc'],
            'drc_ratio': str(d(x['drc']) / d(y['drc'])),
            'candidate_drc_reduction_pct': str(100*(1-d(x['drc'])/d(ar[0]['drc']))),
            'serial_drc_reduction_pct': str(100*(1-d(y['drc'])/d(br[0]['drc']))),
            'candidate_wire_um': x['wire_um'], 'serial_wire_um': y['wire_um'],
            'candidate_wire_saving_pct': str(100*(1-d(x['wire_um'])/d(y['wire_um']))),
            'candidate_metal2_metal3_shorts': x['metal2_metal3_shorts'],
            'serial_metal2_metal3_shorts': y['metal2_metal3_shorts'],
            'candidate_extracted_rc': False, 'serial_extracted_rc': True,
            'verdict': 'CENSORED_CANDIDATE_ROUTING_NO_GPU_CLAIM',
            'original_zip_sha256': SHA,
            'candidate_iterations': a['rows'], 'serial_iterations': b['rows']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pairwise', type=Path)
    p.add_argument('--serial', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        assert VIOL.findall('[INFO DRT-0199]   Number of violations = 7930.') == ['7930']
        assert START.findall('[INFO DRT-0195] Start 18th stubborn tiles iteration.') == ['18']
        assert hashlib.sha256(b'altered ZIP').hexdigest() != SHA['pairwise']
        print('V296_CENSORED_ROUTE_AUDIT_SELFTEST_PASS')
    if a.pairwise or a.serial:
        if not (a.pairwise and a.serial):
            p.error('Both original ZIPs required')
        result = json.dumps(evaluate(a.pairwise, a.serial), indent=2) + '\n'
        if a.output: a.output.write_text(result)
        print(result)
    elif not a.self_test:
        p.error('Provide --self-test or both ZIPs')

if __name__ == '__main__':
    main()
