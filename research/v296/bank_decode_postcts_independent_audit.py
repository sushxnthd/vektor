#!/usr/bin/env python3
"""Independent source/constraint provenance and physical-gate audit.

Never upgrades pre-CTS or incomplete routed evidence to a performance claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import audit_tile_slice

ROOT = Path('research/v296')
TOP = 'v296_tile_slice_bank_decode'
VARIANTS = ('pairwise', 'serial_onehot')


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def verify_provenance(folder, variant):
    if variant not in VARIANTS:
        raise ValueError('Unknown physical contestant')
    manifest = json.loads((folder / 'bank_decode_postcts_manifest.json').read_text())
    if manifest.get('rtl_top') != TOP or manifest.get('serial_fifth_stage_control_repair_required') is not True:
        raise ValueError('Wrong RTL or serial fifth-stage protocol')
    if manifest.get('frozen_clock_ns') != 3.5 or manifest.get('frozen_rc_multiplier') != 2.0:
        raise ValueError('Changed physical constraints')
    for filename, field in (('run_bank_decode_postcts.sh', 'derived_runner_sha256'),
                            ('cts45_tile.tcl', 'unchanged_generated_physical_tcl_sha256')):
        if sha_bytes((folder / filename).read_bytes()) != manifest[field]:
            raise ValueError('Mutated derived physical input: ' + filename)
    if sha_bytes((ROOT / (TOP + '.sv')).read_bytes()) != manifest['source_rtl_sha256']:
        raise ValueError('RTL source changed after physical generator')
    digest_lines = (folder / f'{variant}.inputs.sha256').read_text().splitlines()
    source = f'research/v296/{TOP}.sv'
    matched = [line.split() for line in digest_lines if line.endswith('  ' + source)]
    if len(matched) != 1 or matched[0][0] != manifest['source_rtl_sha256']:
        raise ValueError('Physical synthesis did not pin the decoded RTL')
    if any(line.endswith('  research/v296/v296_tile_slice.sv') for line in digest_lines):
        raise ValueError('Original unretimed RTL leaked into experiment')
    log = (folder / f'{variant}.high.log').read_text(errors='replace')
    required = 'V296_CTS45_EXTRA_REPAIR 1' if variant == 'serial_onehot' else 'V296_CTS45_EXTRA_REPAIR 0'
    if required not in log:
        raise ValueError('Missing strong serial-control repair or invalid candidate repair')
    if 'V296_CTS45_CLOCKS_PROPAGATED 1' not in log or 'V296_CTS45_RC_MULTIPLIER 2.0' not in log:
        raise ValueError('No propagated clock or extracted 2x RC evidence')
    return manifest


def audit(folder, variant):
    verify_provenance(folder, variant)
    row = audit_tile_slice.case(folder, variant)
    return {'variant': variant, 'source_provenance': 'PASS',
            'physical': row, 'physically_feasible': row.get('feasible', False)}


def aggregate(folder):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = audit(folder, variant)
        except (ValueError, OSError, KeyError, TypeError, IndexError) as e:
            rows[variant] = {'complete': False, 'error': str(e)}
    if not all(rows[v].get('physical', {}).get('complete') for v in VARIANTS):
        verdict = 'INCOMPLETE_NO_GPU_CLAIM'
    elif not all(rows[v]['physically_feasible'] for v in VARIANTS):
        verdict = 'BOTH_FEASIBLE_GATE_NOT_MET_NO_GPU_CLAIM'
    else:
        verdict = 'BOTH_SLICE_FEASIBLE_STILL_NOT_GPU_CLAIM'
    result = {'verdict': verdict, 'rows': rows, 'real_holdouts': 'SEALED',
              'measured_gpu_speedup': False, 'equal_consumed_area_tile': False,
              'measured_power': False, 'sram_macro_integration': False}
    (folder / 'aggregate.bank_decode_postcts.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'verdict': verdict,
                      'variants': {v: {'complete': bool(rows[v].get('physical', {}).get('complete')),
                                        'feasible': rows[v].get('physically_feasible', False),
                                        'error': rows[v].get('error')} for v in VARIANTS}}, indent=2))
    if verdict != 'BOTH_SLICE_FEASIBLE_STILL_NOT_GPU_CLAIM':
        raise SystemExit(3)


def self_test():
    assert sha_bytes(b'abc') == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    try:
        verify_provenance(Path('/does/not/exist'), 'fake')
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown contestant accepted')
    assert set(VARIANTS) == {'pairwise', 'serial_onehot'}
    print('V296_DECODED_POSTCTS_INDEPENDENT_AUDIT_SELFTEST_PASS')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--aggregate', type=Path)
    p.add_argument('--single', nargs=2)
    a = p.parse_args()
    if a.self_test: self_test()
    if a.single:
        print(json.dumps(audit(Path(a.single[0]), a.single[1]), indent=2))
    if a.aggregate: aggregate(a.aggregate)
    if not (a.self_test or a.single or a.aggregate): p.error('Select an audit mode')
