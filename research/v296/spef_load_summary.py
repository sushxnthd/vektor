#!/usr/bin/env python3
"""Read-only six-case SPEF net-load summary. NOT a slew-violator classifier."""
import hashlib
import json
from pathlib import Path
import re
import sys

VARIANTS = ("original", "optimized", "pairwise")
SCENARIOS = ("nominal", "high")


def parse_spef(text):
    if not re.search(r"(?m)^\*C_UNIT\s+1\s+PF\s*$", text):
        raise ValueError("Expected SPEF net capacitances in pF")
    header = text.split("*D_NET", 1)[0]
    name_map = dict(re.findall(r"(?m)^\*(\d+)\s+(\S+)\s*$", header))
    rows = []
    pat = r"(?ms)^\*D_NET\s+(\S+)\s+([\d.eE+\-]+)\s*\n(.*?)^\*END\s*$"
    for match in re.finditer(pat, text):
        ref, cap, body = match.groups()
        if "*CONN" not in body or "*CAP" not in body:
            raise ValueError("Malformed SPEF net connection/capacitance block")
        conn = body.split("*CONN", 1)[1].split("*CAP", 1)[0]
        inputs = len(re.findall(r"(?m)^\*I\s+\S+\s+I\b", conn))
        outputs = len(re.findall(r"(?m)^\*I\s+\S+\s+O\b", conn))
        name = name_map.get(ref[1:], ref) if ref.startswith("*") else ref
        rows.append({"net": name, "declared_total_cap_pf": float(cap),
                     "cell_input_connections": inputs, "cell_output_connections": outputs})
    if not rows:
        raise ValueError("No SPEF D_NET records")
    return rows


def summary(path):
    raw = path.read_bytes()
    rows = parse_spef(raw.decode("utf-8"))
    ordered = sorted(rows, key=lambda x: x["declared_total_cap_pf"], reverse=True)
    return {
        "spef_sha256": hashlib.sha256(raw).hexdigest(),
        "net_count": len(rows),
        "sum_declared_net_cap_pf": round(sum(x["declared_total_cap_pf"] for x in rows), 9),
        "max_declared_net_cap_pf": ordered[0]["declared_total_cap_pf"],
        "max_cell_input_connections_per_net": max(x["cell_input_connections"] for x in rows),
        "sum_cell_input_connections": sum(x["cell_input_connections"] for x in rows),
        "nets_with_at_least_32_cell_input_connections": sum(x["cell_input_connections"] >= 32 for x in rows),
        "top_capacitance_nets": ordered[:12],
    }


def audit(root):
    cases = {}
    for scenario in SCENARIOS:
        cases[scenario] = {}
        for variant in VARIANTS:
            path = root / f"{variant}.{scenario}.detail.spef"
            if not path.is_file() or not path.stat().st_size:
                raise ValueError(f"Missing extracted SPEF: {path}")
            cases[scenario][variant] = summary(path)
    high = cases["high"]
    p, c = high["pairwise"], high["optimized"]
    ratios = {}
    for key in ("net_count", "sum_declared_net_cap_pf",
                "max_declared_net_cap_pf", "max_cell_input_connections_per_net",
                "sum_cell_input_connections"):
        ratios[key + "_pct_change_vs_optimized_high"] = 100 * (p[key] / c[key] - 1)
    return {"source": "immutable artifact 12523741140, workflow 39995731088",
            "units": "SPEF declared D_NET total capacitance in pF; NOT dynamic power",
            "cases": cases, "high_rc_pairwise_vs_optimized": ratios,
            "limitations": ("Independent physical implementation per RC; not a fixed-topology RC experiment. "
                            "High-capacitance/fanout nets are candidates only, not proven slew violators. "
                            "No CTS, GPU throughput or power measurement."),
            "holdouts": "SEALED"}


def self_test():
    sample = ("*SPEF \"ieee 1481-1999\"\n*C_UNIT 1 PF\n*NAME_MAP\n*1 issue_wave0[0]\n"
              "*D_NET *1 0.125\n*CONN\n*I *2:A I\n*I *3:Z O\n"
              "*CAP\n1 *2:A 0.125\n*END\n")
    rows = parse_spef(sample)
    assert rows == [{"net": "issue_wave0[0]", "declared_total_cap_pf": 0.125,
                     "cell_input_connections": 1, "cell_output_connections": 1}]
    for bad in (sample.replace("*C_UNIT 1 PF", "*C_UNIT 1 FF"),
                sample.replace("*D_NET", "*BAD_NET"), sample.replace("*CONN", "*BAD_CONN")):
        try:
            parse_spef(bad)
        except ValueError:
            continue
        raise AssertionError("Malformed SPEF was accepted")
    print("V296_SPEF_LOAD_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 3:
        raise SystemExit("Usage: spef_load_summary.py DETAIL_DIR OUTPUT_JSON")
    try:
        result = audit(Path(sys.argv[1]))
    except (ValueError, OSError, UnicodeError) as exc:
        result = {"decision": "SPEF_LOAD_AUDIT_FAIL", "error": str(exc)}
    else:
        result["decision"] = "SPEF_LOAD_SUMMARY_OK"
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["decision"] != "SPEF_LOAD_SUMMARY_OK":
        raise SystemExit(3)
