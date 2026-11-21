#!/usr/bin/env python3
"""Fail-closed matched-route physical evidence gate for V296/V317.

Only accepts independent, extracted detailed-route reports for BOTH designs.
This is an evidence checker, not a routing result or signoff certification.
Input JSON schema (one object with compact and pairwise):
{
 "technology":"...", "openroad_version":"...", "sdc_sha256":"...",
 "lef_sha256":"...", "lib_sha256":"...", "rc_corner":"...",
 "routing_layers":"...", "die_box_um":"...", "utilization_target":"...",
 "designs":{
  "compact":{"extraction":"detailed_route","drc_count":0,
   "max_cap_violations":0,"max_slew_violations":0,"max_fanout_violations":0,
   "setup_wns_ns":0.01,"hold_wns_ns":0.01,"area_um2":21314.6,
   "clock_period_ns":1.0,"workload_cycles":{"win":100,"no_win":100}},
  "pairwise":{...}
 }
}
Never substitute placement/global-route estimates for extracted route.
"""
import json
import math
import re
import sys
from fractions import Fraction

MATCHED = ("technology", "openroad_version", "sdc_sha256", "lef_sha256",
           "lib_sha256", "rc_corner", "routing_layers", "die_box_um",
           "utilization_target")
COUNTS = ("drc_count", "max_cap_violations", "max_slew_violations",
          "max_fanout_violations")
POSITIVE = ("area_um2", "clock_period_ns")
SLACKS = ("setup_wns_ns", "hold_wns_ns")

def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)

def validate(report):
    for field in MATCHED:
        if field not in report or report[field] in ("", None):
            raise ValueError("missing matched provenance: " + field)
    for field in ("sdc_sha256", "lef_sha256", "lib_sha256"):
        if not isinstance(report[field], str) or not re.fullmatch(r"[0-9a-f]{64}", report[field]):
            raise ValueError("invalid provenance SHA256: " + field)
    designs = report.get("designs", {})
    if set(designs) != {"compact", "pairwise"}:
        raise ValueError("both matched designs required")
    for label, d in designs.items():
        if d.get("extraction") != "detailed_route":
            raise ValueError(label + ": extracted detailed route required")
        for key in COUNTS:
            v = d.get(key)
            if type(v) is not int or v < 0:
                raise ValueError(label + ": invalid violation count " + key)
            if v:
                raise ValueError(label + ": electrical/DRC violation " + key)
        for key in POSITIVE + SLACKS:
            v = d.get(key)
            if not finite_number(v) or (key in POSITIVE and v <= 0):
                raise ValueError(label + ": invalid physical metric " + key)
            if key in SLACKS and v < 0:
                raise ValueError(label + ": negative slack " + key)
        cycles = d.get("workload_cycles", {})
        if set(cycles) != {"win", "no_win"}:
            raise ValueError(label + ": frozen win/no_win workloads required")
        if any(type(v) is not int or v <= 0 for v in cycles.values()):
            raise ValueError(label + ": invalid cycle count")
    a, b = designs["compact"], designs["pairwise"]
    results = {}
    for regime in ("win", "no_win"):
        ratio = (Fraction(a["workload_cycles"][regime], b["workload_cycles"][regime])
                 * Fraction(str(a["clock_period_ns"]), str(b["clock_period_ns"]))
                 * Fraction(str(a["area_um2"]), str(b["area_um2"])))
        results[regime] = {"throughput_per_area_ratio": float(ratio),
                           "pairwise_wins": ratio > 1}
    return results

def self_test():
    base = dict(technology="test", openroad_version="test", sdc_sha256="a"*64,
                lef_sha256="b"*64, lib_sha256="c"*64, rc_corner="test",
                routing_layers="test", die_box_um="test",
                utilization_target="test")
    def design(cycles):
        return dict(extraction="detailed_route", drc_count=0,
                    max_cap_violations=0, max_slew_violations=0,
                    max_fanout_violations=0, setup_wns_ns=0,
                    hold_wns_ns=0, area_um2=100, clock_period_ns=1,
                    workload_cycles={"win":cycles, "no_win":100})
    base["designs"] = {"compact":design(100), "pairwise":design(50)}
    assert validate(base)["win"]["pairwise_wins"]
    assert not validate(base)["no_win"]["pairwise_wins"]
    for key, val in [("extraction","placement"), ("drc_count",1),
                     ("max_cap_violations",1), ("max_slew_violations",1),
                     ("max_fanout_violations",1), ("setup_wns_ns",-0.1),
                     ("hold_wns_ns",-0.1), ("area_um2",0),
                     ("clock_period_ns",float("nan"))]:
        old = base["designs"]["pairwise"][key]
        base["designs"]["pairwise"][key] = val
        try:
            validate(base)
            raise AssertionError("accepted invalid " + key)
        except ValueError:
            pass
        finally:
            base["designs"]["pairwise"][key] = old
    old_digest = base["sdc_sha256"]
    base["sdc_sha256"] = "test"
    try:
        validate(base)
        raise AssertionError("accepted placeholder provenance digest")
    except ValueError:
        pass
    finally:
        base["sdc_sha256"] = old_digest
    print("PASS: valid matched fixture, nine negative physical gates, placeholder digest rejection")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            print(json.dumps(validate(json.load(f)), indent=2, sort_keys=True))
    else:
        sys.exit("Usage: physical_gate.py --self-test | matched_extracted_report.json")
