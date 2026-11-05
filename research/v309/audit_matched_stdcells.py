#!/usr/bin/env python3
"""Independent mapped-standard-cell area and load-proxy audit; not STA."""
import collections
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("build/v309_max_subset/standard_cells")
DESIGNS = {
    "original_greedy": "vektor_rf_bank_arbiter",
    "compact_greedy": "vektor_v309_compact_greedy_arbiter",
    "factored_exact_max": "vektor_v309_factored_subset_arbiter",
}
EXPECTED_PORTS = {
    "request_valid": ("input", 4),
    "src0_bank_flat": ("input", 16),
    "src1_bank_flat": ("input", 16),
    "grant": ("output", 4),
}
FROZEN_LIB_BLOB_SHA = "90e4afb274cfc6514c587c434c77903d554117d1"


def inspect(name, module_name):
    raw = json.loads((ROOT / (name + ".json")).read_text())
    modules = raw["modules"]
    if module_name not in modules:
        raise AssertionError(f"mapped module absent: {module_name}")
    top = modules[module_name]
    ports = {key: (value["direction"], len(value["bits"]))
             for key, value in top["ports"].items()}
    if ports != EXPECTED_PORTS:
        raise AssertionError(f"{name}: mismatched resource/port contract: {ports}")
    cells = top.get("cells", {})
    if not cells:
        raise AssertionError(f"{name}: empty mapped netlist")
    kinds = collections.Counter()
    fanout = collections.Counter()
    for instance in cells.values():
        typ = instance["type"]
        if typ.startswith("$") or typ not in modules:
            raise AssertionError(f"{name}: unmapped or unknown cell {typ}")
        kinds[typ] += 1
        directions = instance.get("port_directions", {})
        for pin, bits in instance["connections"].items():
            if pin not in directions:
                raise AssertionError(f"{name}: missing direction for {typ}.{pin}")
            if directions[pin] == "input":
                for bit in bits:
                    if isinstance(bit, int):
                        fanout[bit] += 1
    log = (ROOT / (name + ".log")).read_text()
    areas = re.findall(r"Chip area for module[^\n]*?:\s*([0-9]+(?:\.[0-9]+)?)", log)
    if not areas:
        raise AssertionError(f"{name}: standard-cell area not reported")
    area = float(areas[-1])
    if not (area > 0):
        raise AssertionError(f"{name}: nonpositive mapped area")
    return {
        "standard_cell_area_library_units": area,
        "mapped_cells": len(cells),
        "cell_types": dict(sorted(kinds.items())),
        "maximum_cell_input_fanout": max(fanout.values(), default=0),
        "nets_with_more_than_four_cell_input_pins": sum(x > 4 for x in fanout.values()),
        "electrical_timing_signoff": False,
    }


def main():
    lib = ROOT / "NangateOpenCellLibrary_typical.lib"
    if not lib.is_file():
        raise AssertionError("missing pinned standard-cell liberty")
    rows = {name: inspect(name, module)
            for name, module in DESIGNS.items()}
    compact = rows["compact_greedy"]["standard_cell_area_library_units"]
    factored = rows["factored_exact_max"]["standard_cell_area_library_units"]
    ratio = factored / compact
    out = {
        "evidence_tier": "matched_liberty_synthesis_only_not_placed_or_routed",
        "frozen_upstream_git_blob_sha": FROZEN_LIB_BLOB_SHA,
        "liberty_sha256": hashlib.sha256(lib.read_bytes()).hexdigest(),
        "matched_resource_contract": EXPECTED_PORTS,
        "designs": rows,
        "factored_to_compact_mapped_area_ratio": ratio,
        "frozen_max_mapped_area_ratio": 2.0,
        "standard_cell_area_gate": "PASS" if ratio <= 2.0 else "FAIL_KILL_FACTORED_RTL",
        "fanout_is_proxy_not_capacitance_or_slew_check": True,
        "physical_timing_power_or_gpu_speedup_claimed": False,
    }
    (ROOT / "independent_summary.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    if ratio > 2.0:
        sys.exit("FROZEN_STDCELL_AREA_FAIL: kill factored exact-max implementation")


if __name__ == "__main__":
    main()
