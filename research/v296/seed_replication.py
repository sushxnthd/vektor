#!/usr/bin/env python3
"""Preregistered V296 placement-seed replication and fail-closed independent audit."""
import argparse
import hashlib
import json
from pathlib import Path
import audit_cts45_setup250 as physical

SEEDS = (17, 43)
ROOT = Path('research/v296')

def patch_once(src, old, new):
    if src.count(old) != 1:
        raise ValueError('source changed or ambiguous anchor: ' + old)
    return src.replace(old, new)

def build(seed):
    if seed not in SEEDS:
        raise ValueError('seed not preregistered')
    dest = Path(f'build/v296/cts45_seedrep/seed{seed}')
    dest.mkdir(parents=True, exist_ok=True)
    src = {name: (ROOT / name).read_text() for name in (
        'cap_margin_repair.tcl', 'cap_margin_third.tcl',
        'cts45_setup250.tcl', 'run_cts45_setup250.sh')}
    generated = {}
    generated['cap_margin_repair_seeded.tcl'] = patch_once(
        src['cap_margin_repair.tcl'],
        'global_placement -density $env(V296_PLACE_DENSITY)',
        f'puts "V296_PLACE_SEED {seed}"\nglobal_placement -density $env(V296_PLACE_DENSITY) -random_seed {seed} -perturb_dist 500')
    generated['cap_margin_third_seeded.tcl'] = patch_once(
        src['cap_margin_third.tcl'],
        'source research/v296/cap_margin_repair.tcl',
        f'source {dest}/cap_margin_repair_seeded.tcl')
    generated['cts45_seeded.tcl'] = patch_once(
        src['cts45_setup250.tcl'],
        'source research/v296/cap_margin_third.tcl',
        f'source {dest}/cap_margin_third_seeded.tcl')
    runner = patch_once(src['run_cts45_setup250.sh'],
                        'root=build/v296/cts45_setup250', f'root={dest}')
    if runner.count('research/v296/cts45_setup250.tcl') != 2:
        raise ValueError('source runner has unexpected Tcl references')
    runner = runner.replace('research/v296/cts45_setup250.tcl',
                            f'{dest}/cts45_seeded.tcl')
    generated['run_cts45_seeded.sh'] = runner
    for name, value in generated.items():
        (dest / name).write_text(value)
    manifest = {
        'seed': seed, 'perturb_dist_nm': 500, 'matched_variants': True,
        'original_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in src.items()},
        'generated_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in generated.items()},
    }
    (dest / 'seed_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'V296_SEED_GENERATED seed={seed} path={dest}')

def audit_seed(root, seed):
    manifest = json.loads((root / 'seed_manifest.json').read_text())
    if manifest.get('seed') != seed or manifest.get('perturb_dist_nm') != 500 or manifest.get('matched_variants') is not True:
        raise ValueError('seed provenance mismatch')
    for variant in ('pairwise', 'serial_onehot'):
        lines = (root / f'{variant}.high.log').read_text(errors='replace').splitlines()
        marker = f'V296_PLACE_SEED {seed}'
        if lines.count(marker) != 1 or any(x.startswith('V296_PLACE_SEED ') and x != marker for x in lines):
            raise ValueError('missing or conflicting physical seed marker: ' + variant)
    result = physical.aggregate(root)
    if result['decision'] == 'INCOMPLETE_NO_PHYSICAL_CLAIM':
        raise ValueError('incomplete physical evidence')
    return result

def audit_all(root):
    cases = {}
    for seed in SEEDS:
        try:
            cases[str(seed)] = audit_seed(root / f'seed{seed}', seed)
        except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
            cases[str(seed)] = {'decision': 'INCOMPLETE_NO_PHYSICAL_CLAIM', 'error': str(exc)}
    decisions = [cases[str(seed)]['decision'] for seed in SEEDS]
    if 'INCOMPLETE_NO_PHYSICAL_CLAIM' in decisions:
        decision = 'INCOMPLETE_NO_REPLICATION_CLAIM'
    elif all(d == 'FEASIBLE_PARETO_SUPPORTED' for d in decisions):
        decision = 'ALL_SEEDS_FEASIBLE_PARETO_SUPPORTED'
    else:
        decision = 'SEED_ROBUSTNESS_FALSIFIED'
    result = {'decision': decision, 'seeds': cases, 'frozen_seed_set': list(SEEDS),
              'strict_equal_consumed_area': False, 'gpu_tile_performance_measured': False,
              'unseen_workload_holdouts': 'SEALED'}
    root.mkdir(parents=True, exist_ok=True)
    (root / 'aggregate.seedrep.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if decision != 'ALL_SEEDS_FEASIBLE_PARETO_SUPPORTED':
        raise SystemExit(3)

def self_test():
    from tempfile import TemporaryDirectory
    assert SEEDS == (17,43)
    for bad in (0,1,42,44):
        try: build(bad)
        except ValueError: pass
        else: raise AssertionError('unregistered seed accepted')
    try: patch_once('foo', 'missing', 'x')
    except ValueError: pass
    else: raise AssertionError('missing anchor accepted')
    with TemporaryDirectory() as td:
        try: audit_all(Path(td))
        except SystemExit as exc: assert exc.code == 3
        else: raise AssertionError('missing evidence passed')
    physical.self_test()
    print('V296_SEED_REPLICATION_SELFTEST_PASS')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int)
    p.add_argument('--aggregate', type=Path)
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test: self_test()
    elif a.seed is not None: build(a.seed)
    elif a.aggregate is not None: audit_all(a.aggregate)
    else: p.error('choose --seed, --aggregate or --self-test')

if __name__ == '__main__': main()
