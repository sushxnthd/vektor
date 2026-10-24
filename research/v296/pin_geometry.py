#!/usr/bin/env python3
"""V296 two-regime I/O-boundary stress with identical contestant constraints."""
import argparse
import hashlib
import json
from pathlib import Path
import audit_cts45_setup250 as physical

EDGES = ('top', 'bottom')
ROOT = Path('research/v296')

def replace_one(src, old, new):
    if src.count(old) != 1:
        raise ValueError('source anchor mismatch: ' + old)
    return src.replace(old, new)

def build(edge):
    if edge not in EDGES: raise ValueError('unregistered I/O geometry')
    out = Path(f'build/v296/cts45_pin_stress/{edge}')
    out.mkdir(parents=True, exist_ok=True)
    files = {name: (ROOT / name).read_text() for name in (
        'cap_margin_repair.tcl','cap_margin_third.tcl','cts45_setup250.tcl','run_cts45_setup250.sh')}
    generated = {}
    generated['cap_margin_repair_pin.tcl'] = replace_one(files['cap_margin_repair.tcl'],
        'place_pins -hor_layers metal5 -ver_layers metal6',
        f'puts "V296_PIN_EXCLUDE {edge}"\nplace_pins -hor_layers metal5 -ver_layers metal6 -exclude {edge}:*')
    generated['cap_margin_third_pin.tcl'] = replace_one(files['cap_margin_third.tcl'],
        'source research/v296/cap_margin_repair.tcl', f'source {out}/cap_margin_repair_pin.tcl')
    generated['cts45_pin.tcl'] = replace_one(files['cts45_setup250.tcl'],
        'source research/v296/cap_margin_third.tcl', f'source {out}/cap_margin_third_pin.tcl')
    runner = replace_one(files['run_cts45_setup250.sh'],
        'root=build/v296/cts45_setup250', f'root={out}')
    if runner.count('research/v296/cts45_setup250.tcl') != 2:
        raise ValueError('unexpected source Tcl references')
    generated['run_cts45_pin.sh'] = runner.replace('research/v296/cts45_setup250.tcl', f'{out}/cts45_pin.tcl')
    for name, value in generated.items(): (out / name).write_text(value)
    manifest = {'excluded_edge': edge, 'matched_variants': True,
                'original_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in files.items()},
                'generated_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in generated.items()}}
    (out/'pin_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('V296_PIN_GEOMETRY_GENERATED',edge)

def audit_case(root, edge):
    manifest = json.loads((root/'pin_manifest.json').read_text())
    if manifest.get('excluded_edge') != edge or manifest.get('matched_variants') is not True:
        raise ValueError('I/O geometry provenance mismatch')
    for variant in ('pairwise','serial_onehot'):
        lines = (root/f'{variant}.high.log').read_text(errors='replace').splitlines()
        marker = f'V296_PIN_EXCLUDE {edge}'
        if lines.count(marker) != 1 or any(x.startswith('V296_PIN_EXCLUDE ') and x != marker for x in lines):
            raise ValueError('I/O geometry mismatch: '+variant)
    result = physical.aggregate(root)
    if result['decision'] == 'INCOMPLETE_NO_PHYSICAL_CLAIM':
        raise ValueError('incomplete physical evidence')
    return result

def audit_all(root):
    rows = {}
    for edge in EDGES:
        try: rows[edge] = audit_case(root/edge,edge)
        except (OSError,ValueError,KeyError,IndexError,TypeError) as exc:
            rows[edge] = {'decision':'INCOMPLETE_NO_PHYSICAL_CLAIM','error':str(exc)}
    decisions = [rows[e]['decision'] for e in EDGES]
    if 'INCOMPLETE_NO_PHYSICAL_CLAIM' in decisions:
        verdict = 'INCOMPLETE_NO_PIN_SENSITIVITY_CLAIM'
    elif all(x == 'FEASIBLE_PARETO_SUPPORTED' for x in decisions):
        verdict = 'BOTH_PIN_GEOMETRIES_FEASIBLE_PARETO_SUPPORTED'
    else: verdict = 'PIN_GEOMETRY_ROBUSTNESS_FALSIFIED'
    result = {'decision':verdict,'cases':rows,'preregistered_edges':list(EDGES),
              'placement_seed_replication':False,'strict_equal_consumed_area':False,
              'tile_throughput_measured':False,'holdouts':'SEALED'}
    root.mkdir(parents=True,exist_ok=True)
    (root/'aggregate.pin_stress.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if verdict != 'BOTH_PIN_GEOMETRIES_FEASIBLE_PARETO_SUPPORTED': raise SystemExit(3)

def self_test():
    from tempfile import TemporaryDirectory
    for bad in ('left','right','all',None):
        try: build(bad)
        except ValueError: pass
        else: raise AssertionError('unregistered geometry accepted')
    try: replace_one('foo','bar','x')
    except ValueError: pass
    else: raise AssertionError('missing anchor accepted')
    with TemporaryDirectory() as d:
        try: audit_all(Path(d))
        except SystemExit as exc: assert exc.code == 3
        else: raise AssertionError('missing evidence accepted')
    physical.self_test()
    print('V296_PIN_GEOMETRY_SELFTEST_PASS')

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--edge',choices=EDGES)
    p.add_argument('--aggregate',type=Path)
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test:self_test()
    elif a.edge:build(a.edge)
    elif a.aggregate:audit_all(a.aggregate)
    else:p.error('choose --edge, --aggregate, or --self-test')
