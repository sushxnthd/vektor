#!/usr/bin/env python3
"""Independent audit of four-way Yosys/Nangate45 V296 return-tree mapping.

Usage: python3 research/v296/return_tree_mapped_audit.py path/to/unzipped-artifact
Optional: --source-root PATH (verifies both RTL files against hosted hashes).
Only graph-depth and mapped area are measured; no timing or power claim.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

CASES = {
    'original_pairwise': 'v296_tile_slice',
    'original_serial': 'v296_tile_slice',
    'balanced_pairwise': 'v296_tile_slice_return_tree',
    'balanced_serial': 'v296_tile_slice_return_tree',
}
EXPECTED_LIBRARY_SHA256 = '8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1'
EXPECTED_LOG_SHA256 = {
    'original_pairwise': 'ff9a855c1644f503f0fc664c59f81d341fa3635e547cb360046e3699cf6a8d4a',
    'original_serial': 'ed757e44f652e5f61eed6ccb78ac8785df5cc94ed4eaf1b6ffa71856cdceab1d',
    'balanced_pairwise': '9439a4cb8cfea04b3b7bc33d0de9eacbc3dbe8031e9aad10c015b4303687678a',
    'balanced_serial': 'ea503b43ab89b95efb826dacb8e094e96c1e5ae9995ae0c754f75e427fd0d5df',
}
SOURCE_PATHS = (
    'research/v296/v296_tile_slice.sv',
    'research/v296/v296_tile_slice_return_tree.sv',
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(folder, source_root=None):
    folder = Path(folder)
    libline = (folder / 'library.sha256').read_text().splitlines()
    assert len(libline) == 1, 'library hash manifest malformed'
    lib_hash = libline[0].split()[0]
    assert re.fullmatch(r'[0-9a-f]{64}', lib_hash), 'invalid library hash'
    assert lib_hash == EXPECTED_LIBRARY_SHA256, 'unexpected library manifest'
    assert sha256(folder / 'nangate.lib') == lib_hash, 'library checksum mismatch'
    source_manifest = (folder / 'source.sha256').read_text().splitlines()
    sources = {}
    for line in source_manifest:
        fields = line.split(maxsplit=1)
        assert len(fields) == 2 and re.fullmatch(r'[0-9a-f]{64}', fields[0]), 'bad source manifest'
        assert fields[1] not in sources, 'duplicate source hash entry'
        sources[fields[1]] = fields[0]
    assert set(sources) == set(SOURCE_PATHS), 'unexpected source manifest'
    if source_root is not None:
        for name, expected in sources.items():
            assert sha256(Path(source_root) / name) == expected, 'source mismatch: ' + name
    version = (folder / 'yosys.version').read_text().strip()
    assert version.startswith('Yosys 0.9 '), 'unexpected synthesis version'

    results = {}
    for case, module in CASES.items():
        logfile = folder / (case + '.log')
        assert sha256(logfile) == EXPECTED_LOG_SHA256[case], 'hosted log digest mismatch: ' + case
        log = logfile.read_text()
        areas = re.findall(r"Chip area for module '\\([^']+)':\s*([0-9]+(?:\.[0-9]+)?)", log)
        paths = re.findall(r'Longest topological path in (\w+) \(length=(\d+)\):', log)
        assert len(areas) == len(paths) == 1, 'ambiguous area/path in ' + case
        assert areas[0][0] == paths[0][0] == module, 'unexpected top in ' + case
        area = float(areas[0][1])
        depth = int(paths[0][1])
        assert math.isfinite(area) and area > 0 and depth > 0
        tail = log.split('Longest topological path in ' + module, 1)[1]
        indices = [int(m.group(1)) for m in re.finditer(r'^\s*(\d+):', tail, re.M)]
        assert indices == list(range(depth + 1)), 'incomplete topological path in ' + case
        results[case] = {'area_um2': area, 'ltp_edges': depth}

    def percent(new, old):
        return 100 * (new / old - 1)

    op, os = results['original_pairwise'], results['original_serial']
    bp, bs = results['balanced_pairwise'], results['balanced_serial']
    comparisons = {
        'pairwise_return_tree_vs_original': {
            'area_pct': percent(bp['area_um2'], op['area_um2']),
            'depth_pct': percent(bp['ltp_edges'], op['ltp_edges']),
        },
        'serial_return_tree_vs_original': {
            'area_pct': percent(bs['area_um2'], os['area_um2']),
            'depth_pct': percent(bs['ltp_edges'], os['ltp_edges']),
        },
        'balanced_pairwise_vs_balanced_serial': {
            'area_pct': percent(bp['area_um2'], bs['area_um2']),
            'depth_pct': percent(bp['ltp_edges'], bs['ltp_edges']),
        },
    }
    assert bp['ltp_edges'] < op['ltp_edges'], 'pairwise depth hypothesis failed'
    assert bs['ltp_edges'] > os['ltp_edges'], 'serial depth regression unexpectedly absent'
    return {'artifact_type': 'mapped_yosys_only_not_postroute', 'yosys': version,
            'nangate45_sha256': lib_hash, 'source_sha256': sources,
            'results': results, 'comparisons': comparisons,
            'physical_closure': 'not_tested_by_this_checker'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact_dir')
    parser.add_argument('--source-root', default=None)
    args = parser.parse_args()
    print(json.dumps(audit(args.artifact_dir, args.source_root), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
