"""Read Yosys generic netlists; count logic cells, levels and net fanout.

No library area, physical capacitance, routed delay, power or RF storage is inferred.
"""
import collections
import json
import pathlib
import re
import sys


def parse_case(folder, lanes, bits):
    tag = f"{lanes}x{bits}"
    log = (folder / f"synth_{tag}.log").read_text()
    obj = json.loads((folder / f"synth_{tag}.json").read_text())
    mod = obj["modules"]["vektor_v317_forwarding_gate"]
    counts = [int(x) for x in re.findall(r"Number of cells:\s+(\d+)", log)]
    depths = [int(x) for x in re.findall(r"Longest topological path[^\n]*length=(\d+)", log)]
    if not counts or not depths:
        raise ValueError(f"missing Yosys cell/depth evidence for {tag}")
    fanout = collections.Counter()
    for cell in mod["cells"].values():
        for port, direction in cell["port_directions"].items():
            if direction == "input":
                fanout.update(bit for bit in cell["connections"][port]
                              if isinstance(bit, int))
    grant_bit = mod["ports"]["forward_grant"]["bits"][0]
    assert len(mod["ports"]["forwarded_data"]["bits"]) == lanes * bits
    assert counts[-1] == len(mod["cells"])
    return {"lanes": lanes, "data_bits_per_lane": bits,
            "data_bus_bits": lanes * bits,
            "generic_cells": counts[-1], "generic_logic_depth": depths[-1],
            "max_generic_net_fanout": max(fanout.values(), default=0),
            "forward_grant_net_fanout": fanout[grant_bit],
            "cell_count_per_data_bit": round(counts[-1] / (lanes * bits), 6)}


def audit(folder):
    return {"evidence_tier": "GENERIC_YOSYS_LOGIC_FANOUT_PROXY_ONLY",
            "limitations": "No buffers, placement, extracted capacitance, timing, power or source-buffer cost",
            "cases": [parse_case(folder, a, b) for a, b in ((4, 8), (8, 16), (32, 32))]}


if __name__ == "__main__":
    print(json.dumps(audit(pathlib.Path(sys.argv[1])), sort_keys=True, indent=2))
