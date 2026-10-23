#!/usr/bin/env python3
"""V296 predictive throughput/tile-area law; never reads sealed holdouts.

Inputs must be externally measured clocks, controller areas and workload traces.
This analytical projection is NOT observed GPU speedup, placed timing or power.
Example schema:
{"f_control_ghz":1.0,"f_pairwise_ghz":1.05,
 "issue_area_control_um2":3780.126,"issue_area_pairwise_um2":3098.368,
 "tile_area_control_um2":100000,
 "workloads":[{"id":"external-trace","issue_waves_per_cycle":2,
 "occupancy":0.8,"control_cycles_per_issue":0.05,
 "downstream_ceiling_waves_per_s":1200000000}]}
The example numbers are illustrative, not experimental results.
"""
import argparse
import json
import math
from pathlib import Path


def number(v, name, zero=False):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name}: expected number")
    if not math.isfinite(v) or (v < 0 if zero else v <= 0):
        raise ValueError(f"{name}: expected finite positive value")
    return float(v)


def evaluate(p):
    fc = number(p["f_control_ghz"], "f_control_ghz") * 1e9
    fp = number(p["f_pairwise_ghz"], "f_pairwise_ghz") * 1e9
    ac = number(p["issue_area_control_um2"], "issue_area_control_um2")
    ap = number(p["issue_area_pairwise_um2"], "issue_area_pairwise_um2")
    tile = number(p["tile_area_control_um2"], "tile_area_control_um2")
    if tile < ac or tile - ac + ap <= 0:
        raise ValueError("invalid tile/block area relationship")
    rows = []
    for w in p["workloads"]:
        issue = number(w["issue_waves_per_cycle"], "issue_waves_per_cycle")
        occupancy = number(w["occupancy"], "occupancy")
        if occupancy > 1:
            raise ValueError("occupancy must not exceed 1")
        overhead = number(w["control_cycles_per_issue"], "control_cycles_per_issue", True)
        ceiling = number(w["downstream_ceiling_waves_per_s"], "downstream_ceiling_waves_per_s")
        effective_ipc = issue * occupancy / (1 + overhead)
        c = fc * effective_ipc
        n = fp * effective_ipc
        tc, tn = min(c, ceiling), min(n, ceiling)
        if fp >= fc:
            regime = ("no_win_downstream_limited" if ceiling <= c else
                      "clock_ratio_limited" if ceiling >= n else
                      "partial_bandwidth_limited")
        else:
            regime = ("no_win_downstream_limited" if ceiling <= n else
                      "clock_regression" if ceiling >= c else
                      "partial_regression")
        rows.append({"id": str(w["id"]), "regime": regime,
                     "baseline_waves_per_s": tc, "pairwise_waves_per_s": tn,
                     "gain": tn / tc, "ceiling_to_baseline_issue_ratio": ceiling / c})
    return {
        "evidence_class": "analytical_projection_requires_measured_fmax_and_external_workloads",
        "not_evidence_of": ["measured_workload_speedup", "post_route_timing", "power", "novelty"],
        "assumptions": "identical decisions, ports, buffering, occupancy, control overhead and downstream ceiling; only frequency and mapped area differ",
        "frequency_ratio": fp / fc,
        "issue_block_area_ratio": ap / ac,
        "tile_area_reduction_fraction": (ac - ap) / tile,
        "tile_area_after_um2": tile - ac + ap,
        "workloads": rows,
    }


def selftest():
    p = {"f_control_ghz": 1, "f_pairwise_ghz": 1.2,
         "issue_area_control_um2": 100, "issue_area_pairwise_um2": 80,
         "tile_area_control_um2": 1000,
         "workloads": [
             {"id": "synthetic_bandwidth", "issue_waves_per_cycle": 2,
              "occupancy": 1, "control_cycles_per_issue": 0,
              "downstream_ceiling_waves_per_s": 1e9},
             {"id": "synthetic_issue", "issue_waves_per_cycle": 2,
              "occupancy": 1, "control_cycles_per_issue": 0,
              "downstream_ceiling_waves_per_s": 3e9},
             {"id": "synthetic_partial", "issue_waves_per_cycle": 2,
              "occupancy": 1, "control_cycles_per_issue": 0,
              "downstream_ceiling_waves_per_s": 2.2e9},
         ]}
    r = evaluate(p)
    assert [round(x["gain"], 8) for x in r["workloads"]] == [1.0, 1.2, 1.1]
    assert abs(r["tile_area_reduction_fraction"] - 0.02) < 1e-12
    p["f_pairwise_ghz"] = 0.8
    assert evaluate(p)["workloads"][1]["gain"] == 0.8
    print("V296_BOUNDARY_SELFTEST_PASS: four synthetic checks; holdouts sealed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="JSON of measured clocks and independent workloads")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
    else:
        if not args.input:
            parser.error("input required unless --self-test")
        print(json.dumps(evaluate(json.loads(Path(args.input).read_text())), indent=2))
