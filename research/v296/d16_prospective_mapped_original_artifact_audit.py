#!/usr/bin/env python3
"""Fail-closed, independent audit of prospectively frozen D16 mapped-area transfer.

The freeze precedes Actions 40542155911. All outputs are MAPPED_ONLY, not STA,
physical closure, workload performance, or energy. No measured D16 area is embedded.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

RUN = 40542155911
HEAD = '831ec79865d4c0b85f8bc25904737eb7c73a702b'
EXPECTED = {
    4: ('cdeee83a0b3e22f0734c3c107181ef2a9231fec1c71c52d55d73bc592cfd28c6', 12752126503),
    8: ('efe40ce43c0d4ad37a7a83902ccb566e671633b59287631e2f38c4f3d255e8d4', 12751094117),
    16: ('f1733131d283e6cedcc96cddd3070773a9d9d98f2ec16f6eb04d7a6c9140b008', 12752960026),
}
RTL16 = ('29ed1b595edc447c621fe68644c1a4b733d42e2648b22cb423cfa5c0980dbe37', 12750287978)
FREEZE = {'pairwise': 26736.458, 'serial': 28674.800, 'relative_error_limit': 0.15}
AREA_RE = re.compile(r"Chip area for module '\\v296_tile_slice_deep_bank': ([0-9.]+)")
LTP_RE = re.compile(r'Longest topological path in v296_tile_slice_deep_bank \(length=(\d+)\):')


def verified_zip(path, expected):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError(f'original artifact SHA mismatch: {path}')
    z = ZipFile(path)
    if any(n.startswith('/') or '..' in Path(n).parts for n in z.namelist()):
        raise ValueError('unsafe ZIP member path')
    if len(z.namelist()) != len(set(z.namelist())):
        raise ValueError('duplicate ZIP members')
    return z


def parse_mapped(path, depth):
    digest, artifact_id = EXPECTED[depth]
    z = verified_zip(path, digest)
    wanted = {f'depth{depth}_pairwise.log', f'depth{depth}_serial.log',
              'evidence_tier.txt', 'nangate.lib', 'source_library.sha256', 'yosys.version'}
    if set(z.namelist()) != wanted:
        raise ValueError(f'unexpected mapped artifact members at D{depth}')
    if z.read('evidence_tier.txt').decode().strip() != f'MAPPED_ONLY_NO_PHYSICAL_SIGNOFF depth={depth}':
        raise ValueError('evidence tier mismatch')
    version = z.read('yosys.version').decode().strip()
    if version != 'Yosys 0.9 (git sha1 1979e0b)':
        raise ValueError('unexpected Yosys version')
    provenance = z.read('source_library.sha256').decode()
    lines = provenance.strip().splitlines()
    if len(lines) != 4 or not all(re.fullmatch(r'[a-f0-9]{64}  .+', x) for x in lines):
        raise ValueError('incomplete source/library hashes')
    lib_digest = hashlib.sha256(z.read('nangate.lib')).hexdigest()
    if not any(x.startswith(lib_digest + '  ') and x.endswith('/nangate.lib') for x in lines):
        raise ValueError('standard-cell library hash mismatch')
    parsed = {}
    for architecture in ('pairwise', 'serial'):
        log = z.read(f'depth{depth}_{architecture}.log').decode(errors='replace')
        if 'Executing CHECK pass' not in log or 'found and reported 0 problems.' not in log:
            raise ValueError(f'Yosys structural check failed: D{depth} {architecture}')
        areas = AREA_RE.findall(log)
        lengths = LTP_RE.findall(log)
        if len(areas) != 1 or len(lengths) != 1:
            raise ValueError(f'ambiguous mapped area/diagnostic: D{depth} {architecture}')
        parsed[architecture] = {'area_um2': float(areas[0]),
                                'ltp_noff_nodes_NOT_STA': int(lengths[0]),
                                'ltp_loop_warnings': log.count('Warning: Detected loop at')}
        if parsed[architecture]['area_um2'] <= 0:
            raise ValueError('nonpositive area')
    return {'artifact_id': artifact_id, 'sha256': digest, 'areas': parsed,
            'provenance': provenance, 'tool_version': version}


def audit(paths, rtl16):
    parsed = {d: parse_mapped(paths[d], d) for d in (4, 8, 16)}
    if len({parsed[d]['provenance'] for d in parsed}) != 1:
        raise ValueError('source/library changed across depth')
    if len({parsed[d]['tool_version'] for d in parsed}) != 1:
        raise ValueError('tool changed across depth')
    z = verified_zip(rtl16, RTL16[0])
    if z.namelist() != ['v296_deep_bank_rtl.log']:
        raise ValueError('unexpected D16 RTL archive members')
    rtl = z.read('v296_deep_bank_rtl.log').decode().strip()
    if rtl != 'V296_DEEP_BANK_DYNAMIC_RTL_PASS depth=16 cycles=2048 accepted=6608 word_addresses=16':
        raise ValueError('D16 RTL oracle mismatch')
    for architecture in ('pairwise', 'serial'):
        a4 = parsed[4]['areas'][architecture]['area_um2']
        a8 = parsed[8]['areas'][architecture]['area_um2']
        if abs((a8 + 2*(a8-a4)) - FREEZE[architecture]) > 0.001:
            raise ValueError('frozen D16 prediction does not follow D4/D8 observations')
    observed = {x: parsed[16]['areas'][x]['area_um2'] for x in ('pairwise', 'serial')}
    relative = {x: (observed[x]-FREEZE[x])/FREEZE[x] for x in observed}
    model_pass = all(abs(relative[x]) <= FREEZE['relative_error_limit'] for x in relative) and observed['pairwise'] < observed['serial']
    saving = observed['serial']-observed['pairwise']
    return {'source_run': RUN, 'source_head': HEAD,
            'evidence_tier': 'SHA_VERIFIED_RTL_AND_MAPPED_SYNTHESIS_ONLY',
            'frozen_before_run': FREEZE, 'measured_D16_um2': observed,
            'relative_prediction_error': relative,
            'measured_D16_saving_um2': saving,
            'measured_D16_saving_pct_of_serial': 100*saving/observed['serial'],
            'predicted_saving_um2': FREEZE['serial']-FREEZE['pairwise'],
            'predicted_saving_overstatement_pct': 100*((FREEZE['serial']-FREEZE['pairwise'])-saving)/(FREEZE['serial']-FREEZE['pairwise']),
            'prospective_mapped_model_gate': 'PASS' if model_pass else 'FAIL',
            'integer_slices_under_30000um2': {x: int(30000//observed[x]) for x in observed},
            'original_artifacts': {str(d): {'id': parsed[d]['artifact_id'], 'sha256': parsed[d]['sha256']} for d in parsed},
            'original_D16_RTL': {'id': RTL16[1], 'sha256': RTL16[0]},
            'diagnostics_NOT_TIMING': {str(d): parsed[d]['areas'] for d in parsed},
            'limitations': ['Yosys LTP -noff crosses sequential arcs; not STA',
                            'flop-array 8-bit register-file proxy, not macro',
                            'serial control not independently routed feasible',
                            'no extracted RC, wire/load, clock, throughput, bandwidth, or power evidence']}


def self_test():
    assert abs((17552.542 + 2*(17552.542-12960.584))-FREEZE['pairwise']) < 0.001
    assert abs((18782.260 + 2*(18782.260-13835.990))-FREEZE['serial']) < 0.001
    assert abs(100*(28998.256-27861.638)/28998.256 - 3.91960813091657) < 1e-9
    try:
        verified_zip(__file__, '0'*64)
    except ValueError as e:
        assert 'SHA mismatch' in str(e)
    else:
        raise AssertionError('corrupt artifact accepted')
    print('V296_D16_INDEPENDENT_AUDIT_SELFTEST_PASS')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    for d in (4, 8, 16):
        p.add_argument(f'--mapped{d}', type=Path)
    p.add_argument('--rtl16', type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test()
    else:
        if any(getattr(args, f'mapped{d}') is None for d in (4, 8, 16)) or args.rtl16 is None:
            p.error('supply three mapped original ZIPs and the D16 RTL ZIP')
        print(json.dumps(audit({d: getattr(args, f'mapped{d}') for d in (4, 8, 16)}, args.rtl16), indent=2, sort_keys=True))
