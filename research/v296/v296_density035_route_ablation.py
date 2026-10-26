#!/usr/bin/env python3
"""Preregistered symmetric placement-density route ablation, diagnostic only.

This is NOT a physical signoff or a change to V296's architectural mechanism.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

OUT = Path('build/v296/tile_slice')
ROOT = Path('research/v296')
BASE = 'run_bank_decode_postcts.sh'
TRIAL = 'run_bank_decode_density035.sh'
ORIGINAL_TCL = 'cts45_tile.tcl'
TRIAL_TCL = 'cts45_tile_density035.tcl'
TCL_ANCHOR = '"$root/cts45_tile.tcl"'
TCL_CHANGE = '"$root/cts45_tile_density035.tcl"'
GUARD_OLD = '$env(V296_PLACE_DENSITY) ne "0.45"'
GUARD_NEW = '$env(V296_PLACE_DENSITY) ne "0.35"'
MESSAGE_OLD = 'CTS45 frozen high-RC 2x and placement density 0.45'
MESSAGE_NEW = 'CTS45 frozen high-RC 2x and placement density 0.35'
MANIFEST = 'density035_manifest.json'
ANCHOR = 'V296_PLACE_DENSITY=0.45'
CHANGE = 'V296_PLACE_DENSITY=0.35'
BASELINE = {3: {'pairwise': 12020, 'serial_onehot': 5281},
            4: {'pairwise': 10441, 'serial_onehot': 3083}}
START = re.compile(r'\[INFO DRT-0195\] Start (\d+)(?:st|nd|rd|th) (?:optimization|stubborn tiles) iteration\.')
VIOL = re.compile(r'\[INFO DRT-0199\]\s+Number of violations = (\d+)\.')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def derive_tcl(text):
    """Change only the assertion that checks the trial density; never physical commands."""
    if text.count(GUARD_OLD) != 1 or text.count(MESSAGE_OLD) != 1:
        raise ValueError('Frozen CTS density guard absent or ambiguous')
    if GUARD_NEW in text or MESSAGE_NEW in text:
        raise ValueError('CTS density guard already modified')
    changed = text.replace(GUARD_OLD, GUARD_NEW).replace(MESSAGE_OLD, MESSAGE_NEW)
    if changed.replace(GUARD_NEW, GUARD_OLD).replace(MESSAGE_NEW, MESSAGE_OLD) != text:
        raise ValueError('CTS guard-only derivation failed')
    return changed


def derive(text):
    if text.count(ANCHOR) != 1 or CHANGE in text:
        raise ValueError('Original 0.45 placement-density anchor absent or ambiguous')
    if text.count(TCL_ANCHOR) != 1 or TCL_CHANGE in text:
        raise ValueError('Original physical Tcl invocation absent or ambiguous')
    if 'serial_onehot) param=0; extra=1' not in text:
        raise ValueError('Independently repaired fifth-stage serial control missing')
    changed = text.replace(ANCHOR, CHANGE).replace(TCL_ANCHOR, TCL_CHANGE)
    if changed.replace(CHANGE, ANCHOR).replace(TCL_CHANGE, TCL_ANCHOR) != text:
        raise ValueError('Runner differs by more than density and separate diagnostic Tcl path')
    return changed


def build():
    import bank_decode_postcts_flow
    bank_decode_postcts_flow.build()
    original = (OUT / BASE).read_bytes()
    trial = derive(original.decode()).encode()
    (OUT / TRIAL).write_bytes(trial)
    original_tcl = (OUT / ORIGINAL_TCL).read_bytes()
    trial_tcl = derive_tcl(original_tcl.decode()).encode()
    (OUT / TRIAL_TCL).write_bytes(trial_tcl)
    parent = json.loads((OUT / 'bank_decode_postcts_manifest.json').read_text())
    assert sha(original) == parent['derived_runner_sha256']
    assert sha((OUT / 'cts45_tile.tcl').read_bytes()) == parent['unchanged_generated_physical_tcl_sha256']
    data = {
        'experiment': 'V296_SYMMETRIC_DENSITY035_ROUTING_DIAGNOSTIC_ONLY',
        'baseline_run_id': 40359299905,
        'baseline_pairwise_zip_sha256': '34fc90009fdb35954e66b8e87065404721fa3679adc834a22c24b69fc095a295',
        'baseline_serial_zip_sha256': '36c9ce00caadf2416082510a6b9a84cbbd5c8a4b26dce646b7ecb19ed7682713',
        'placement_density_original': 0.45,
        'placement_density_trial': 0.35,
        'same_trial_for_both': True,
        'original_runner_sha256': sha(original),
        'trial_runner_sha256': sha(trial),
        'physical_tcl_sha256': sha(original_tcl),
        'diagnostic_guard_tcl_sha256': sha(trial_tcl),
        'tcl_guard_only_change': True,
        'execution_amendment': 'research/v296/DENSITY035_EXECUTION_BLOCKER_AND_GUARD_REPAIR_20261027.md',
        'rtl_sha256': parent['source_rtl_sha256'],
        'frozen_clock_ns': parent['frozen_clock_ns'],
        'frozen_rc_multiplier': parent['frozen_rc_multiplier'],
        'serial_fifth_stage_control_repair_required': True,
        'real_workload_holdouts': 'SEALED',
        'physical_signoff_claim': False,
    }
    (OUT / MANIFEST).write_text(json.dumps(data, indent=2) + '\n')
    print('V296_DENSITY035_DIAGNOSTIC_BUILT')


def iterations(log):
    chunks = START.split(log)
    rows = {}
    for i in range(1, len(chunks), 2):
        index = int(chunks[i])
        found = VIOL.findall(chunks[i+1])
        if not found:
            break  # right-censored iteration, not a zero-DRC result
        if len(found) != 1 or index != len(rows):
            raise ValueError('Ambiguous or nonconsecutive detailed-route trajectory')
        rows[index] = int(found[0])
    return rows


def verdict(pairwise, serial):
    if 3 not in pairwise or 3 not in serial:
        return {'verdict': 'INCOMPLETE_EARLY_ROUTE_NO_CLAIM', 'checkpoint': None}
    b = BASELINE[3]
    cand_reduction = 1 - pairwise[3] / b['pairwise']
    relative_ratio = ((pairwise[3] / serial[3]) /
                      (b['pairwise'] / b['serial_onehot'])) if serial[3] else float('inf')
    passed = cand_reduction >= 0.30 and relative_ratio <= 0.75
    return {'verdict': 'DENSITY_DIAGNOSTIC_SUPPORTED_NOT_SIGNOFF' if passed else 'DENSITY_DIAGNOSTIC_FALSIFIED',
            'checkpoint': 3, 'candidate_drc_reduction': cand_reduction,
            'candidate_to_serial_ratio_relative_to_original': relative_ratio,
            'candidate_drc': pairwise[3], 'serial_drc': serial[3],
            'iteration4_exploratory': {'pairwise': pairwise.get(4), 'serial_onehot': serial.get(4)},
            'physically_feasible': False, 'gpu_speedup_claim': False}


def audit(folder):
    m = json.loads((folder / MANIFEST).read_text())
    for name, key in ((BASE, 'original_runner_sha256'), (TRIAL, 'trial_runner_sha256'),
                      (ORIGINAL_TCL, 'physical_tcl_sha256'),
                      (TRIAL_TCL, 'diagnostic_guard_tcl_sha256')):
        if sha((folder / name).read_bytes()) != m[key]:
            raise ValueError('Physical input hash mismatch: ' + name)
    if (derive((folder / BASE).read_text()).encode() != (folder / TRIAL).read_bytes() or
            derive_tcl((folder / ORIGINAL_TCL).read_text()).encode() != (folder / TRIAL_TCL).read_bytes() or
            m.get('tcl_guard_only_change') is not True or
            m['placement_density_original'] != 0.45 or m['placement_density_trial'] != 0.35 or
            m['frozen_clock_ns'] != 3.5 or m['frozen_rc_multiplier'] != 2.0 or
            m['same_trial_for_both'] is not True or
            m['serial_fifth_stage_control_repair_required'] is not True):
        raise ValueError('Protocol drift')
    rows = {}
    for variant, extra in (('pairwise', '0'), ('serial_onehot', '1')):
        log = (folder / f'{variant}.high.log').read_text(errors='replace')
        if f'V296_CTS45_EXTRA_REPAIR {extra}' not in log:
            raise ValueError('Missing fifth-stage serial control marker: ' + variant)
        lines = (folder / f'{variant}.inputs.sha256').read_text()
        if m['rtl_sha256'] + '  research/v296/v296_tile_slice_bank_decode.sv' not in lines:
            raise ValueError('Source provenance missing: ' + variant)
        rows[variant] = iterations(log)
    result = verdict(rows['pairwise'], rows['serial_onehot'])
    result.update({'trial': 'density035', 'baseline': 'density045_original_pinned',
                   'trajectories': rows, 'no_extracted_rc_or_clock_claim': True,
                   'original_artifact_sha256': {'pairwise': m['baseline_pairwise_zip_sha256'],
                                                'serial_onehot': m['baseline_serial_zip_sha256']}})
    (folder / 'density035_result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


def self_test():
    example = 'serial_onehot) param=0; extra=1\\nV296_PLACE_DENSITY=0.45\\n"$root/cts45_tile.tcl"\\n'
    assert derive(example).replace(CHANGE, ANCHOR).replace(TCL_CHANGE, TCL_ANCHOR) == example
    original_tcl = 'if {$env(V296_PLACE_DENSITY) ne "0.45"} {\\n  error "CTS45 frozen high-RC 2x and placement density 0.45"\\n}\\n'
    assert derive_tcl(original_tcl).replace(GUARD_NEW, GUARD_OLD).replace(MESSAGE_NEW, MESSAGE_OLD) == original_tcl
    for bad_tcl in (original_tcl + GUARD_OLD, original_tcl.replace(GUARD_OLD, GUARD_NEW), original_tcl.replace(MESSAGE_OLD, 'missing')):
        try: derive_tcl(bad_tcl)
        except ValueError: pass
        else: raise AssertionError('Invalid density guard accepted')
    for broken in (example + ANCHOR, example.replace(ANCHOR, CHANGE), example.replace('extra=1', 'extra=0'), example.replace(TCL_ANCHOR, TCL_CHANGE)):
        try: derive(broken)
        except ValueError: pass
        else: raise AssertionError('Protocol mutation not rejected')
    synthetic = ''.join(f'[INFO DRT-0195] Start {i}th optimization iteration.\n[INFO DRT-0199] Number of violations = {9000-i}.\n' for i in range(4))
    assert iterations(synthetic)[3] == 8997
    assert verdict({3: 7000}, {3: 4500})['verdict'] == 'DENSITY_DIAGNOSTIC_SUPPORTED_NOT_SIGNOFF'
    assert verdict({3: 12020}, {3: 5281})['verdict'] == 'DENSITY_DIAGNOSTIC_FALSIFIED'
    assert verdict({2: 1000}, {2: 1000})['verdict'] == 'INCOMPLETE_EARLY_ROUTE_NO_CLAIM'
    print('V296_DENSITY035_DIAGNOSTIC_SELFTEST_PASS')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--build', action='store_true')
    p.add_argument('--audit', type=Path)
    a = p.parse_args()
    if a.self_test: self_test()
    if a.build: build()
    if a.audit:
        result = audit(a.audit)
        if result['verdict'] == 'INCOMPLETE_EARLY_ROUTE_NO_CLAIM': sys.exit(3)
    if not (a.self_test or a.build or a.audit): p.error('Select a mode')
