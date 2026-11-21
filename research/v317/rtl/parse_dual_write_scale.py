"""Independent parser for matched one-/two-write-port generic synthesis.

Checks source-pinned Yosys JSON against log totals; computes generic fanout,
flop count and logic-depth proxy. These are not routed electrical metrics.
"""
import collections
import json
import pathlib
import re
import sys


def read_case(folder, prefix, lanes, bits):
    tag = f"{lanes}x{bits}"
    mod_name = ("vektor_v317_coverage_forwarding" if prefix == "oneport"
                else "vektor_v317_dual_write_forwarding")
    netlist = json.loads((folder / f"{prefix}_{tag}.json").read_text())
    log = (folder / f"{prefix}_{tag}.log").read_text()
    cells = netlist["modules"][mod_name]["cells"]
    counts = [int(x) for x in re.findall(r"Number of cells:\s+(\d+)", log)]
    depths = [int(x) for x in re.findall(
        r"Longest topological path[^\n]*length=(\d+)", log)]
    if not counts or counts[-1] != len(cells) or not depths:
        raise ValueError(f"missing/mismatched generic synthesis: {prefix} {tag}")
    flop = sum(cell["type"].startswith(("$_DFF", "$_SDFF", "$_DFFE"))
               for cell in cells.values())
    if flop < lanes * bits:
        raise ValueError(f"missing snapshot storage: {prefix} {tag}")
    fanout = collections.Counter()
    for cell in cells.values():
        for port, direction in cell["port_directions"].items():
            if direction == "input":
                fanout.update(bit for bit in cell["connections"][port]
                              if isinstance(bit, int))
    return {
        "cells": len(cells),
        "flops": flop,
        "generic_logic_depth": depths[-1],
        "max_generic_net_fanout": max(fanout.values(), default=0),
    }


def main(folder):
    rows = []
    for lanes, bits in ((4, 8), (8, 16), (32, 32)):
        one = read_case(folder, "oneport", lanes, bits)
        two = read_case(folder, "twoport", lanes, bits)
        if one["flops"] != two["flops"]:
            raise ValueError(f"storage mismatch: {lanes}x{bits}")
        if two["cells"] <= one["cells"]:
            raise ValueError(f"unexpected missing second-port logic: {lanes}x{bits}")
        rows.append({
            "lanes": lanes,
            "data_bits": bits,
            "one_port": one,
            "two_port": two,
            "additional_generic_cells": two["cells"] - one["cells"],
            "additional_generic_cell_fraction":
                (two["cells"] - one["cells"]) / one["cells"],
            "extra_generic_logic_depth":
                two["generic_logic_depth"] - one["generic_logic_depth"],
        })
    return {
        "evidence_tier": "MATCHED_GENERIC_YOSYS_NOT_ROUTED_PHYSICAL",
        "comparison_caveat": "One-port wrapper is an intentionally incomplete integration control for two physical write ports; not a functionally equal alternative.",
        "same_information_incremental_read_saving": 0,
        "cases": rows,
    }


if __name__ == "__main__":
    print(json.dumps(main(pathlib.Path(sys.argv[1])), sort_keys=True, indent=2))
