#!/usr/bin/env python3
"""Independent, fail-closed four-artifact matched hold25 physical delta audit.

Python standard library only. Pass original GitHub Actions ZIPs in this order:
--audit BASE_PAIR BASE_SERIAL HOLD25_PAIR HOLD25_SERIAL
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ARTIFACTS = {
    "base_pairwise": "7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b",
    "base_serial": "56781fca03ab151661e2c3c393639caa5e71862358fbbe50e0be1dfc278d6050",
    "hold25_pairwise": "6265bc15d8be03d62ec8b8f4c3f435b0e30c355f42ed75c5e7316fed40efc625",
    "hold25_serial": "1847b10524877f02791b335a0aed4afc99ba1c21a8143d070122489b8017e9c8",
}
RTL_SHA = "1d798344ede7aee67d84f6dab5fd266dbd65c3c164f65694206c3d6b921eb8f2"
BASE_TCL_SHA = "30b0a072ec197a47c5e2264567fee50f908b85a8d946e607765083221c0fcf3d"
HOLD_TCL_SHA = "c842fd60c57d9e543f70181749b6fbae1cb6bb5fdc1e82dfd9b218fc5c6bfbe3"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def single(pattern, text, label):
    matches = re.findall(pattern, text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"{label}: expected one occurrence, got {len(matches)}")
    return matches[0]

def read_case(path, key):
    path = Path(path)
    if sha(path.read_bytes()) != ARTIFACTS[key]:
        raise ValueError(f"{key}: original GitHub ZIP digest mismatch")
    variant = "pairwise" if "pairwise" in key else "serial_onehot"
    hold25 = key.startswith("hold25")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or any(n.startswith("/") or ".." in Path(n).parts for n in names):
            raise ValueError(f"{key}: unsafe or duplicate archive members")
        for n in [variant + ".tile.audit.json", variant + ".high.log", variant + ".v",
                  variant + ".inputs.sha256", "cts45_tile.tcl"]:
            if n not in names:
                raise ValueError(f"{key}: missing {n}")
        audit = json.loads(z.read(variant + ".tile.audit.json"))
        log = z.read(variant + ".high.log").decode("utf-8", "replace")
        inputs = z.read(variant + ".inputs.sha256").decode()
        if audit["variant"] != variant or not audit["complete"]:
            raise ValueError(f"{key}: incomplete or wrong-variant physical audit")
        if RTL_SHA + "  research/v296/v296_tile_slice_fixed_word.sv" not in inputs:
            raise ValueError(f"{key}: RTL provenance mismatch")
        if sha(z.read("cts45_tile.tcl")) != BASE_TCL_SHA:
            raise ValueError(f"{key}: base Tcl mismatch")
        if single(r"^V296_CTS45_RC_MULTIPLIER ([0-9.]+)$", log, "RC") != "2.0":
            raise ValueError(f"{key}: changed RC multiplier")
        if single(r"^V296_CTS45_DRC_COUNT (\d+)$", log, "DRC") != "0":
            raise ValueError(f"{key}: DRC violations")
        if single(r"^V296_CTS45_IS_ROUTED (\d+)$", log, "route") != "1":
            raise ValueError(f"{key}: not routed")
        expected_extra = "0" if variant == "pairwise" else "1"
        if single(r"^V296_CTS45_EXTRA_REPAIR (\d+)$", log, "serial repair") != expected_extra:
            raise ValueError(f"{key}: mismatched serial control")
        if log.splitlines().count("V296_HOLD25_MARGIN_NS 0.025") != int(hold25):
            raise ValueError(f"{key}: hold25 intervention marker mismatch")
        if hold25:
            if "cts45_hold25_tile.tcl" not in names or sha(z.read("cts45_hold25_tile.tcl")) != HOLD_TCL_SHA:
                raise ValueError(f"{key}: modified hold25 Tcl")
            manifest = json.loads(z.read("fixed_word_hold25_manifest.json"))
            if (manifest["clock_ns"], manifest["rc_multiplier"], manifest["hold_slack_margin_ns"]) != (3.5, 2.0, 0.025):
                raise ValueError(f"{key}: hold25 manifest drift")
        f = audit["final"]
        hold = float(single(r"V296_CTS45_HOLD_BEGIN\nworst slack ([-0-9.]+)\nV296_CTS45_HOLD_END", log, "hold"))
        setup = float(single(r"V296_STAGE_BEGIN cts45_extracted\nV296_METRIC stage=cts45_extracted area_um2=[0-9.]+ slew=\d+ cap=\d+\nworst slack ([-0-9.]+)", log, "setup"))
        metric = single(r"^V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$", log, "metrics")
        area, slew, cap = float(metric[0]), int(metric[1]), int(metric[2])
        if (abs(f["hold_ns"] - hold) > 1e-9 or abs(f["setup_ns"] - setup) > 1e-9 or
            abs(f["area_um2"] - area) > 1e-7 or f["slew"] != slew or f["cap"] != cap):
            raise ValueError(f"{key}: physical audit disagrees with original tool log")
        wires = int(re.findall(r"^Total wire length = (\d+) um\.$", log, re.MULTILINE)[-1])
        vias = int(re.findall(r"^Total number of vias = (\d+)\.$", log, re.MULTILINE)[-1])
        return {"variant": variant, "hold25": hold25,
                "setup_ps": round(setup * 1000, 3), "hold_ps": round(hold * 1000, 3),
                "area_um2": area, "cap_violations": cap, "slew_violations": slew,
                "drc_violations": 0, "wire_um": wires, "vias": vias,
                "netlist_sha256": sha(z.read(variant + ".v")), "rtl_sha256": RTL_SHA}

def verdict(rows):
    for name in ARTIFACTS:
        if name not in rows:
            raise ValueError("missing paired case: " + name)
    if rows["base_pairwise"]["netlist_sha256"] != rows["hold25_pairwise"]["netlist_sha256"]:
        raise ValueError("candidate synthesized netlist changed")
    if rows["base_serial"]["netlist_sha256"] != rows["hold25_serial"]["netlist_sha256"]:
        raise ValueError("serial synthesized netlist changed")
    deltas = {}
    for v in ("pairwise", "serial"):
        b, h = rows["base_" + v], rows["hold25_" + v]
        deltas[v] = {
            "setup_improvement_ps": round(h["setup_ps"] - b["setup_ps"], 3),
            "hold_improvement_ps": round(h["hold_ps"] - b["hold_ps"], 3),
            "area_increase_um2": round(h["area_um2"] - b["area_um2"], 6),
            "wire_increase_um": h["wire_um"] - b["wire_um"],
            "via_increase": h["vias"] - b["vias"],
            "cap_violation_delta": h["cap_violations"] - b["cap_violations"],
        }
    def feasible(r):
        return (r["setup_ps"] >= 50 and r["hold_ps"] >= 0 and
                r["cap_violations"] == r["slew_violations"] == r["drc_violations"] == 0 and
                r["area_um2"] <= 30000)
    result = {
        "artifact_sha256": ARTIFACTS, "rows": rows, "deltas": deltas,
        "candidate_feasible_after_hold25": feasible(rows["hold25_pairwise"]),
        "serial_feasible_after_hold25": feasible(rows["hold25_serial"]),
        "matched_feasible_pareto": feasible(rows["hold25_pairwise"]) and feasible(rows["hold25_serial"]),
        "same_clock_admission_gain": 0.0,
        "nonnegative_setup_cost_law_falsified_by_observation":
            deltas["pairwise"]["setup_improvement_ps"] > 0 and deltas["pairwise"]["hold_improvement_ps"] > 0,
        "causal_identification_of_path_delay_transfer": False,
        "production_gpu_claim": False, "holdouts": "SEALED",
    }
    return result

def self_test():
    assert single(r"^x=(\d+)$", "x=7\n", "test") == "7"
    for s in ("", "x=1\nx=2\n"):
        try:
            single(r"^x=(\d+)$", s, "test")
        except ValueError:
            pass
        else:
            raise AssertionError("bad cardinality accepted")
    print("HOLD25_MATCHED_DELTA_SELFTEST_PASS")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--audit", nargs=4, metavar=("BASE_PAIR", "BASE_SERIAL", "HOLD_PAIR", "HOLD_SERIAL"))
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.audit:
        rows = {key: read_case(path, key) for key, path in zip(ARTIFACTS, a.audit)}
        print(json.dumps(verdict(rows), indent=2, sort_keys=True))
    if not (a.self_test or a.audit):
        p.error("choose --self-test or --audit")

if __name__ == "__main__":
    main()
