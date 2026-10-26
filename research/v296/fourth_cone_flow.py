#!/usr/bin/env python3
"""Matched pre-CTS fourth-global-route critical-cone localization, no signoff.

Truncates the frozen paired physical Tcl at the first common fourth-round
checkpoint. It does not replace either arbiter, change constraints, or add ports.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tile_slice_flow

ROOT = Path('research/v296')
OUT = Path('build/v296/tile_slice')
STOP = 'puts "V296_CTS45_FOURTH_DONE"'
RUN_TCL = '"$root/cts45_tile.tcl"'
RUN_AUDIT = 'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?'
RUN_END = 'echo "TILE_SLICE_POSTCTS_EXTRACTED_COMPLETE $variant"'
DIAG = r'''
puts "V296_FOURTH_CONE_BEGIN"
puts "V296_FOURTH_CONE_TIER PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS"
puts "V296_FOURTH_CONE_SETUP_PATH_BEGIN"
report_checks -path_delay max -fields {slew capacitance fanout} -digits 6
puts "V296_FOURTH_CONE_SETUP_PATH_END"
puts "V296_FOURTH_CONE_HOLD_PATH_BEGIN"
report_checks -path_delay min -fields {slew capacitance fanout} -digits 6
puts "V296_FOURTH_CONE_HOLD_PATH_END"
puts "V296_FOURTH_CONE_WORST_SETUP_BEGIN"
report_worst_slack -max -digits 6
puts "V296_FOURTH_CONE_WORST_SETUP_END"
puts "V296_FOURTH_CONE_WORST_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_FOURTH_CONE_WORST_HOLD_END"
write_def "$env(V296_OUT).fourth_diag.def"
puts "V296_FOURTH_CONE_DONE"
'''

def replace_once(src, before, after):
    if src.count(before) != 1:
        raise ValueError('Frozen anchor missing/duplicated: ' + before)
    return src.replace(before, after)

def derive(tcl, runner):
    if tcl.count(STOP) != 1:
        raise ValueError('Common fourth-round boundary absent')
    prefix = tcl.split(STOP, 1)[0]
    for required in ('v296_repair_metrics cts45_fourth_routed',
                     'global_route -guide_file "$env(V296_OUT).fourth.guide"',
                     'estimate_parasitics -global_routing'):
        if required not in prefix:
            raise ValueError('Fourth-round route missing: ' + required)
    if any(x in prefix for x in ('clock_tree_synthesis', 'detailed_route -output_drc',
                                  'extract_parasitics -ext_model_file')):
        raise ValueError('Not a pre-CTS stop')
    tcl_out = prefix + DIAG
    runner_out = replace_once(runner, RUN_TCL, '"$root/cts45_fourth_diag.tcl"')
    runner_out = replace_once(runner_out, RUN_AUDIT,
                              'test -s "$root/$variant.high.fourth_diag.def" || audit_rc=$?')
    runner_out = replace_once(runner_out, RUN_END,
                              'echo "V296_FOURTH_CONE_NO_SIGNOFF $variant"')
    return tcl_out, runner_out

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def self_test():
    fake = ('global_route -guide_file "$env(V296_OUT).fourth.guide"\n'
            'estimate_parasitics -global_routing\n'
            'v296_repair_metrics cts45_fourth_routed\n' + STOP + '\n'
            'clock_tree_synthesis\n')
    runner = RUN_TCL + '\n' + RUN_AUDIT + '\n' + RUN_END
    a,b = derive(fake,runner)
    assert 'V296_FOURTH_CONE_DONE' in a and 'clock_tree_synthesis' not in a
    assert 'fourth_diag.def' in b and 'NO_SIGNOFF' in b
    assert '-group_path_count' not in a
    for bad in (fake.replace(STOP, 'wrong'), fake + STOP, fake.replace('v296_repair_metrics cts45_fourth_routed','')):
        try: derive(bad,runner)
        except ValueError: pass
        else: raise AssertionError('Accepted invalid Tcl')
    for bad in (runner.replace(RUN_AUDIT,''),runner+RUN_TCL):
        try: derive(fake,bad)
        except ValueError: pass
        else: raise AssertionError('Accepted invalid runner')
    print('V296_FOURTH_CONE_GENERATOR_SELFTEST_PASS')

def build():
    tile_slice_flow.build()
    tcl=(OUT/'cts45_tile.tcl').read_text()
    runner=(ROOT/'run_tile_slice_return_tree.sh').read_text()
    a,b=derive(tcl,runner)
    (OUT/'cts45_fourth_diag.tcl').write_text(a)
    (OUT/'run_fourth_diag.sh').write_text(b)
    (OUT/'fourth_diag_manifest.json').write_text(json.dumps({
        'tier':'PRECTS_GLOBAL_ROUTE_ONLY_NOT_SIGNOFF',
        'preregistration':'research/v296/FOURTH_CONE_PREREG_20261026.md',
        'source_tcl_sha256':sha(tcl),'source_runner_sha256':sha(runner),
        'generated_tcl_sha256':sha(a),'generated_runner_sha256':sha(b),
        'clock_ns':3.5,'shared_fourth_stage':True,
        'serial_fifth_control_repair_excluded':True,
        'extracted_rc':False,'postcts':False,'routed':False
    },indent=2)+'\n')
    print('V296_FOURTH_CONE_GENERATED')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--build',action='store_true')
    a=p.parse_args()
    if a.self_test:self_test()
    if a.build:build()
    if not(a.self_test or a.build):p.error('select --self-test or --build')
