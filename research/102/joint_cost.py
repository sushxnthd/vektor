"""Synthetic serialized service-slot accounting, NOT a GPU cycle simulator."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, asdict
from math import ceil
import random

@dataclass(frozen=True)
class Config:
    pattern: str = 'balanced'
    length: int = 16
    warps: int = 8
    window: int = 8
    banks: int = 16
    rf_ports: int = 4
    migration_bw: int = 32
    setup: int = 4
    memory_stride: int = 0
    memory_ports: int = 2
    locality: str = 'warp_local'
    seed: int = 102
    bank_scheme: str = 'linear'
    estimate_length: int = 8

@dataclass(frozen=True)
class Lane:
    warp: int
    lane: int
    path: int
    address: int

def trace(c: Config) -> list[Lane]:
    r = random.Random(c.seed)
    lanes = []
    for w in range(c.warps):
        for lane in range(32):
            if c.pattern == 'coherent': p = 0
            elif c.pattern == 'balanced': p = lane % 2
            elif c.pattern == 'minority': p = int(lane == 31)
            elif c.pattern == 'four_path': p = lane % 4
            elif c.pattern == 'random': p = r.randrange(4)
            else: raise ValueError(c.pattern)
            if c.locality == 'warp_local': addr = (w * 32 + lane) * 4
            elif c.locality == 'path_striped': addr = (p * c.warps * 32 + w * 32 + lane) * 4
            elif c.locality == 'random': addr = r.randrange(256) * 128 + (lane % 32) * 4
            else: raise ValueError(c.locality)
            lanes.append(Lane(w, lane, p, addr))
    return lanes

def grouped(lanes: list[Lane], compact: bool) -> list[list[Lane]]:
    buckets: dict[tuple[int, int], list[Lane]] = {}
    for x in lanes:
        key = (0 if compact else x.warp, x.path)
        buckets.setdefault(key, []).append(x)
    groups = []
    for key in sorted(buckets):
        v = buckets[key]
        if compact:
            for i in range(0, len(v), 32): groups.append(v[i:i+32])
        else: groups.append(v)
    return groups

def group_slots(group: list[Lane], c: Config) -> tuple[int, int, int]:
    total = 0; tx = 0; reads = 0
    for inst in range(c.length):
        counts = Counter()
        for x in group:
            for reg in ((inst * 7) % 64, (inst * 11 + 3) % 64):
                if c.bank_scheme == 'linear': bank = (x.warp * 13 + x.lane * 5 + reg * 3) % c.banks
                elif c.bank_scheme == 'xor': bank = (x.warp * 13 ^ x.lane * 5 ^ reg * 3) % c.banks
                elif c.bank_scheme == 'lane': bank = (x.lane + reg) % c.banks
                else: raise ValueError(c.bank_scheme)
                counts[bank] += 1
                reads += 1
        rf = max(1, max((ceil(n / c.rf_ports) for n in counts.values()), default=0))
        if c.memory_stride and inst % c.memory_stride == 0:
            lines = len({x.address // 128 for x in group})
            tx += lines
            mem = ceil(lines / c.memory_ports)
        else: mem = 0
        total += max(1, rf, mem)
    return total, tx, reads

def window_cost(lanes: list[Lane], c: Config, compact: bool) -> dict:
    groups = grouped(lanes, compact)
    service = tx = reads = 0
    for group in groups:
        s, m, r = group_slots(group, c)
        service += s; tx += m; reads += r
    migrated = 0
    if compact:
        for g in groups:
            source = Counter(x.warp for x in g)
            migrated += len(g) - max(source.values())
    overhead = c.setup + ceil(migrated / c.migration_bw) if compact else 0
    return dict(cost=service + overhead, service=service, overhead=overhead,
                migrated=migrated, groups=len(groups), transactions=tx, rf_reads=reads)

def run(c: Config) -> dict:
    assert c.warps % c.window == 0 and c.window > 0
    assert c.length > 0 and c.rf_ports > 0 and c.migration_bw > 0
    lanes = trace(c)
    totals = {k:0 for k in ('ipdom','dwf','heuristic','oracle')}
    details = []
    for start in range(0,c.warps,c.window):
        subset = [x for x in lanes if start <= x.warp < start+c.window]
        b = window_cost(subset,c,False)
        d = window_cost(subset,c,True)
        estimated_saving = (b['groups'] - d['groups']) * c.estimate_length
        use_dwf = estimated_saving > d['overhead']
        totals['ipdom'] += b['cost']; totals['dwf'] += d['cost']
        totals['heuristic'] += d['cost'] if use_dwf else b['cost']
        totals['oracle'] += min(b['cost'],d['cost'])
        details.append(dict(base=b,compacted=d,heuristic_compacts=use_dwf,
                            estimated_saving=estimated_saving))
        assert b['rf_reads'] == d['rf_reads'] == len(subset)*2*c.length
    assert totals['oracle'] <= min(totals['ipdom'],totals['dwf'])
    return dict(config=asdict(c), totals=totals, windows=details,
                speedup=totals['ipdom']/totals['dwf'],
                heuristic_speedup=totals['ipdom']/totals['heuristic'])
