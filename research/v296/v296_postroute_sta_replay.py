#!/usr/bin/env python3
"""Fail-closed, read-only STA reconstruction from frozen routed DEF and extracted SPEF.

No rerouting, resizing, or re-extraction is performed. This is a diagnostic,
not a new physical design or proof of signoff.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ORIGINAL = {
    'pairwise': {'zip_sha256': 'c0d90c6652deba498c46e6b01e9d3e1ce0317505caf833eea51323b54e6f49a7',
                 'setup_ns': -0.220829, 'hold_ns': -0.010023, 'artifact_id': 12703514184},
    'serial_onehot': {'zip_sha256': '928adb671004dea251dc9c1c558f87a34fc3d3ff233e66d41ddd311d3d305ea4',
                      'setup_ns': -0.711405, 'hold_ns': -0.013032, 'artifact_id': 12703682763},
}
TOL_NS = 0.001  # 1 ps; no post-hoc widening
TCL = r'''# Read-only reconstructed STA, NOT a new route or timing repair.
foreach k {V296_REPLAY_ROOT V296_REPLAY_VARIANT V296_LIB V296_TECH_LEF V296_CELL_LEF} {
  if {![info exists env($k)]} { error "Missing replay input $k" }
}
set root $env(V296_REPLAY_ROOT)
set variant $env(V296_REPLAY_VARIANT)
if {$variant ni {pairwise serial_onehot}} { error "Invalid variant" }
set def "$root/$variant.high.cts45.def"
set spef "$root/$variant.high.cts45.spef"
foreach f [list $def $spef $env(V296_LIB) $env(V296_TECH_LEF) $env(V296_CELL_LEF)] {
  if {![file isfile $f]} { error "Missing replay input $f" }
}
read_lef $env(V296_TECH_LEF)
read_lef $env(V296_CELL_LEF)
read_liberty $env(V296_LIB)
read_def $def
create_clock -name coreclk -period 3.5 [get_ports clk]
set_input_delay -clock coreclk 0.15 [all_inputs -no_clocks]
set_output_delay -clock coreclk 0.15 [all_outputs]
set_input_transition 0.04 [all_inputs -no_clocks]
set_load 0.005 [all_outputs]
set_max_transition 0.25 [current_design]
set_max_fanout 16 [current_design]
set_false_path -from [get_ports rst_n]
set_propagated_clock [all_clocks]
if {![check_setup]} { error "Unconstrained reconstructed timing" }
# The original SPEF was extracted and then scaled by 2x R/CC/GND C
# BEFORE write_spef; DO NOT apply another adjust_rc here.
read_spef $spef
puts "V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION"
puts "V296_REPLAY_SETUP_WORST_BEGIN"
report_worst_slack -max -digits 6
puts "V296_REPLAY_SETUP_WORST_END"
puts "V296_REPLAY_HOLD_WORST_BEGIN"
report_worst_slack -min -digits 6
puts "V296_REPLAY_HOLD_WORST_END"
puts "V296_REPLAY_SETUP_PATHS_BEGIN"
report_checks -path_delay max -group_path_count 10 -fields {slew capacitance fanout} -digits 6
puts "V296_REPLAY_SETUP_PATHS_END"
puts "V296_REPLAY_HOLD_PATHS_BEGIN"
report_checks -path_delay min -group_path_count 10 -fields {slew capacitance fanout} -digits 6
puts "V296_REPLAY_HOLD_PATHS_END"
puts "V296_REPLAY_DONE"
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def generate(dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(TCL)
    print(json.dumps({'probe_sha256': sha(TCL.encode()), 'probe': str(dest),
                      'evidence_tier': 'RECONSTRUCTED_POSTROUTE_STA_NOT_NEW_ROUTE'}, sort_keys=True))


def block(log, name):
    a, b = f'V296_REPLAY_{name}_BEGIN', f'V296_REPLAY_{name}_END'
    if log.splitlines().count(a) != 1 or log.splitlines().count(b) != 1:
        raise ValueError('Missing or duplicated markers: ' + name)
    return log.split(a, 1)[1].split(b, 1)[0]


def worst(text):
    m = re.findall(r'^worst slack\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s*$', text, re.M)
    if len(m) != 1:
        raise ValueError('Missing or ambiguous worst slack')
    value = float(m[0])
    if not math.isfinite(value):
        raise ValueError('Nonfinite worst slack')
    return value


def paths(text):
    pieces = re.split(r'(?=^Startpoint:\s*)', text, flags=re.M)
    rows = []
    for p in pieces:
        if not p.startswith('Startpoint:'):
            continue
        start = re.search(r'^Startpoint:\s*(.+)$', p, re.M)
        end = re.search(r'^Endpoint:\s*(.+)$', p, re.M)
        slack = re.findall(r'^\s*slack\s+(?:\([^)]*\)\s+)?(-?(?:\d+(?:\.\d*)?|\.\d+))\s*$', p, re.M)
        if not start or not end or len(slack) != 1:
            raise ValueError('Incomplete extracted path report')
        rows.append({'start': start[1].strip(), 'end': end[1].strip(), 'slack_ns': float(slack[0])})
    if not rows:
        raise ValueError('No named paths')
    return rows


def audit(log, variant):
    if variant not in ORIGINAL:
        raise ValueError('Unknown variant')
    if log.splitlines().count('V296_REPLAY_DONE') != 1:
        raise ValueError('Incomplete replay')
    if log.splitlines().count('V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION') != 1:
        raise ValueError('Missing evidence tier')
    s = worst(block(log, 'SETUP_WORST'))
    h = worst(block(log, 'HOLD_WORST'))
    setup_paths = paths(block(log, 'SETUP_PATHS'))
    hold_paths = paths(block(log, 'HOLD_PATHS'))
    if abs(setup_paths[0]['slack_ns'] - s) > TOL_NS or abs(hold_paths[0]['slack_ns'] - h) > TOL_NS:
        raise ValueError('Reported path not the measured worst path')
    original = ORIGINAL[variant]
    if abs(s - original['setup_ns']) > TOL_NS or abs(h - original['hold_ns']) > TOL_NS:
        raise ValueError(f'Reconstructed STA does not reproduce original routed slacks: setup {s}, hold {h}')
    return {'decision': 'POSTROUTE_REPLAY_REPRODUCED', 'variant': variant,
            'source_run': 40427986118, 'original_artifact_id': original['artifact_id'],
            'original_zip_sha256': original['zip_sha256'], 'replay_log_sha256': sha(log.encode()),
            'setup_ns': s, 'hold_ns': h, 'setup_paths': setup_paths,
            'hold_paths': hold_paths, 'physically_feasible': False,
            'new_route_or_timing_repair': False, 'gpu_speedup_claim': False}


def self_test():
    sample = ('V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION\n'
              'V296_REPLAY_SETUP_WORST_BEGIN\nworst slack -0.220829\nV296_REPLAY_SETUP_WORST_END\n'
              'V296_REPLAY_HOLD_WORST_BEGIN\nworst slack -0.010023\nV296_REPLAY_HOLD_WORST_END\n'
              'V296_REPLAY_SETUP_PATHS_BEGIN\nStartpoint: a/Q\nEndpoint: b/D\n'
              'slack (VIOLATED) -0.220829\nV296_REPLAY_SETUP_PATHS_END\n'
              'V296_REPLAY_HOLD_PATHS_BEGIN\nStartpoint: c/Q\nEndpoint: d/D\n'
              'slack (VIOLATED) -0.010023\nV296_REPLAY_HOLD_PATHS_END\nV296_REPLAY_DONE\n')
    assert audit(sample, 'pairwise')['decision'] == 'POSTROUTE_REPLAY_REPRODUCED'
    for bad in (sample.replace('V296_REPLAY_DONE', ''), sample.replace('-0.220829', '-0.120829'),
                sample.replace('Endpoint: b/D', ''), sample.replace('V296_REPLAY_SETUP_PATHS_END', '')):
        try:
            audit(bad, 'pairwise')
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid replay accepted')
    assert 'adjust_rc ' not in '\n'.join(line for line in TCL.splitlines() if not line.startswith('#'))
    assert 'detailed_route ' not in TCL
    print('V296_POSTROUTE_STA_REPLAY_SELFTEST_PASS')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--generate', type=Path)
    p.add_argument('--audit-log', type=Path)
    p.add_argument('--variant', choices=tuple(ORIGINAL))
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.generate:
        generate(a.generate)
    if a.audit_log:
        if not a.variant:
            p.error('--variant required with --audit-log')
        try:
            result = audit(a.audit_log.read_text(errors='replace'), a.variant)
        except (ValueError, OSError) as exc:
            result = {'decision': 'INCOMPLETE_NO_EXTRACTED_PATH_CLAIM', 'variant': a.variant,
                      'error': str(exc), 'gpu_speedup_claim': False}
        output = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if a.output:
            a.output.write_text(output)
        print(output)
        if result['decision'] != 'POSTROUTE_REPLAY_REPRODUCED':
            raise SystemExit(3)
    if not (a.self_test or a.generate or a.audit_log):
        p.error('Select an action')


if __name__ == '__main__':
    main()
