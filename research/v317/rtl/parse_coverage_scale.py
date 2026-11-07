"""Compare source-pinned *generic* coverage wrapper synthesis with matched
stateful RTL. Neither design is technology mapped, placed, or routed.
"""
import collections
import json
import pathlib
import re
import sys
from research.v317.rtl.parse_stateful_scale import parse as parse_base


def parse_wrapper(folder, lanes, bits, naive=False):
    tag = f"{lanes}x{bits}"
    prefix = "coverage_naive" if naive else "coverage"
    module = "vektor_v317_coverage_forwarding_naive" if naive else "vektor_v317_coverage_forwarding"
    netlist = json.loads((folder / f"{prefix}_{tag}.json").read_text())
    log = (folder / f"{prefix}_{tag}.log").read_text()
    mod = netlist["modules"][module]
    cells = mod["cells"]
    flops = sum(1 for cell in cells.values()
                if cell["type"].startswith(("$_DFF", "$_SDFF", "$_DFFE")))
    counts = [int(x) for x in re.findall(r"Number of cells:\s+(\d+)", log)]
    depths = [int(x) for x in re.findall(
        r"Longest topological path[^\n]*length=(\d+)", log)]
    if not counts or not depths or counts[-1] != len(cells):
        raise ValueError(f"missing or inconsistent Yosys evidence {tag}")
    fanout = collections.Counter()
    for cell in cells.values():
        for port, direction in cell["port_directions"].items():
            if direction == "input":
                fanout.update(bit for bit in cell["connections"][port]
                              if isinstance(bit, int))
    return {
        "generic_cells_total": len(cells),
        "generic_flop_cells": flops,
        "generic_comb_cells": len(cells) - flops,
        "generic_comb_logic_depth_proxy": depths[-1],
        "max_generic_net_fanout": max(fanout.values(), default=0),
    }


def main(folder):
    cases = []
    for lanes, bits in ((4, 8), (8, 16), (32, 32)):
        base = parse_base(folder, lanes, bits)
        wrapped = parse_wrapper(folder, lanes, bits)
        naive = parse_wrapper(folder, lanes, bits, naive=True)
        if lanes == 32 and wrapped["generic_cells_total"] >= naive["generic_cells_total"]:
            raise ValueError("single-mask factorization did not reduce 32x32 generic cells")
        if wrapped["generic_flop_cells"] < base["generic_flop_cells"] + 1:
            raise ValueError(f"missing coverage fault state {lanes}x{bits}")
        cases.append({
            "lanes": lanes, "bits_per_lane": bits,
            "base_stateful": base, "naive_double_mask": naive,
            "coverage_wrapped": wrapped,
            "optimized_vs_naive_cell_delta": wrapped["generic_cells_total"] - naive["generic_cells_total"],
            "generic_cell_delta": wrapped["generic_cells_total"] - base["generic_cells_total"],
            "generic_flop_delta": wrapped["generic_flop_cells"] - base["generic_flop_cells"],
        })
    return {
        "evidence_tier": "MATCHED_GENERIC_UNPLACED_YOSYS_ONLY",
        "unimplemented": ["independent monitor completeness detector",
                          "physical write-event network", "placement and routing",
                          "wire capacitance and electrical signoff"],
        "predicted_incremental_transactions_vs_equal_information_baseline": 0,
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(main(pathlib.Path(sys.argv[1])), sort_keys=True, indent=2))
