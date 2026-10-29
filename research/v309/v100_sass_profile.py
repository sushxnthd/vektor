#!/usr/bin/env python3
"""V309: full authentic V100 trace demand descriptors, NOT hardware stall counts."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import tarfile

from v100_trace_inventory import MAX_ARCHIVE, validate_name

EXPECTED_SHA = 'aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1'
REG = re.compile(r'R([0-9]+)\Z')
OP = re.compile(r'[A-Za-z][A-Za-z0-9_.]*\Z')
HEX = re.compile(r'[0-9a-fA-F]+\Z')
BANKS = (2, 4, 8)
FIELDS = ('rows','zero_mask','active','active_lanes','memory','source_occurrences',
          'unique_sources','duplicate_sources','r255_occurrences','multi_source',
          'unsupported','files')


def parse_row(line: str):
    t = line.split()
    if len(t) < 9:
        raise ValueError('short instruction')
    try:
        cta_warp = [int(v) for v in t[:4]]
        if any(v < 0 for v in cta_warp): raise ValueError('negative CTA/warp')
        if not HEX.fullmatch(t[4]) or not HEX.fullmatch(t[5]): raise ValueError('PC/mask not hex')
        mask = int(t[5], 16)
        if mask > 0xffffffff: raise ValueError('mask too wide')
        ndst = int(t[6]); pos = 7
        if not 0 <= ndst <= 16: raise ValueError('destination count invalid')
        dest = t[pos:pos+ndst]; pos += ndst
        if len(dest) != ndst or any(not REG.fullmatch(v) for v in dest):
            raise ValueError('destination register invalid')
        opcode = t[pos]; pos += 1
        if not OP.fullmatch(opcode): raise ValueError('opcode invalid')
        nsrc = int(t[pos]); pos += 1
        if not 0 <= nsrc <= 16: raise ValueError('source count invalid')
        src = t[pos:pos+nsrc]; pos += nsrc
        if len(src) != nsrc or any(not REG.fullmatch(v) for v in src):
            raise ValueError('source register invalid')
        width = int(t[pos]); pos += 1
        if width < 0: raise ValueError('negative memory width')
        if width == 0 and pos != len(t): raise ValueError('unexpected nonmemory payload')
        return mask, opcode, tuple(int(REG.fullmatch(x).group(1)) for x in src), width
    except (IndexError, ValueError) as exc:
        raise ValueError(str(exc)) from exc


def fresh():
    x = {f:0 for f in FIELDS}
    x.update({f'collide_mod{b}_all':0 for b in BANKS})
    x.update({f'collide_mod{b}_without_r255':0 for b in BANKS})
    return x


def account(row, acc):
    mask, opcode, src, width = row
    acc['rows'] += 1
    if mask == 0:
        acc['zero_mask'] += 1
        return
    acc['active'] += 1
    acc['active_lanes'] += mask.bit_count()
    acc['memory'] += (width > 0)
    acc['source_occurrences'] += len(src)
    acc['unique_sources'] += len(set(src))
    acc['duplicate_sources'] += len(src)-len(set(src))
    acc['r255_occurrences'] += src.count(255)
    acc['multi_source'] += (len(set(src)) >= 2)
    unique = set(src)
    no255 = unique - {255}
    for b in BANKS:
        acc[f'collide_mod{b}_all'] += (len({v%b for v in unique}) < len(unique))
        acc[f'collide_mod{b}_without_r255'] += (len({v%b for v in no255}) < len(no255))


def profile(path):
    with open(path,'rb') as f: blob=f.read(MAX_ARCHIVE+1)
    if len(blob)>MAX_ARCHIVE: raise ValueError('compressed archive over cap')
    sha=hashlib.sha256(blob).hexdigest()
    if sha != EXPECTED_SHA: raise ValueError('external archive SHA-256 differs from frozen digest')
    apps=defaultdict(fresh)
    opcodes=defaultdict(Counter)
    unsupported=[]
    trace_files=0
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        for m in tar:
            validate_name(m.name)
            if m.isdev(): raise ValueError('device entry')
            if m.issym() or m.islnk() or not m.isfile(): continue
            if not m.name.endswith('.traceg'): continue
            if m.size>2*1024**3: raise ValueError('trace file too large')
            parts=PurePosixPath(m.name).parts
            if len(parts)<5: raise ValueError('unrecognized trace directory layout')
            app=parts[2]
            a=apps[app]
            a['files']+=1; trace_files+=1
            f=tar.extractfile(m)
            if f is None: raise ValueError('unreadable trace')
            for n, raw in enumerate(f,1):
                s=raw.decode('utf-8',errors='replace').strip()
                if not s or s.startswith(('#','-')): continue
                if not s[0].isdigit(): continue
                try:
                    row=parse_row(s)
                except ValueError as exc:
                    a['unsupported']+=1
                    if len(unsupported)<12: unsupported.append({'app':app,'file':m.name,'line':n,'reason':str(exc),'prefix':s[:120]})
                    continue
                account(row,a)
                if row[0]: opcodes[app][row[1]]+=1
    global_counts=fresh()
    for a in apps.values():
        for k in global_counts: global_counts[k]+=a[k]
    if global_counts['active']==0: raise ValueError('no decoded active dynamic rows')
    result={'evidence_tier':'authentic_V100_SASS_dynamic_instruction_demand_NOT_measured_stalls',
            'archive_sha256':sha,'trace_files':trace_files,
            'application_count':len(apps),'global':global_counts,
            'applications':{k:{**v,'top_opcodes':opcodes[k].most_common(12)} for k,v in sorted(apps.items())},
            'unsupported_examples':unsupported,
            'model_limits':['R255 semantics not physically verified','modulo bank maps are hypothetical',
                            'no matched hardware counters','no execution or memory latency model',
                            'no RTX 5090 inference']}
    return result


def selftest():
    a=fresh()
    account(parse_row('0 0 0 0 0010 ffffffff 1 R1 IMAD.U32 3 R1 R1 R3 0'),a)
    assert a['active']==1 and a['source_occurrences']==3 and a['unique_sources']==2
    assert a['duplicate_sources']==1 and a['collide_mod2_all']==1 and a['collide_mod4_all']==0
    account(parse_row('0 0 0 0 0000 00000000 0 SHFL.IDX 2 R255 R255 0'),a)
    assert a['zero_mask']==1 and a['active']==1
    account(parse_row('0 0 0 0 0020 000000ff 1 R2 LDG.E 1 R255 4 0x1234'),a)
    assert a['memory']==1 and a['r255_occurrences']==1 and a['active_lanes']==40
    mutants=['0 0 0 0 0000 ffffffff 0 MOV 1 RX 0',
             '0 0 0 0 0000 ffffffff 0 MOV 1 R1 0 extra',
             '0 0 0 0 0000 ffffffff 0 MOV 3 R1 0',
             '0 0 0 0 0000 ffffffff 0 MOV 0 -1']
    for x in mutants:
        try:parse_row(x)
        except ValueError:pass
        else:raise AssertionError('malformed row accepted: '+x)
    return {'selftest':'PASS','mutation_tests':len(mutants),'active_fixture_rows':2}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('archive',nargs='?')
    p.add_argument('--selftest',action='store_true')
    x=p.parse_args()
    if x.selftest: print(json.dumps(selftest()))
    if x.archive: print(json.dumps(profile(x.archive),indent=2,sort_keys=True))
    elif not x.selftest:p.error('archive required')
