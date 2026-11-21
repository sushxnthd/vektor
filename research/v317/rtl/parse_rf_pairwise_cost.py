"""Matched generic synthesis audit for V317 pairwise bank-credit RTL.

No mapped delay, placement, wire RC, standard-cell area, power or GPU IPC claim.
"""
import json
import sys

from research.v317.rtl.parse_rf_exact_cost import summarize
from research.v317.rtl.parse_rf_rotating_cost import depth

TOPS = (
    ("source_fixed", "vektor_rf_bank_arbiter"),
    ("pairwise_fixed", "vektor_v317_rf_pairwise"),
    ("source_rotating", "vektor_v317_rf_rotating"),
    ("pairwise_rotating", "vektor_v317_rf_pairwise_rotating"),
)


def compare(paths):
    if len(paths) != 8:
        raise ValueError("need four ordered netlist/log pairs")
    out = {}
    for (label, top), (netlist, log) in zip(TOPS, zip(paths[::2], paths[1::2])):
        out[label] = {**summarize(netlist, top),
                      "generic_logic_levels": depth(log)}
    f0, f1 = out["source_fixed"], out["pairwise_fixed"]
    r0, r1 = out["source_rotating"], out["pairwise_rotating"]
    return {
        "evidence_tier": "MATCHED_GENERIC_YOSYS_NOT_MAPPED_OR_ROUTED",
        "configurations": out,
        "fixed_cell_ratio": f1["generic_cells"] / f0["generic_cells"],
        "rotating_cell_ratio": r1["generic_cells"] / r0["generic_cells"],
        "fixed_depth_delta": f1["generic_logic_levels"] - f0["generic_logic_levels"],
        "rotating_depth_delta": r1["generic_logic_levels"] - r0["generic_logic_levels"],
        "frozen_both_area_predictions_survive":
            f1["generic_cells"] < f0["generic_cells"]
            and r1["generic_cells"] < r0["generic_cells"],
        "physical_signoff": False,
        "gpu_ipc_measured": False,
    }


if __name__ == "__main__":
    print(json.dumps(compare(sys.argv[1:]), indent=2, sort_keys=True))
