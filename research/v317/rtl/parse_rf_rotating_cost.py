"""Three-way source-pinned generic RTL comparison; never a routed PPA claim."""
import json
import re
import sys
from research.v317.rtl.parse_rf_exact_cost import summarize


def depth(logfile):
    text = open(logfile, encoding="utf-8").read()
    matches = re.findall(r"Longest topological path in .*?\(length=(\d+)\)", text)
    if len(matches) != 1:
        raise ValueError(f"Expected one Yosys LTP result in {logfile}; found {matches}")
    return int(matches[0])


def compare(paths):
    names = (
        ("fixed_priority", "vektor_rf_bank_arbiter"),
        ("rotating_priority", "vektor_v317_rf_rotating"),
        ("exact_cardinality", "vektor_v317_rf_bank_exact"),
    )
    out = {}
    for (name, top), (netlist, log) in zip(names, paths):
        out[name] = {**summarize(netlist, top), "generic_logic_levels": depth(log)}
    b, r, e = out["fixed_priority"], out["rotating_priority"], out["exact_cardinality"]
    return {
        "evidence_tier": "MATCHED_GENERIC_YOSYS_NOT_PLACED_ROUTED_OR_TIMED",
        "configurations": out,
        "rotating_to_fixed_cell_ratio": r["generic_cells"] / b["generic_cells"],
        "exact_to_fixed_cell_ratio": e["generic_cells"] / b["generic_cells"],
        "rotating_smaller_and_shallower_than_exact": (
            r["generic_cells"] < e["generic_cells"]
            and r["generic_logic_levels"] < e["generic_logic_levels"]
        ),
        "physical_signoff": False,
        "gpu_ipc_measured": False,
    }


if __name__ == "__main__":
    if len(sys.argv) != 7:
        raise SystemExit("Usage: python -m research.v317.rtl.parse_rf_rotating_cost fixed.json fixed.log rotating.json rotating.log exact.json exact.log")
    args = list(zip(sys.argv[1::2], sys.argv[2::2]))
    print(json.dumps(compare(args), indent=2, sort_keys=True))
