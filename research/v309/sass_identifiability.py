#!/usr/bin/env python3
"""V309: exact finite-collector RF read-service falsification, NOT GPU timing.

The input format is a strict subset of Accel-Sim's plaintext trace rows:
CTA.x CTA.y CTA.z warp PC active_mask ndst [dsts] opcode nsrc [srcs] mem_width.
Memory rows are deliberately rejected; no architecture-specific SASS inference.
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
import itertools
import json
import re

REG = re.compile(r"R([0-9]+)\Z")
OP = re.compile(r"[A-Za-z][A-Za-z0-9_.]*\Z")
HEX = re.compile(r"[0-9a-fA-F]+\Z")


def parse_trace(text: str) -> list[tuple[int, ...]]:
    out = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        t = line.split()
        if len(t) < 10:
            raise ValueError(f'line {lineno}: short trace row')
        try:
            for i in range(4):
                if int(t[i]) < 0:
                    raise ValueError('negative CTA or warp')
            if not HEX.fullmatch(t[4]) or not HEX.fullmatch(t[5]):
                raise ValueError('invalid hex PC/mask')
            mask = int(t[5], 16)
            if mask > 0xffffffff or mask == 0:
                raise ValueError('invalid active mask')
            ndst = int(t[6]); pos = 7
            if ndst < 0 or ndst > 8:
                raise ValueError('destination count out of bounds')
            dest = t[pos:pos+ndst]; pos += ndst
            if len(dest) != ndst or any(not REG.fullmatch(x) for x in dest):
                raise ValueError('invalid destination registers')
            opcode = t[pos]; pos += 1
            if not OP.fullmatch(opcode):
                raise ValueError('invalid opcode')
            nsrc = int(t[pos]); pos += 1
            if nsrc < 0 or nsrc > 8:
                raise ValueError('source count out of bounds')
            src = t[pos:pos+nsrc]; pos += nsrc
            if len(src) != nsrc or any(not REG.fullmatch(x) for x in src):
                raise ValueError('invalid source registers')
            if pos >= len(t) or t[pos] != '0' or pos+1 != len(t):
                raise ValueError('memory payload or trailing fields not supported')
        except (ValueError, IndexError) as exc:
            raise ValueError(f'line {lineno}: {exc}') from exc
        # Broadcast identical sources within an instruction for free.
        out.append(tuple(sorted({int(REG.fullmatch(x).group(1)) for x in src})))
    if not out:
        raise ValueError('no trace instructions')
    return out


def bank_demands(instrs: list[tuple[int, ...]], banks: int) -> tuple[tuple[int, ...], ...]:
    if banks < 1 or banks > 64:
        raise ValueError('invalid bank count')
    return tuple(tuple(sum(reg % banks == b for reg in src) for b in range(banks)) for src in instrs)


def partitions(n: int, cap: int):
    """All allocations of up to cap identical bank read ports across n collectors."""
    if n == 0:
        yield ()
    else:
        for x in range(cap + 1):
            for tail in partitions(n - 1, cap - x):
                yield (x,) + tail


def optimal_cycles(demands: tuple[tuple[int, ...], ...], collectors: int, ports: int) -> int:
    """Exact shortest makespan, finite collector admission, independent reads.

    A collector is admitted in trace order. Reads of admitted instructions may
    interleave; a finished instruction frees its slot on the NEXT cycle.
    Zero-source instructions consume no bank service and are skipped.
    No execution latency, dependencies, dispatch overhead or occupancy model.
    """
    if collectors < 1 or ports < 1 or ports > 8 or collectors > 8:
        raise ValueError('invalid collector/port budget')
    ds = tuple(d for d in demands if any(d))
    n = len(ds)
    if not n:
        return 0
    banks = len(ds[0])
    if n > 8 or banks > 8:
        raise ValueError('exact oracle limited to <=8 instructions and banks')

    @lru_cache(None)
    def solve(next_idx: int, active: tuple[tuple[int, tuple[int, ...]], ...]) -> int:
        if next_idx == n and not active:
            return 0
        # All available slots filled at start of cycle.
        a = list(active)
        while len(a) < collectors and next_idx < n:
            a.append((next_idx, ds[next_idx])); next_idx += 1
        m = len(a)
        choices = []
        for b in range(banks):
            allocations = []
            for v in partitions(m, ports):
                if any(v[j] > a[j][1][b] for j in range(m)):
                    continue
                allocations.append(v)
            choices.append(allocations)
        best = 10**9
        for allocs in itertools.product(*choices):
            if not any(sum(x) for x in allocs):
                continue
            rem = []
            for j, (idx, d) in enumerate(a):
                updated = tuple(d[b] - allocs[b][j] for b in range(banks))
                if any(updated):
                    rem.append((idx, updated))
            best = min(best, 1 + solve(next_idx, tuple(rem)))
        return best
    return solve(0, ())


def analytic_extremes(demands, ports):
    sequential = sum(max((x + ports - 1)//ports for x in d) for d in demands)
    pooled = max((sum(d[b] for d in demands) + ports - 1)//ports for b in range(len(demands[0])))
    return sequential, pooled


def fixture(pairs):
    return '\n'.join(f'0 0 0 0 {i*16:04x} ffffffff 1 R9 IADD3 2 R{a} R{b} 0' for i,(a,b) in enumerate(pairs))


def experiment():
    # Same opcode, mask, instruction count, per-register histogram, total RF
    # demand, and number of source operands. Only the PAIRING differs.
    grouped = parse_trace(fixture([(0,2),(1,3)]))
    crossed = parse_trace(fixture([(0,1),(2,3)]))
    assert Counter(itertools.chain.from_iterable(grouped)) == Counter(itertools.chain.from_iterable(crossed))
    rows = []
    for banks, ports, collectors in itertools.product((2,4), (1,2), (1,2)):
        for name, instrs in [('grouped',grouped),('crossed',crossed)]:
            d = bank_demands(instrs,banks)
            seq,pool = analytic_extremes(d,ports)
            exact = optimal_cycles(d,collectors,ports)
            if collectors == 1: assert exact == seq
            if collectors >= len(instrs): assert exact == pool
            rows.append({'pairing':name,'banks':banks,'ports_per_bank':ports,
                         'collectors':collectors,'exact_read_service_cycles':exact,
                         'sequential_bound':seq,'fully_pooled_bound':pool})
    return {'evidence_tier':'synthetic_SASS_format_rows_exact_RF_service_only',
            'same_source_multiset':True,'rows':rows}


def selftest():
    assert len(parse_trace('31 0 0 3 0000 ffffffff 1 R1 IMAD.MOV.U32 2 R255 R255 0')) == 1
    assert parse_trace(fixture([(0,0)])) == [(0,)]
    x = fixture([(0,1)])
    mutants = [x.replace('ffffffff','00000000'), x.replace('IADD3','?BAD'),
               x.replace(' 2 R0 R1 0',' 3 R0 R1 0'), x.replace(' 2 R0 R1 0',' 2 R0 R1 4'),
               x.replace(' 2 R0 R1 0',' 2 R0 RX 0'), x.replace('0 0 0 0','-1 0 0 0'),
               x.replace(' 2 R0 R1 0',' 2 R0 R1 0 GARBAGE')]
    for bad in mutants:
        try: parse_trace(bad)
        except ValueError: pass
        else: raise AssertionError('mutant escaped: '+bad)
    # Independently verified exact formula in both extreme collector regimes.
    for banks in (2,3,4):
        for ports in (1,2):
            for regs in itertools.product(range(4), repeat=4):
                d = bank_demands([(regs[0],regs[1]),(regs[2],regs[3])],banks)
                seq,pool = analytic_extremes(d,ports)
                assert optimal_cycles(d,1,ports)==seq
                assert optimal_cycles(d,2,ports)==pool
    return {'mutation_tests':len(mutants),'exhaustive_reg_assignments':3*2*4**4}

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--selftest',action='store_true')
    args=p.parse_args()
    if args.selftest: print(json.dumps(selftest()))
    print(json.dumps(experiment(),indent=2))
