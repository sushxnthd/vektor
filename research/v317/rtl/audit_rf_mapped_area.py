"""V317 independent mapped-cell area and fanout stress audit.

Nangate45 library cell areas are *mapped* proxies; this is not STA, placement,
routing, extracted RC, measured clock, GPU IPC, or silicon power.
"""
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ALPHAS = (0.0, 0.05, 0.20, 0.50)
TOPS = (
    ("source_fixed", "vektor_rf_bank_arbiter"),
    ("pairwise_fixed", "vektor_v317_rf_pairwise"),
    ("source_rotating", "vektor_v317_rf_rotating"),
    ("pairwise_rotating", "vektor_v317_rf_pairwise_rotating"),
)


def liberty_areas(path):
    text = Path(path).read_text()
    markers = list(re.finditer(r"(?m)^\s*cell\s*\(\s*([\w]+)\s*\)\s*\{", text))
    if not markers:
        raise AssertionError("No Liberty cells found")
    areas = {}
    for i, marker in enumerate(markers):
        chunk = text[marker.end():markers[i + 1].start() if i + 1 < len(markers) else len(text)]
        found = re.search(r"\barea\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*;", chunk)
        if found:
            areas[marker.group(1)] = float(found.group(1))
    if not areas:
        raise AssertionError("No Liberty cell areas found")
    return areas


def is_bit(value):
    return isinstance(value, int)


def summarize(netlist, top, areas):
    data = json.loads(Path(netlist).read_text())
    module = data["modules"][top]
    cells = module["cells"]
    sinks = Counter()
    drivers = {}
    cell_inputs = {}
    cell_outputs = {}
    sequential = set()
    cell_area = 0.0
    types = Counter()

    for name, cell in cells.items():
        typ = cell["type"].lstrip("\\")
        if typ == "$scopeinfo":
            continue
        if typ not in areas:
            raise AssertionError("Unmapped or unknown cell: " + typ)
        directions = cell.get("port_directions", {})
        if not directions:
            raise AssertionError("Missing mapped port directions: " + typ)
        ins, outs = [], []
        for port, bits in cell["connections"].items():
            direction = directions.get(port)
            if direction not in ("input", "output", "inout"):
                raise AssertionError("Unknown port direction " + typ + "." + port)
            if direction in ("input", "inout"):
                ins.extend(b for b in bits if is_bit(b))
                sinks.update(b for b in bits if is_bit(b))
            if direction in ("output", "inout"):
                outs.extend(b for b in bits if is_bit(b))
        if not outs:
            raise AssertionError("Mapped cell without outputs: " + name)
        if any(b in drivers for b in outs):
            raise AssertionError("Multiple drivers on mapped net")
        for bit in outs:
            drivers[bit] = name
        cell_inputs[name] = ins
        cell_outputs[name] = outs
        if re.search(r"(?:^|_)DFF|SDFF|LATCH|DLH|DLL|LHQ|LHL", typ, re.I):
            sequential.add(name)
        types[typ] += 1
        cell_area += areas[typ]

    endpoints = []
    for port in module["ports"].values():
        if port["direction"] == "output":
            for bit in port["bits"]:
                if is_bit(bit):
                    endpoints.append(bit)
                    sinks[bit] += 1
    for name in sequential:
        endpoints.extend(cell_inputs[name])
    if not endpoints:
        raise AssertionError("No timing-proxy endpoints")

    cell_fanouts = {
        name: max((sinks[b] for b in outs), default=0)
        for name, outs in cell_outputs.items()
    }

    def path_stress(alpha):
        active = set()

        @lru_cache(maxsize=None)
        def visit(bit):
            name = drivers.get(bit)
            if name is None or name in sequential:
                return 0.0
            if bit in active:
                raise AssertionError("Combinational cycle")
            active.add(bit)
            predecessor = max((visit(b) for b in cell_inputs[name]), default=0.0)
            active.remove(bit)
            return predecessor + 1.0 + alpha * max(0, cell_fanouts[name] - 1)

        return max(visit(bit) for bit in endpoints)

    return {
        "cell_count": sum(types.values()),
        "mapped_cell_area_um2": round(cell_area, 4),
        "cell_types": dict(sorted(types.items())),
        "max_net_sink_fanout": max(sinks.values(), default=0),
        "total_pin_and_output_sinks": sum(sinks.values()),
        "fanout_weighted_logic_depth_proxy": {
            str(alpha): round(path_stress(alpha), 4) for alpha in ALPHAS
        },
        "flop_count": len(sequential),
    }


def compare(liberty, netlists):
    if len(netlists) != 4:
        raise ValueError("Provide four matched mapped JSON netlists")
    areas = liberty_areas(liberty)
    out = {}
    for (label, top), netlist in zip(TOPS, netlists):
        out[label] = summarize(netlist, top, areas)
    source_f = out["source_fixed"]["mapped_cell_area_um2"]
    pair_f = out["pairwise_fixed"]["mapped_cell_area_um2"]
    source_r = out["source_rotating"]["mapped_cell_area_um2"]
    pair_r = out["pairwise_rotating"]["mapped_cell_area_um2"]
    return {
        "evidence_tier": "NANGATE45_MAPPED_CELL_AREA_NOT_PLACED_OR_ROUTED",
        "configurations": out,
        "fixed_mapped_area_ratio": round(pair_f / source_f, 8),
        "rotating_mapped_area_ratio": round(pair_r / source_r, 8),
        "optimized_rotating_vs_fixed_area_ratio": round(pair_r / pair_f, 8),
        "frozen_fixed_area_prediction_survives": pair_f < source_f,
        "frozen_rotating_area_prediction_survives": pair_r < source_r,
        "identical_policy_intrinsic_service_gain": 1.0,
        "load_sensitivity_is_dimensionless_proxy": True,
        "timing_signoff": False,
        "routed_rc": False,
        "gpu_ipc_measured": False,
    }


if __name__ == "__main__":
    print(json.dumps(compare(sys.argv[1], sys.argv[2:]), indent=2, sort_keys=True))
