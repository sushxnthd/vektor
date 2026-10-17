"""Exact mapped-netlist depth audit. Not a timing or silicon estimate."""
import collections
import functools
import json
import re
import sys
from pathlib import Path

CELL = re.compile(r'^  (\w+)\s+(_\d+_)\s*\(\s*\n(.*?)^  \);', re.M | re.S)
PIN = re.compile(r'\.(\w+)\((.*?)\)', re.S)
OUTPUTS = {'ZN', 'Z', 'Y', 'CO'}

def analyze(path):
    raw = Path(path).read_text()
    drivers, gates, flops = {}, [], []
    for typ, name, body in CELL.findall(raw):
        pins = {k: v.strip() for k, v in PIN.findall(body)}
        if typ.startswith(('DFF', 'SDFF')):
            flops.append((name, pins))
            for port in ('Q', 'QN'):
                if port in pins:
                    assert pins[port] not in drivers
                    drivers[pins[port]] = ('flop', name, ())
        else:
            ins = tuple(v for k, v in pins.items() if k not in OUTPUTS)
            outs = tuple(v for k, v in pins.items() if k in OUTPUTS)
            assert outs
            for net in outs:
                assert net not in drivers
                drivers[net] = ('gate', name, ins)
            gates.append((name, ins, outs))
    for _, ins, _ in gates:
        for net in ins:
            assert not (net.startswith('_') and net not in drivers), ('undriven', net)

    @functools.lru_cache(None)
    def depth(net):
        if net not in drivers:
            return 0, 'input:' + net.split('[')[0]
        typ, name, ins = drivers[net]
        if typ == 'flop':
            return 0, 'flop:' + name
        d, source = max((depth(i) for i in ins), key=lambda x: x[0])
        return d + 1, source

    rec = [(depth(pins['D'])[0], depth(pins['D'])[1], name)
           for name, pins in flops if 'D' in pins]
    # Independent iterative traversal checks all flop-input depths.
    known = {net: 0 for net, (typ, _, _) in drivers.items() if typ == 'flop'}
    all_inputs = {net for _, ins, _ in gates for net in ins}
    known.update({net: 0 for net in all_inputs if net not in drivers})
    remaining = list(gates)
    while remaining:
        nxt, progress = [], 0
        for name, ins, outs in remaining:
            if all(net in known for net in ins):
                level = max((known[net] for net in ins), default=0) + 1
                for net in outs:
                    known[net] = level
                progress += 1
            else:
                nxt.append((name, ins, outs))
        assert progress, ('unresolved_or_cyclic', len(nxt))
        remaining = nxt
    for name, pins in flops:
        if 'D' in pins:
            assert depth(pins['D'])[0] == known[pins['D']]
    groups = collections.defaultdict(list)
    for d, source, _ in rec:
        groups[source.split(':')[0]].append(d)
    return {
        'evidence_class': 'exact structural mapped-gate depth; not STA',
        'netlist': Path(path).name,
        'gate_count': len(gates), 'flop_count': len(flops),
        'max_depth': max(d for d, _, _ in rec),
        'by_source': {k: {'max_depth': max(v), 'endpoints': len(v)}
                      for k, v in sorted(groups.items())},
        'independent_iterative_check': 'PASS',
        'top_paths': [{'depth': d, 'source': src, 'endpoint_flop': name}
                      for d, src, name in sorted(rec, reverse=True)[:5]]
    }

if __name__ == '__main__':
    print(json.dumps([analyze(p) for p in sys.argv[1:]], indent=2))
