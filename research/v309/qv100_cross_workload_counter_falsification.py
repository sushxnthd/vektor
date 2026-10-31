#!/usr/bin/env python3
"""Compare two independently audited QV100-SASS workloads without claiming DRAM traffic.

The reported L1D and L2 miss counters are distinct simulator statistics.
Their ratio is NOT an L2 miss rate or measured off-chip traffic.
"""
import argparse
import json
from pathlib import Path

COUNTERS = ("L1D_total_cache_misses", "L2_total_cache_misses",
            "gpu_tot_sim_cycle", "gpu_tot_sim_insn")


def validate(d):
    if (d.get("status") != "PASS_INDEPENDENT_SIMULATOR_COUNTER_REPLAY"
            or d.get("evidence_tier") != "pinned_accel_sim_QV100_SASS_only_not_hardware"
            or d.get("hardware_validated") is not False
            or d.get("architecture_speedup_permitted") is not False
            or d.get("semantic_kernel_counters_identical") is not True):
        raise ValueError("not an independently accepted simulator-only audit")
    rows = d.get("kernel_records")
    if not isinstance(rows, list) or len(rows) != d.get("expected_launches") or not rows:
        raise ValueError("missing or inconsistent kernel records")
    totals = d.get("cumulative_counter_totals")
    if not isinstance(totals, dict):
        raise ValueError("missing cumulative counters")
    for k in COUNTERS:
        if type(totals.get(k)) is not int or totals[k] < 0:
            raise ValueError("invalid cumulative counter: " + k)
        if rows[-1].get(k) != totals[k]:
            raise ValueError("final kernel disagrees with cumulative counter: " + k)
        if sum(r.get("increments", {}).get(k, -1) for r in rows) != totals[k]:
            raise ValueError("per-kernel conservation failed: " + k)
    if totals["gpu_tot_sim_cycle"] <= 0 or totals["gpu_tot_sim_insn"] <= 0:
        raise ValueError("nonpositive simulated work")
    if not isinstance(d.get("selected_list"), str) or not d["selected_list"].endswith("/kernelslist.g"):
        raise ValueError("invalid workload identity")
    return totals


def compare(a, b):
    x, y = validate(a), validate(b)
    if a["selected_list"] == b["selected_list"]:
        raise ValueError("workloads are not independent selections")
    def entry(d, c):
        return {
            "selected_list": d["selected_list"],
            "simulated_cycles": c["gpu_tot_sim_cycle"],
            "simulated_instructions": c["gpu_tot_sim_insn"],
            "reported_L1D_misses": c["L1D_total_cache_misses"],
            "reported_L2_misses": c["L2_total_cache_misses"],
            "L2_to_L1D_counter_ratio_not_miss_rate": (
                c["L2_total_cache_misses"] / c["L1D_total_cache_misses"]
                if c["L1D_total_cache_misses"] else None),
        }
    return {
        "status": "PASS_SIMULATOR_COUNTER_CROSS_WORKLOAD_COMPARISON",
        "workloads": [entry(a, x), entry(b, y)],
        "L1D_miss_count_alone_cannot_identify_L2_miss_count": (
            x["L1D_total_cache_misses"] > 0 and y["L1D_total_cache_misses"] > 0
            and ((x["L2_total_cache_misses"] == 0) != (y["L2_total_cache_misses"] == 0))),
        "DRAM_traffic_identified": False,
        "hardware_validated": False,
        "architecture_speedup_permitted": False,
    }


def fixture(name, l1, l2):
    c = dict(zip(COUNTERS, (l1, l2, 100, 200)))
    return {"status": "PASS_INDEPENDENT_SIMULATOR_COUNTER_REPLAY",
            "evidence_tier": "pinned_accel_sim_QV100_SASS_only_not_hardware",
            "hardware_validated": False, "architecture_speedup_permitted": False,
            "semantic_kernel_counters_identical": True, "selected_list": name + "/kernelslist.g",
            "expected_launches": 1, "cumulative_counter_totals": c,
            "kernel_records": [dict(c, increments=dict(c))]}


def selftest():
    a, b = fixture("pathfinder", 3534, 129), fixture("lud", 2048, 0)
    assert compare(a, b)["L1D_miss_count_alone_cannot_identify_L2_miss_count"]
    cases = [
        (dict(a, hardware_validated=True), b),
        (dict(a, architecture_speedup_permitted=True), b),
        (dict(a, semantic_kernel_counters_identical=False), b),
        (dict(a, selected_list=b["selected_list"]), b),
        (dict(a, cumulative_counter_totals=dict(a["cumulative_counter_totals"], L2_total_cache_misses=130)), b),
        (dict(a, expected_launches=2), b),
        (dict(a, status="PASS_RUNTIME"), b),
        (dict(a, kernel_records=[]), b),
    ]
    for x, y in cases:
        try:
            compare(x, y)
        except ValueError:
            continue
        raise AssertionError("adversarial control accepted")
    return {"status": "PASS", "positive_controls": 1, "negative_controls": len(cases)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--first")
    p.add_argument("--second")
    p.add_argument("--out")
    args = p.parse_args()
    if args.selftest:
        result = selftest()
    else:
        if not (args.first and args.second and args.out):
            p.error("provide --first, --second and --out")
        result = compare(json.loads(Path(args.first).read_text()),
                         json.loads(Path(args.second).read_text()))
        Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
