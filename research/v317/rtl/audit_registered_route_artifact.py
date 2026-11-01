"""Independent audit of V317 registered OpenROAD routed-evidence ZIP.

Consumes GitHub Actions artifact bytes, not a researcher-edited summary.
Fail closed on missing metrics. Route success is NOT complete electrical signoff.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import zipfile

LABELS = ("source_35", "pairwise_35", "source_65", "pairwise_65")


def member(z, label, suffix):
    names = [n for n in z.namelist() if n.startswith(label + "/") and n.endswith(suffix)]
    if len(names) != 1:
        raise ValueError(f"{label}: expected exactly one {suffix}, found {len(names)}")
    return z.read(names[0]).decode("utf-8")


def number(text, pattern, label):
    matches = re.findall(pattern, text, re.M)
    if len(matches) != 1:
        raise ValueError(f"{label}: expected exactly one metric {pattern}, found {len(matches)}")
    value = float(matches[0])
    if not math.isfinite(value):
        raise ValueError(f"{label}: nonfinite metric")
    return value


def section(text, title):
    m = re.search(r"finish " + re.escape(title) + r"\s*\n-+\n(.*?)(?=\n={15,}|\Z)", text, re.S)
    if not m:
        raise ValueError(f"missing {title}")
    return m.group(1)


def audit(z, label):
    status = member(z, label, "status.txt")
    match = re.search(r"^exit_code=(\d+)$", status, re.M)
    if not match:
        raise ValueError(f"{label}: missing exit status")
    exit_code = int(match.group(1))
    if exit_code:
        log = member(z, label, "make.log")
        return {
            "label": label,
            "route_completed": False,
            "exit_code": exit_code,
            "floorplan_density_error": "FLW-0024" in log,
            "physical_signoff": False,
        }
    finish = member(z, label, "6_finish.rpt")
    final_log = member(z, label, "6_report.log")
    route_log = member(z, label, "5_2_route.log")
    area = number(final_log, r"Design area ([0-9]+(?:\.[0-9]+)?) um\^2 \d+% utilization", label)
    util = number(final_log, r"Design area [0-9]+(?:\.[0-9]+)? um\^2 (\d+)% utilization", label)
    min_period = number(section(finish, "report_clock_min_period"),
                        r"core_clk period_min = ([0-9]+(?:\.[0-9]+)?)", label)
    setup = number(section(finish, "report_checks -path_delay max"),
                   r"(-?\d+\.\d+)\s+slack \(MET\)", label)
    hold = number(section(finish, "report_checks -path_delay min"),
                  r"(-?\d+\.\d+)\s+slack \(MET\)", label)
    drcs = re.findall(r"Number of violations = (\d+)\.", route_log)
    lengths = re.findall(r"Total wire length = (\d+) um", route_log)
    if not drcs or not lengths:
        raise ValueError(f"{label}: missing detailed-route DRC or wirelength")
    p = section(finish, "report_power")
    powers = re.findall(r"^Total\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", p, re.M)
    if len(powers) != 1:
        raise ValueError(f"{label}: missing activity-assumption power proxy")
    return {
        "label": label,
        "route_completed": True,
        "exit_code": 0,
        "cell_area_um2": area,
        "reported_utilization_pct": util,
        "min_clock_period_ns": min_period,
        "setup_slack_ns": setup,
        "hold_slack_ns": hold,
        "last_detailed_route_drc_count": int(drcs[-1]),
        "routed_wire_length_um": int(lengths[-1]),
        "default_activity_power_proxy_w": float(powers[0][3]),
        "timing_and_drc_pass": setup >= 0 and hold >= 0 and int(drcs[-1]) == 0,
        "physical_signoff": False,
    }


def evaluate(path):
    with zipfile.ZipFile(path) as z:
        rows = {label: audit(z, label) for label in LABELS}
        sim = [n for n in z.namelist() if n == "rtl_simulation.log"]
        if len(sim) != 1 or "PASS: 4998" not in z.read(sim[0]).decode("utf-8"):
            raise ValueError("registered RTL comparison not independently confirmed")
    a, b = rows["source_35"], rows["pairwise_35"]
    if not a["route_completed"] or not b["route_completed"]:
        raise ValueError("missing matched 35% routed pair")
    area_reduction = 1 - b["cell_area_um2"] / a["cell_area_um2"]
    wire_reduction = 1 - b["routed_wire_length_um"] / a["routed_wire_length_um"]
    return {
        "evidence_tier": "NANGATE45_OPENROAD_REGISTERED_CONTROL_BLOCK_ROUTE",
        "rows": rows,
        "frozen_35_pairwise_area_win": area_reduction > 0,
        "area_reduction_fraction_35": area_reduction,
        "wire_length_reduction_fraction_35": wire_reduction,
        "critical_period_ratio_source_over_pairwise_35":
            a["min_clock_period_ns"] / b["min_clock_period_ns"],
        "matched_35_setup_hold_and_drc_pass":
            a["timing_and_drc_pass"] and b["timing_and_drc_pass"],
        "equal_clock_equal_port_intrinsic_service_ratio": 1.0,
        "full_electrical_signoff": False,
        "integrated_gpu_throughput_measured": False,
        "unverified": [
            "postroute maximum-capacitance and maximum-transition report",
            "independent routed parasitic audit and input-driver equivalence",
            "tile-level register-file SRAM, bandwidth, clock and workload model",
            "silicon power and process-corner variation",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("artifact_zip")
    args = p.parse_args()
    result = evaluate(args.artifact_zip)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["frozen_35_pairwise_area_win"] or not result["matched_35_setup_hold_and_drc_pass"]:
        raise SystemExit("frozen 35% routed gate FAILED")


if __name__ == "__main__":
    main()
