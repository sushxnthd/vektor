"""Exact mapped-netlist gate-depth audit. Structural, not a timing/power estimate."""
import collections
import functools
import json
import re
import sys
from pathlib import Path

CELL = re.compile(r'^  (\\w+)\\s+(_\\d+_)\\s*\\(\\s*\\n(.*?)^  \\);', re.M | re.S)
PIN = re.compile(r'\\.(\\w+)\\((.*?)\\)', re.S)
OUT_PINS = {'ZN', 'Z', 'Y', 'CO'}

def analyze(path):
    raw = Path(path).read_text()
    drivers, gates, flops = {}, [], []
    for cell, name, body in CELL.findall(raw):
        pins = {k: v.strip() for k, v in PIN.findall(body)}
        if cell.startswith(('DFF', 'SDFF')):
            flops.append((name, pins))
            for port in ('Q', 'QN'):
                if port in pins:
                    assert pins[port] not in drivers
                    drivers[pins[port]] = ('flop', name, ())
        else:
            ins = tuple(v for k, v in pins.items() if k not in OUT_PINS)
            outs = tuple(v for k, v in pins.items() if k in OUT_PINS)
            assert outs, (cell, name)
            for net in outs:
                assert net not in drivers, ('multi_driver', net)
                drivers[net] = ('gate', name, ins)
            gates.append((name, ins, outs))
    for _, ins, _ in gates:
        for net in ins:
            assert not (net.startswith('_') and net not in drivers), ('undriven', net)

    @functools.lru_cache(None)
    def depth(net):
        if net not in drivers:
            return (0, 'input:' + net.split('[')[0])
        typ, name, ins = drivers[net]
        if typ == 'flop':
            return (0, 'flop:' + name)
        d, src = max((depth(i) for i in ins), key=lambda x: x[0])
        return d + 1, src

    rec = [(depth(pins['D'])[0], depth(pins['D'])[1], name)
           for name, pins in flops if 'D' in pins]
    # Independent iterative dynamic-programming implementation.
    known = {net: 0 for net, (typ, _, _) in drivers.items() if typ == 'flop'}
    all_ins = {n for _, ins, _ in gates for n in ins}
    known.update({n: 0 for n in all_ins if n not in drivers})
    remaining = list(gates)
    while remaining:
        nxt, progress = [], 0
        for name, ins, outs in remaining:
            if all(n in known for n in ins):
                value = max((known[n] for n in ins), default=0) + 1
                for net in outs:
                    known[net] = value
                progress += 1
            else:
                nxt.append((name, ins, outs))
        assert progress, ('cycle_or_unresolved', len(nxt))
        remaining = nxt
    assert all(d == known[pins['D']] for d, _, name in rec
               for nm, pins in flops if nm == name)
    groups = collections.defaultdict(list)
    for d, src, name in rec:
        groups[src.split(':')[0]].append(d)
    return {
        'evidence_class': 'exact mapped-netlist gate depth; not OpenSTA',
        'mapped_netlist': Path(path).name,
        'gate_count': len(gates),
        'flop_count': len(flops),
        'max_depth': max(d for d, _, _ in rec),
        'by_source': {k: {'max_depth': max(v), 'endpoints': len(v)}
                      for k, v in sorted(groups.items())},
        'independent_iterative_check': 'PASS',
        'top_paths': [{'depth': d, 'source': src, 'endpoint_flop': name}
                      for d, src, name in sorted(rec, reverse=True)[:5]],
    }

if __name__ == '__main__':
    print(json.dumps([analyze(p) for p in sys.argv[1:]], indent=2))
