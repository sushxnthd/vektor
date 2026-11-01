"""Summarize matched Yosys generic netlists for the V317 arbiter challenger.

Only generic cell count, sequential cell count, and per-net sink fanout are
reported. This is NOT standard-cell area, placement, routed delay or power.
"""
from collections import Counter
import json
import sys


def summarize(path, top):
    with open(path, encoding="utf-8") as f:
        design = json.load(f)
    module = design["modules"][top]
    cells = module["cells"]
    types = Counter(c["type"] for c in cells.values())
    sinks = Counter()
    for cell in cells.values():
        for port, bits in cell["connections"].items():
            if cell.get("port_directions", {}).get(port) == "input":
                for bit in bits:
                    if isinstance(bit, int):
                        sinks[bit] += 1
    return {
        "generic_cells": len(cells),
        "flip_flops": sum(n for t, n in types.items() if "DFF" in t.upper()),
        "max_generic_net_sink_fanout": max(sinks.values(), default=0),
        "cell_types": dict(sorted(types.items())),
    }


def main():
    baseline = summarize(sys.argv[1], "vektor_rf_bank_arbiter")
    exact = summarize(sys.argv[2], "vektor_v317_rf_bank_exact")
    ratio = exact["generic_cells"] / max(1, baseline["generic_cells"])
    result = {
        "evidence_tier": "MATCHED_GENERIC_YOSYS_NOT_ROUTED_TIMING",
        "baseline": baseline,
        "exact_challenger": exact,
        "exact_to_priority_generic_cell_ratio": ratio,
        "physical_signoff": False,
        "workload_throughput_measured": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
