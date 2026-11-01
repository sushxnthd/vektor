"""Independent V317 Nangate45 mapped-netlist maximum-capacitance audit.

Pre-route cell-pin load only. No placement, wire RC, or electrical signoff.
Fail closed on unknown cells, pins, drivers, aliases, or Liberty attributes.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

IDENT = r"[\\A-Za-z_$][\\A-Za-z0-9_$]*"
NUM = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
CELL = re.compile(r"\bcell\s*\(\s*\"?([A-Za-z0-9_]+)\"?\s*\)\s*\{")
PIN = re.compile(r"\bpin\s*\(\s*\"?([A-Za-z0-9_]+)\"?\s*\)\s*\{")
ATTR = lambda name: re.compile(r"\b" + name + r"\s*:\s*(" + NUM + r")\s*;")
DIR = re.compile(r"\bdirection\s*:\s*(input|output|inout)\s*;")


def block(text, start):
    depth = 1
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    raise ValueError("unterminated Liberty block")


def attr(text, name):
    match = ATTR(name).search(text)
    return float(match.group(1)) if match else None


def liberty_pins(text):
    units = re.search(r"\bcapacitive_load_unit\s*\(\s*1\s*,\s*ff\s*\)", text, re.I)
    if not units:
        raise ValueError("expected pinned Nangate45 capacitance unit 1 fF")
    result = {}
    for cm in CELL.finditer(text):
        body = block(text, cm.end())
        pins = {}
        for pm in PIN.finditer(body):
            pb = block(body, pm.end())
            dm = DIR.search(pb)
            if not dm:
                # Liberty also describes internal state pins (e.g. IQ) with no
                # physical input/output direction. They cannot be cell ports.
                # If a mapped netlist references one, strict pin-set validation fails.
                continue
            pins[pm.group(1)] = {
                "direction": dm.group(1),
                "cap_ff": attr(pb, "capacitance"),
                "max_cap_ff": attr(pb, "max_capacitance"),
            }
        if pins:
            result[cm.group(1)] = pins
    if not result:
        raise ValueError("no Liberty cells")
    return result


def widths(netlist):
    out = {}
    for m in re.finditer(r"(?m)^\s*(?:input|output|wire)\s+(?:wire\s+)?(?:\[(\d+)\s*:\s*(\d+)\]\s+)?([^;]+);", netlist):
        hi, lo, names = m.groups()
        indices = [None] if hi is None else list(range(min(int(hi), int(lo)), max(int(hi), int(lo)) + 1))
        for name in names.split(","):
            name = name.strip()
            if re.fullmatch(IDENT, name):
                out[name] = indices
    return out


def bits(expr, width_map):
    expr = expr.strip()
    if expr.startswith("{") and expr.endswith("}"):
        parts = expr[1:-1].split(",")
        result = []
        for part in reversed(parts):
            result.extend(bits(part, width_map))
        return result
    if re.fullmatch(r"\d+'[bhd][0-9a-fA-F_xXzZ]+", expr):
        # Constants are not load-bearing signal nets.
        size = int(expr.split("'")[0])
        return [None] * size
    if re.fullmatch(r"1'[bB][01xXzZ]", expr):
        return [None]
    slice_match = re.fullmatch("(" + IDENT + r")\[(\d+):(\d+)\]", expr)
    if slice_match:
        name, hi, lo = slice_match.groups()
        return [f"{name}[{i}]" for i in range(min(int(hi), int(lo)), max(int(hi), int(lo)) + 1)]
    if re.fullmatch(IDENT + r"\[\d+\]", expr):
        return [expr.replace(" ", "")]
    if re.fullmatch(IDENT, expr):
        if expr not in width_map:
            # Undeclared escaped wires are scalar only.
            return [expr]
        idx = width_map[expr]
        return [expr] if idx == [None] else [f"{expr}[{i}]" for i in idx]
    raise ValueError(f"unsupported net expression {expr!r}")


class Union:
    def __init__(self):
        self.parent = {}

    def root(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.root(self.parent[x])
        return self.parent[x]

    def join(self, a, b):
        if a is not None and b is not None:
            self.parent[self.root(a)] = self.root(b)


def parse_netlist(text, pins):
    w = widths(text)
    aliases = Union()
    for m in re.finditer(r"\bassign\s+([^=;]+?)\s*=\s*([^;]+);", text):
        left, right = bits(m.group(1), w), bits(m.group(2), w)
        if len(left) != len(right):
            raise ValueError(f"assign width mismatch: {m.group(0)}")
        for a, b in zip(left, right):
            aliases.join(a, b)
    # Yosys emits named Liberty pin instances, not positional connections.
    inst = re.compile(r"(?ms)^\s*([A-Za-z_][A-Za-z0-9_$]*)\s+([\\A-Za-z_$][\\A-Za-z0-9_$]*)\s*\(\s*(\.[\s\S]*?)\s*\)\s*;")
    sink_loads = defaultdict(float)
    drivers = defaultdict(list)
    instances = 0
    for m in inst.finditer(text):
        cell, name, body = m.groups()
        if cell not in pins:
            raise ValueError(f"unknown mapped cell {cell} ({name})")
        pairs = re.findall(r"\.([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*([^()]*)\s*\)", body)
        if not pairs or len(pairs) != body.count("."):
            raise ValueError(f"unsupported cell pin syntax {cell}/{name}")
        if len({p for p, _ in pairs}) != len(pairs):
            raise ValueError(f"duplicate pin {cell}/{name}")
        if set(p for p, _ in pairs) != set(pins[cell]):
            raise ValueError(f"missing/extra mapped pins {cell}/{name}")
        instances += 1
        for pin, expr in pairs:
            meta = pins[cell][pin]
            signal = bits(expr, w)
            if len(signal) != 1:
                raise ValueError(f"non-scalar cell pin {cell}/{name}/{pin}")
            net = signal[0]
            if net is None:
                continue
            net = aliases.root(net)
            if meta["direction"] == "input":
                if meta["cap_ff"] is None:
                    raise ValueError(f"missing input capacitance {cell}/{pin}")
                sink_loads[net] += meta["cap_ff"]
            elif meta["direction"] == "output":
                if meta["max_cap_ff"] is None:
                    raise ValueError(f"missing output max-capacitance {cell}/{pin}")
                drivers[net].append((cell, name, pin, meta["max_cap_ff"]))
            else:
                raise ValueError(f"unsupported bidirectional cell pin {cell}/{pin}")
    if instances == 0:
        raise ValueError("no mapped instances")
    return w, aliases, sink_loads, drivers, instances


def audit_core(netlist, lib, drive, external_ff, grant_width=4):
    if drive not in lib or "A" not in lib[drive] or "Z" not in lib[drive]:
        raise ValueError(f"missing output buffer {drive}")
    buf_in = lib[drive]["A"]["cap_ff"]
    buf_max = lib[drive]["Z"]["max_cap_ff"]
    if buf_in is None or buf_max is None:
        raise ValueError("buffer Liberty pin capacitance/max_capacitance missing")
    w, aliases, sinks, drivers, count = parse_netlist(netlist, lib)
    for bit in range(grant_width):
        grant = aliases.root(f"grant[{bit}]")
        if grant not in drivers:
            raise ValueError(f"no mapped driver for grant[{bit}] (alias={grant}, mapped_driver_count={len(drivers)}, assignments={[m.group(0) for m in re.finditer(r\'\\bassign\\s+[^;]+;\', netlist) if \'grant\' in m.group(0)][:8]})")
        sinks[grant] += buf_in
    rows = []
    for net, ds in drivers.items():
        if len(ds) != 1:
            raise ValueError(f"multiple mapped drivers on {net}: {ds}")
        cell, instance, pin, limit = ds[0]
        cap = sinks[net]
        rows.append({"net": net, "cell": cell, "instance": instance, "pin": pin,
                     "load_ff": round(cap, 6), "max_cap_ff": limit,
                     "margin_ff": round(limit - cap, 6), "legal": cap <= limit + 1e-9})
    rows.sort(key=lambda x: (x["margin_ff"], x["net"]))
    # The four output buffer instances have separate external pin loads.
    external = {"buffer": drive, "load_ff": external_ff, "max_cap_ff": buf_max,
                "margin_ff": round(buf_max - external_ff, 6),
                "legal": external_ff <= buf_max + 1e-9}
    return {"mapped_instances": count, "mapped_output_nets": len(rows),
            "internal_violations": [r for r in rows if not r["legal"]],
            "worst_internal": rows[:10], "output_buffer": external,
            "all_max_cap_legal": external["legal"] and all(r["legal"] for r in rows),
            "evidence_tier": "pre-route cell-pin capacitance only, no wire parasitics"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("liberty", type=Path)
    p.add_argument("source_netlist", type=Path)
    p.add_argument("pairwise_netlist", type=Path)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    lib = liberty_pins(args.liberty.read_text())
    results = {}
    for name, path in (("source", args.source_netlist), ("pairwise", args.pairwise_netlist)):
        results[name] = {}
        for drive, load in (("BUF_X1", 24), ("BUF_X2", 100), ("BUF_X1", 100)):
            key = f"{drive}_{load}ff"
            results[name][key] = audit_core(path.read_text(), lib, drive, load)
    frozen = {
        "BUF_X1_24ff_output_legal": all(results[n]["BUF_X1_24ff"]["output_buffer"]["legal"] for n in results),
        "BUF_X2_100ff_output_legal": all(results[n]["BUF_X2_100ff"]["output_buffer"]["legal"] for n in results),
        "BUF_X1_100ff_output_illegal": all(not results[n]["BUF_X1_100ff"]["output_buffer"]["legal"] for n in results),
    }
    print(json.dumps({"frozen_predictions": frozen, "results": results}, indent=2, sort_keys=True))
    if not all(frozen.values()):
        raise SystemExit("frozen output-pin predictions failed")
    # Internal failures are retained as scientific negative results, not hidden.
    if any(not results[n][f"{d}_{l}ff"]["all_max_cap_legal"]
           for n in results for d, l in (("BUF_X1", 24), ("BUF_X2", 100))):
        raise SystemExit("mapped-netlist max-capacitance violation: physical gate FAILED")


if __name__ == "__main__":
    main()
