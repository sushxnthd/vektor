#!/usr/bin/env python3
"""Independent, fail-closed replay of V296's frozen density-0.35 routed test.

Inputs are original GitHub Actions artifact ZIPs, not the generated audit JSON.
A GitHub workflow success is NOT treated as physical-design success.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

EXPECTED = {
    'pairwise': 'c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7',
    'serial_onehot': '928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4',
}
GUARD = 0.050
BASE = {'pairwise': 12020, 'serial_onehot': 5281}

def one(blob, variant, enforce_hash=True):
    digest = hashlib.sha256(blob).hexdigest()
    if enforce_hash and digest != EXPECTED[variant]:
        raise ValueError('Original artifact ZIP SHA-256 mismatch: ' + variant)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        def read(name):
            return z.read(name).decode('utf-8')
        m = json.loads(read('density035_manifest.json'))
        if m['placement_density_trial'] != 0.35 or m['frozen_clock_ns'] != 3.5 or m['frozen_rc_multiplier'] != 2.0 or not m['serial_fifth_stage_control_repair_required']:
            raise ValueError('Frozen physical protocol mismatch')
        for path, key in [('run_bank_decode_density035.sh', 'trial_runner_sha256'),
                          ('cts45_tile_density035.tcl', 'diagnostic_guard_tcl_sha256')]:
            if hashlib.sha256(z.read(path)).hexdigest() != m[key]:
                raise ValueError('Modified physical input ' + path)
        if m['rtl_sha256'] + '  research/v296/v296_tile_slice_bank_decode.sv' not in read(f'{variant}.inputs.sha256'):
            raise ValueError('RTL provenance mismatch')
        log = read(f'{variant}.high.log')
        markers = [f'V296_CTS45_VARIANT {variant}',
                   f'V296_CTS45_EXTRA_REPAIR {1 if variant == "serial_onehot" else 0}',
                   'V296_CLOCK_PERIOD_NS 3.5', 'V296_PLACE_DENSITY 0.35',
                   'V296_CTS45_RC_MULTIPLIER 2.0', 'V296_CTS45_DRC_COUNT 0',
                   'V296_CTS45_IS_ROUTED 1', 'V296_CTS45_DONE']
        if any(log.splitlines().count(s) != 1 for s in markers):
            raise ValueError('Missing or duplicated physical signoff marker')
        if ('V296_CTS45_FIFTH_DONE' in log) != (variant == 'serial_onehot'):
            raise ValueError('Strong serial control repair provenance mismatch')
        if f'{variant}.high.cts45.spef' not in z.namelist() or not z.getinfo(f'{variant}.high.cts45.spef').file_size:
            raise ValueError('Missing extracted parasitics')
        def single(pattern):
            matches = re.findall(pattern, log, re.S)
            if len(matches) != 1:
                raise ValueError('Ambiguous extracted physical metric: ' + pattern)
            return matches[0]
        area, slew, cap, setup = single(r'V296_METRIC stage=cts45_extracted area_um2=([\d.]+) slew=(\d+) cap=(\d+)\s+worst slack\s+(-?[\d.]+)')
        hold = single(r'V296_CTS45_HOLD_BEGIN\s+worst slack\s+(-?[\d.]+)\s+V296_CTS45_HOLD_END')
        starts = re.split(r'\[INFO DRT-0195\] Start (\d+)(?:st|nd|rd|th) (?:optimization|stubborn tiles) iteration\.', log)
        iters = {}
        for i in range(1, len(starts), 2):
            values = re.findall(r'\[INFO DRT-0199\]\s+Number of violations = (\d+)\.', starts[i+1])
            if len(values) != 1:
                break
            k = int(starts[i])
            if k != len(iters):
                raise ValueError('Nonconsecutive routing iteration')
            iters[k] = int(values[0])
        if 3 not in iters:
            raise ValueError('Missing frozen routing checkpoint')
        cap_section = single(r'V296_CTS45_CAP_VIOLATORS_BEGIN\n(.*?)(?:\n)?V296_CTS45_CAP_VIOLATORS_END')
        if cap_section.count('(VIOLATED)') != int(cap):
            raise ValueError('Capacitance violator table does not match extracted count')
        if single(r'V296_CTS45_SLEW_VIOLATORS_BEGIN\n(.*?)V296_CTS45_SLEW_VIOLATORS_END').strip():
            raise ValueError('Unexpected slew violator listing')
        area, slew, cap, setup, hold = float(area), int(slew), int(cap), float(setup), float(hold)
        return dict(artifact_sha256=digest, area_um2=area, setup_ns=setup, hold_ns=hold,
                    cap_violations=cap, slew_violations=slew, drc=0, routed=True,
                    drc_at_iteration3=iters[3], drc_at_iteration4=iters.get(4),
                    feasible=area <= 30000 and setup >= GUARD and hold >= 0 and cap == 0 and slew == 0)

def evaluate(candidate, control):
    a, b = candidate['drc_at_iteration3'], control['drc_at_iteration3']
    ratio = (a * BASE['serial_onehot']) / (b * BASE['pairwise']) if b else None
    diagnostic_pass = a <= 8414 and ratio is not None and ratio <= 0.75
    return {'source_run': 40427986118, 'density035_checkpoint': 'FALSIFIED' if not diagnostic_pass else 'SUPPORTED_NOT_SIGNOFF',
            'checkpoint_ratio': ratio, 'candidate_only_drc_reduction': 1-a/BASE['pairwise'],
            'candidate': candidate, 'strong_serial_control': control,
            'candidate_setup_guard_shortfall_ns': max(0, GUARD-candidate['setup_ns']),
            'control_setup_guard_shortfall_ns': max(0, GUARD-control['setup_ns']),
            'candidate_area_saving_fraction': (control['area_um2']-candidate['area_um2'])/control['area_um2'],
            'candidate_extracted_setup_lead_ns': candidate['setup_ns']-control['setup_ns'],
            'physical_decision': 'DECODED_V296_DENSITY035_REPAIR_REJECTED' if not candidate['feasible'] else 'PHYSICAL_GATE_PASSED',
            'same_clock_gpu_speedup_established': False, 'workload_holdouts': 'SEALED'}

def self_test():
    c = {'drc_at_iteration3':3632,'area_um2':17213.9245080416,'setup_ns':-.220829,'feasible':False}
    s = {'drc_at_iteration3':2119,'area_um2':17994.89979248392,'setup_ns':-.711405,'feasible':False}
    result = evaluate(c,s)
    assert result['density035_checkpoint'] == 'FALSIFIED'
    assert abs(result['checkpoint_ratio']-.7530548032655972) < 1e-12
    assert result['physical_decision'] == 'DECODED_V296_DENSITY035_REPAIR_REJECTED'
    assert evaluate(dict(c,drc_at_iteration3=3000),s)['density035_checkpoint'] == 'SUPPORTED_NOT_SIGNOFF'
    print('V296_DENSITY035_INDEPENDENT_EXTRACTED_SELFTEST_PASS')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path)
    p.add_argument('--serial', type=Path)
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test: self_test()
    if a.candidate or a.serial:
        if not a.candidate or not a.serial: p.error('Both artifacts required')
        result = evaluate(one(a.candidate.read_bytes(),'pairwise'),one(a.serial.read_bytes(),'serial_onehot'))
        print(json.dumps(result,indent=2,sort_keys=True))
    elif not a.self_test: p.error('Provide both ZIPs or --self-test')
if __name__ == '__main__': main()
