#!/usr/bin/env python3
"""Fail-closed same-library mapped-area and flop-accounting gate."""
import argparse
import json
import re
from pathlib import Path

NAMES = ("decoded_pairwise", "decoded_serial", "fixed_pairwise", "fixed_serial")
AREA_RE = re.compile(r"Chip area for module[^:\n]*:\\s*([0-9]+(?:\\.[0-9]+)?)")
CELL_RE = re.compile(r"^\\s*(?:([A-Za-z_][A-Za-z_0-9]*)\\s+(\\d+)|(\\d+)\\s+([A-Za-z_][A-Za-z_0-9]*))\\s*$", re.M)

def parse(s):
    a = AREA_RE.findall(s)
    if not a:
        raise ValueError("Missing mapped cell area")
    area = float(a[-1])
    if not 0 < area < 30000:
        raise ValueError("Invalid mapped cell area")
    # Yosys stat formats differ between versions; accept both column orders.
    cells = {}
    for m in CELL_RE.finditer(s):
        name, count = (m[1], m[2]) if m[1] is not None else (m[4], m[3])
        if "DFF" in name.upper() or "SDFF" in name.upper():
            cells[name] = int(count)
    flops = sum(cells.values())
    if flops <= 0:
        raise ValueError("Missing mapped sequential cells")
    return {"area_um2": area, "flops": flops, "flop_cells": cells}

def evaluate(logs):
    rows = {n: parse(logs[n]) for n in NAMES}
    if len({rows[n]["flops"] for n in NAMES}) != 1:
        raise ValueError("Sequential-state mismatch")
    if rows["fixed_pairwise"]["flops"] != 388:
        raise ValueError("Unexpected sequential state; prior frozen reference is 388")
    ratios = {s: rows["fixed_" + s]["area_um2"] / rows["decoded_" + s]["area_um2"]
              for s in ("pairwise", "serial")}
    ok = all(v <= 1.10 for v in ratios.values())
    return {"decision": "MAPPED_AREA_GATE_PASS_NOT_PHYSICAL" if ok else "MAPPED_AREA_GATE_FAIL",
            "areas": rows, "area_ratios": ratios,
            "physically_feasible": False, "gpu_speedup_claim": False}

def self_test():
    fake = "Chip area for module \\test: 100.000\n    DFFR_X1 388\n"
    assert parse(fake)["flops"] == 388
    logs = {n: fake for n in NAMES}
    assert evaluate(logs)["decision"] == "MAPPED_AREA_GATE_PASS_NOT_PHYSICAL"
    logs["fixed_serial"] = "Chip area for module \\test: 111.000\n DFFR_X1 388\n"
    assert evaluate(logs)["decision"] == "MAPPED_AREA_GATE_FAIL"
    for bad in ("Chip area for module \\test: 10\n", "DFFR_X1 388\n"):
        try:
            parse(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted incomplete synthesis evidence")
    print("V296_FIXED_WORD_MAPPED_AUDIT_SELFTEST_PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--log-dir", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.log_dir:
        result = evaluate({n: (a.log_dir / (n + ".log")).read_text() for n in NAMES})
        print(json.dumps(result, sort_keys=True, indent=2))
        if a.output:
            a.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        if result["decision"] != "MAPPED_AREA_GATE_PASS_NOT_PHYSICAL":
            raise SystemExit(2)
    if not a.self_test and not a.log_dir:
        p.error("Choose --self-test and/or --log-dir")
