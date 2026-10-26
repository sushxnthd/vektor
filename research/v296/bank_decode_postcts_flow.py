#!/usr/bin/env python3
"""Fail-closed, symmetric decoded V296 post-CTS extracted-RC experiment.

Only the integrated RTL module/source is replaced. The frozen CTS, control-
advantaged fifth repair, routing, RC, and independent physical audit are reused.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path('research/v296')
OUT = Path('build/v296/tile_slice')
OLD = 'v296_tile_slice'
NEW = 'v296_tile_slice_bank_decode'
SRC_RUNNER = ROOT / 'run_tile_slice_cts.sh'
FROZEN_TCL = 'cts45_tile.tcl'


def digest(data):
    return hashlib.sha256(data.encode()).hexdigest()


def replace_count(text, old, new, count):
    found = text.count(old)
    if found != count:
        raise ValueError(f'Unsafe anchor {old!r}: expected {count}, found {found}')
    return text.replace(old, new)


def derive(runner, cts):
    # Replace the RTL path and three exact top references, NOT the output path,
    # audit implementation, floorplan or physical Tcl.
    out = replace_count(runner, f'research/v296/{OLD}.sv',
                        f'research/v296/{NEW}.sv', 2)
    out = replace_count(out, f'hierarchy -top {OLD} -chparam PAIRWISE',
                        f'hierarchy -top {NEW} -chparam PAIRWISE', 1)
    out = replace_count(out, f'synth -top {OLD} -flatten',
                        f'synth -top {NEW} -flatten', 1)
    out = replace_count(out, f'V296_TOP="{OLD}"', f'V296_TOP="{NEW}"', 1)
    out = replace_count(out, 'echo "TILE_SLICE_POSTCTS_EXTRACTED_COMPLETE $variant"',
                        'echo "V296_DECODED_POSTCTS_EXTRACTED_COMPLETE $variant"', 1)
    if f'research/v296/{OLD}.sv' in out or f'V296_TOP="{OLD}"' in out:
        raise ValueError('Original top leaked into derived physical runner')
    if out.count('python3 research/v296/audit_tile_slice.py --single') != 1:
        raise ValueError('Missing independent physical audit')
    if 'serial_onehot) param=0; extra=1' not in out or 'V296_CONTROL_EXTRA="$extra"' not in out:
        raise ValueError('Strong serial fifth-stage repair not retained')
    for token in ('clock_tree_synthesis', 'detailed_route -output_drc',
                  'extract_parasitics -ext_model_file',
                  'adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0',
                  'if {$env(V296_CONTROL_EXTRA) eq "1"}',
                  'repair_timing -setup -slack_margin 0.250',
                  'set_max_fanout 16 [current_design]'):
        if token not in cts:
            raise ValueError('Missing frozen physical or strong-control policy: ' + token)
    if 'source build/v296/tile_slice/cap_margin_third_tile.tcl' not in cts:
        raise ValueError('Integrated floorplan source absent')
    return out


def build():
    import tile_slice_flow
    tile_slice_flow.build()
    runner = SRC_RUNNER.read_text()
    cts = (OUT / FROZEN_TCL).read_text()
    transformed = derive(runner, cts)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'run_bank_decode_postcts.sh').write_text(transformed)
    manifest = {
        'tier': 'POSTCTS_DETAILED_ROUTE_EXTRACTED_RC_PENDING',
        'preregistration': 'research/v296/BANK_DECODE_POSTCTS_PREREG_20261026.md',
        'rtl_top': NEW,
        'same_rtl_intervention_for_both': True,
        'serial_fifth_stage_control_repair_required': True,
        'frozen_clock_ns': 3.5,
        'frozen_rc_multiplier': 2.0,
        'source_runner_sha256': digest(runner),
        'derived_runner_sha256': digest(transformed),
        'unchanged_generated_physical_tcl_sha256': digest(cts),
        'source_rtl_sha256': hashlib.sha256((ROOT / (NEW + '.sv')).read_bytes()).hexdigest(),
        'no_gpu_speedup_without_both_feasible': True,
        'real_workload_holdouts': 'SEALED',
    }
    (OUT / 'bank_decode_postcts_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('V296_DECODED_POSTCTS_STRONG_CONTROL_GENERATED')


def self_test():
    runner = ('sha256sum research/v296/v296_tile_slice.sv\n'
              'src="research/v296/v296_tile_slice.sv"\n'
              'hierarchy -top v296_tile_slice -chparam PAIRWISE\n'
              'synth -top v296_tile_slice -flatten\n'
              'V296_TOP="v296_tile_slice"\n'
              'serial_onehot) param=0; extra=1 ;;\n'
              'V296_CONTROL_EXTRA="$extra"\n'
              'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?\n'
              'echo "TILE_SLICE_POSTCTS_EXTRACTED_COMPLETE $variant"\n')
    cts = ('source build/v296/tile_slice/cap_margin_third_tile.tcl\n'
           'clock_tree_synthesis\n'
           'detailed_route -output_drc\n'
           'extract_parasitics -ext_model_file\n'
           'adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0\n'
           'if {$env(V296_CONTROL_EXTRA) eq "1"}\n'
           'repair_timing -setup -slack_margin 0.250\n'
           'set_max_fanout 16 [current_design]\n')
    transformed = derive(runner, cts)
    assert transformed.count('research/v296/v296_tile_slice_bank_decode.sv') == 2
    assert 'hierarchy -top v296_tile_slice_bank_decode' in transformed
    assert 'V296_TOP="v296_tile_slice_bank_decode"' in transformed
    assert 'serial_onehot) param=0; extra=1' in transformed
    for a, b in ((runner.replace('extra=1', 'extra=0'), cts),
                 (runner, cts.replace('clock_tree_synthesis', '')),
                 (runner + 'synth -top v296_tile_slice -flatten', cts),
                 (runner, cts.replace('repair_timing -setup -slack_margin 0.250', ''))):
        try:
            derive(a, b)
        except ValueError:
            continue
        raise AssertionError('Unsafe physical experiment accepted')
    print('V296_DECODED_POSTCTS_GENERATOR_SELFTEST_PASS')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--build', action='store_true')
    a = p.parse_args()
    if a.self_test: self_test()
    if a.build: build()
    if not (a.self_test or a.build): p.error('Specify --self-test or --build')
