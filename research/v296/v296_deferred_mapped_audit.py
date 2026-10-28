#!/usr/bin/env python3
"""Fail-closed original-ZIP audit of V296 symmetric deferred-write mapped area.
Usage: python3 v296_deferred_mapped_audit.py --original-d4 ZIP --original-d8 ZIP --deferred-d4 ZIP --deferred-d8 ZIP [--output JSON].
Mapped evidence only: NOT STA, routed physical feasibility or GPU throughput.
"""
import argparse
import hashlib
import json
import re
import zipfile
from decimal import Decimal
from pathlib import Path

EXPECTED = {
    'original_d4': ('fe59053e653148616c35b2e1304d34ff9e200fe0ddd02b443ba6b8c2bcf68b20', '12960.584', '13835.990'),
    'original_d8': ('add9c2dcf6a85e6fd6bd5eaf63bee86c78bbc34e205c0b8d51378c612d9df8fb', '17552.542', '18782.260'),
    'deferred_d4': ('89d2bb353bc3bb1b292964a2fb26eb98f802ea48a3b936073d958d478307f335', '13044.906', '13510.406'),
    'deferred_d8': ('96e2c4409afd52fdb27151d072c12c90d3627fdc67094f10b851ab0496192e46', '18308.514', '18769.492'),
}


def inspect(path, key):
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED[key][0]:
        raise ValueError(f'{key}: immutable ZIP SHA mismatch')
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        def one(suffix):
            found = [n for n in names if n.endswith(suffix)]
            if len(found) != 1:
                raise ValueError(f'{key}: ambiguous or absent {suffix}')
            return z.read(found[0])
        version = one('yosys.version').decode().strip()
        lib = hashlib.sha256(one('nangate.lib')).hexdigest()
        manifest = one('source_library.sha256').decode()
        hashes = {}
        for line in manifest.splitlines():
            sha, filename = line.split(maxsplit=1)
            hashes[Path(filename).name] = sha
        if lib != hashes.get('nangate.lib'):
            raise ValueError(f'{key}: library hash mismatch')
        result = dict(sha256=digest, yosys=version, library_sha256=lib,
                      issue_sha256=hashes.get('v296_issue_core.sv'),
                      serial_sha256=hashes.get('v295_issue_core.sv'),
                      rtl_sha256=hashes.get('v296_tile_slice_deep_bank.sv') or
                                 hashes.get('v296_tile_slice_deferred_write.sv'))
        for name in ('pairwise', 'serial'):
            log = one(f'_{name}.log').decode(errors='replace')
            if 'ERROR:' in log or 'Chip area for module' not in log:
                raise ValueError(f'{key}/{name}: synthesis failure')
            areas = re.findall(r'Chip area for module.*?:\s*([0-9.]+)', log)
            if len(areas) != 1:
                raise ValueError(f'{key}/{name}: ambiguous mapped area')
            result[name] = Decimal(areas[0])
        if (result['pairwise'], result['serial']) != tuple(Decimal(v) for v in EXPECTED[key][1:]):
            raise ValueError(f'{key}: unexpected mapped results')
        return result


def audit(paths):
    rows = {key: inspect(paths[key], key) for key in EXPECTED}
    controls = ('yosys', 'library_sha256', 'issue_sha256', 'serial_sha256')
    for control in controls:
        values = {row[control] for row in rows.values()}
        if len(values) != 1 or None in values:
            raise ValueError(f'matched tool/library/control mismatch: {control}')
    result = dict(evidence_tier='SHA-verified Yosys/Nangate45 mapped area only; NOT STA/physical signoff',
                  controls={k: rows['original_d4'][k] for k in controls},
                  depth_results={}, physically_feasible=False, gpu_speedup=False)
    for d in (4, 8):
        old = rows[f'original_d{d}']
        new = rows[f'deferred_d{d}']
        old_margin = old['serial'] - old['pairwise']
        new_margin = new['serial'] - new['pairwise']
        if new_margin <= 0:
            raise ValueError(f'depth {d}: deferred design lost mapped area ordering')
        result['depth_results'][str(d)] = {
            'original_pairwise_um2': str(old['pairwise']),
            'original_serial_um2': str(old['serial']),
            'original_margin_um2': str(old_margin),
            'deferred_pairwise_um2': str(new['pairwise']),
            'deferred_serial_um2': str(new['serial']),
            'deferred_margin_um2': str(new_margin),
            'deferred_margin_percent_of_serial': float(new_margin / new['serial'] * 100),
            'margin_eroded_percent': float((old_margin-new_margin)/old_margin*100),
            'pairwise_area_delta_um2': str(new['pairwise']-old['pairwise']),
            'serial_area_delta_um2': str(new['serial']-old['serial']),
            'original_artifact_sha256': old['sha256'],
            'deferred_artifact_sha256': new['sha256'],
        }
    return result


def main():
    p = argparse.ArgumentParser()
    for key in EXPECTED:
        p.add_argument('--'+key.replace('_', '-'), required=True)
    p.add_argument('--output')
    a = p.parse_args()
    result = audit({k: getattr(a, k) for k in EXPECTED})
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.output:
        Path(a.output).write_text(payload)
    else:
        print(payload)


if __name__ == '__main__':
    main()
