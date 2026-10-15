#!/usr/bin/env python3
"""Detect the known OpenSTA 2.0.17 concatenated-LHS netlist incompatibility.

This is a narrow preflight, NOT a complete Verilog syntax check or STA.
"""
import argparse
import json
import re
from pathlib import Path


def audit(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    hazards = []
    for line_number, line in enumerate(lines, 1):
        if re.match(r"^\s*assign\s*\{", line):
            hazards.append({
                "line": line_number,
                "kind": "concatenated_assignment_lhs",
                "excerpt": line.strip()[:200],
            })
    return {
        "path": str(path),
        "lines": len(lines),
        "hazard_count": len(hazards),
        "hazards": hazards,
        "passes_known_opensta_lhs_gate": not hazards,
        "caveat": "Not a complete Verilog syntax checker or STA run",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("netlists", nargs="+", type=Path)
    args = parser.parse_args()
    results = [audit(p) for p in args.netlists]
    print(json.dumps({"results": results}, indent=2))
    raise SystemExit(0 if all(r["passes_known_opensta_lhs_gate"] for r in results) else 2)


if __name__ == "__main__":
    main()
