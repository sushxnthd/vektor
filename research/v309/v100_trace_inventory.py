#!/usr/bin/env python3
"""Bounded, fail-closed inventory of an authentic external SASS trace archive.

This deliberately does NOT estimate GPU cycles, bank conflicts or IPC.
It inventories archive provenance and samples bounded trace prefixes, preserving
negative results if the external source does not meet the trace-format gate.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import tarfile

MAX_ARCHIVE = 64 * 1024 * 1024
MAX_MEMBERS = 200000
MAX_MEMBER_BYTES = 2 * 1024**3
SAMPLE_BYTES = 32768
MAX_SAMPLES = 24
TRACE_EXTENSIONS = ('.trace', '.traceg', '.tracez')
ROW = re.compile(r'^\d+\s+\d+\s+\d+\s+\d+\s+[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+\d+\s+')


def validate_name(name: str) -> None:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or '\x00' in name:
        raise ValueError('unsafe archive member name')


def inspect(path: str) -> dict:
    with open(path, 'rb') as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if not blob or len(blob) > MAX_ARCHIVE:
        raise ValueError('archive outside byte cap')
    digest = hashlib.sha256(blob).hexdigest()
    result = {'evidence_tier': 'external_archive_inventory_bounded_trace_prefixes',
              'archive_bytes': len(blob), 'archive_sha256': digest,
              'member_count': 0, 'trace_member_count': 0, 'trace_bytes_declared': 0,
              'sampled_trace_members': 0, 'sampled_row_prefixes': 0,
              'sampled_rows_matching_old_nvbit_format': 0,
              'samples': [], 'extensions': {}, 'non_trace_examples': [], 'skipped_link_members': 0}
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
            for member in tar:
                result['member_count'] += 1
                if result['member_count'] > MAX_MEMBERS:
                    raise ValueError('too many members')
                validate_name(member.name)
                if member.isdev():
                    raise ValueError('device member rejected')
                if member.issym() or member.islnk():
                    # Metadata-only scan: never follow or extract archive links.
                    result['skipped_link_members'] += 1
                    continue
                if member.size < 0 or member.size > MAX_MEMBER_BYTES:
                    raise ValueError('member size exceeds cap')
                if not member.isfile():
                    continue
                ext = next((e for e in TRACE_EXTENSIONS if member.name.endswith(e)), 'other')
                result['extensions'][ext] = result['extensions'].get(ext, 0) + 1
                if ext == 'other':
                    if len(result['non_trace_examples']) < 16:
                        result['non_trace_examples'].append(member.name)
                    continue
                result['trace_member_count'] += 1
                result['trace_bytes_declared'] += member.size
                if result['sampled_trace_members'] >= MAX_SAMPLES:
                    continue
                fp = tar.extractfile(member)
                if fp is None:
                    raise ValueError('unreadable trace member')
                prefix = fp.read(min(SAMPLE_BYTES, member.size))
                if ext == '.tracez':
                    # compressed tracez needs a separately verified decoder
                    result['samples'].append({'name': member.name, 'size': member.size,
                                              'binary_tracez': True, 'sample_sha256': hashlib.sha256(prefix).hexdigest()})
                    result['sampled_trace_members'] += 1
                    continue
                text = prefix.decode('utf-8', errors='replace')
                lines = text.splitlines()
                if prefix and not prefix.endswith(b'\n') and lines:
                    lines.pop()  # drop potentially truncated last line
                matches = sum(bool(ROW.match(line.strip())) for line in lines)
                result['sampled_row_prefixes'] += len(lines)
                result['sampled_rows_matching_old_nvbit_format'] += matches
                result['samples'].append({'name': member.name, 'size': member.size,
                                          'prefix_bytes': len(prefix), 'complete_prefix_lines': len(lines),
                                          'nvbit_row_matches': matches,
                                          'first_lines': [s[:180] for s in lines[:6]],
                                          'sample_sha256': hashlib.sha256(prefix).hexdigest()})
                result['sampled_trace_members'] += 1
    except (tarfile.TarError, OSError, UnicodeError) as exc:
        raise ValueError(f'invalid gzip tar archive: {exc}') from exc
    if result['trace_member_count'] == 0:
        result['qualification'] = 'NO_TRACE_MEMBERS'
    elif result['sampled_rows_matching_old_nvbit_format'] == 0:
        result['qualification'] = 'TRACE_FORMAT_UNRESOLVED'
    else:
        result['qualification'] = 'AUTHENTIC_TRACE_PREFIXES_ONLY_NOT_PERFORMANCE_VALIDATION'
    return result


def selftest() -> dict:
    def archive(items):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode='w:gz') as t:
            for name, payload in items:
                x = tarfile.TarInfo(name)
                x.size = len(payload)
                t.addfile(x, io.BytesIO(payload))
        return buf.getvalue()
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'fixture.tgz'
        row = b'0 0 0 0 0000 ffffffff 1 R1 IMAD.MOV.U32 2 R2 R3 0\n'
        p.write_bytes(archive([('suite/traces/kernel-0.traceg', b'# header\n' + row),
                               ('suite/traces/kernelslist.g', b'kernel-0.traceg\n')]))
        r = inspect(str(p))
        assert r['trace_member_count'] == 1 and r['sampled_rows_matching_old_nvbit_format'] == 1
        assert r['qualification'] == 'AUTHENTIC_TRACE_PREFIXES_ONLY_NOT_PERFORMANCE_VALIDATION'
        p.write_bytes(archive([('../escape.traceg', row)]))
        try: inspect(str(p))
        except ValueError: pass
        else: raise AssertionError('traversal mutant accepted')
        p.write_bytes(archive([('suite/metadata.txt', b'x')]))
        assert inspect(str(p))['qualification'] == 'NO_TRACE_MEMBERS'
        p.write_bytes(archive([('suite/kernel.traceg', b'# only header\n')]))
        assert inspect(str(p))['qualification'] == 'TRACE_FORMAT_UNRESOLVED'
        p.write_bytes(b'not a gzip tar')
        try: inspect(str(p))
        except ValueError: pass
        else: raise AssertionError('corrupt archive accepted')
    return {'selftest': 'PASS', 'negative_mutants': 4, 'synthetic_fixture_rows': 1}


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('archive', nargs='?')
    a.add_argument('--selftest', action='store_true')
    a.add_argument('--expected-sha256', default=None)
    x = a.parse_args()
    if x.selftest:
        print(json.dumps(selftest(), sort_keys=True))
    if x.archive:
        result = inspect(x.archive)
        if x.expected_sha256 and result['archive_sha256'] != x.expected_sha256:
            raise ValueError('external archive SHA-256 changed from frozen exploratory acquisition')
        print(json.dumps(result, indent=2, sort_keys=True))
    elif not x.selftest:
        a.error('archive required')
