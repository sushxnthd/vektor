"""Parse source-pinned generic Yosys evidence for the *complete stateful* gate.

No technology-mapped area, routed delay, physical power, RF macro or GPU
throughput can be inferred from these generic counts.
"""
import collections
import json
import pathlib
import re
import sys


def parse(folder, lanes, bits):
    tag = f"{lanes}x{bits}"
    netlist = json.loads((folder / f"stateful_{tag}.json").read_text())
    log = (folder / f"stateful_{tag}.log").read_text()
    mod = netlist["modules"]["vektor_v317_stateful_forwarding"]
    cells = mod["cells"]
    flop = sum(1 for cell in cells.values()
               if cell["type"].startswith(("$_DFF", "$_SDFF", "$_DFFE")))
    counts = [int(x) for x in re.findall(r"Number of cells:\s+(\d+)", log)]
    depths = [int(x) for x in re.findall(
        r"Longest topological path[^\n]*length=(\d+)", log)]
    if not counts or not depths or counts[-1] != len(cells):
        raise ValueError(f"missing or inconsistent Yosys evidence {tag}")
    if flop < lanes * bits:
        raise ValueError(f"missing source snapshot state {tag}: {flop} flops")
    fanout = collections.Counter()
    for cell in cells.values():
        for port, direction in cell["port_directions"].items():
            if direction == "input":
                fanout.update(bit for bit in cell["connections"][port]
                              if isinstance(bit, int))
    return {
        "lanes": lanes, "bits_per_lane": bits,
        "snapshot_data_bits": lanes * bits,
        "generic_cells_total": len(cells),
        "generic_flop_cells": flop,
        "generic_comb_cells": len(cells) - flop,
        "generic_comb_logic_depth_proxy": depths[-1],
        "max_generic_net_fanout": max(fanout.values(), default=0)
    }


def main(folder):
    cases = [parse(folder, a, b) for a, b in ((4,8),(8,16),(32,32))]
    return {
        "evidence_tier": "GENERIC_UNPLACED_SYNTHESIS_ONLY",
        "limitations": [
            "No standard-cell mapping, wire parasitics or electrical signoff",
            "External write-event broadcast, RF interface and cache tags not costed",
            "Same-information forwarding baseline has zero incremental benefit",
        ],
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(main(pathlib.Path(sys.argv[1])), sort_keys=True, indent=2))
