#!/usr/bin/env python3
"""Read-only, SHA-locked forensic checker for canceled V296 detailed-route run 40244774412.
Inputs are original GitHub Actions artifact ZIPs; this is NOT physical signoff.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

PINNED = {
    "pairwise": ("9f68536beace12b49ccbc33b29a1b0d5b3b1f6c6ea3d598366ee50784700bf9b", "pairwise.high.log"),
    "serial_onehot": ("b4d3b78618d81debd6ff733d9799ec95ad691937162c9ca320aebe4b51a32678", "serial_onehot.high.log"),
}
RE_STAGE = re.compile(r"V296_STAGE_BEGIN ([\w]+)\s*\nV296_METRIC stage=\1 area_um2=([\d.]+) slew=(\d+) cap=(\d+)\s*\nworst slack\s+(-?[\d.]+)", re.M)
RE_VIOL = re.compile(r"\[INFO DRT-0199\]\s+Number of violations = (\d+)\.")
RE_ITER = re.compile(r"\[INFO DRT-0195\] Start (\d+)(?:st|nd|rd|th) optimization iteration\.")

def inspect_log(blob, variant, check_hash=True):
    digest = hashlib.sha256(blob).hexdigest()
    if check_hash and digest != PINNED[variant][0]:
        raise ValueError("Pinned artifact log SHA-256 mismatch: " + variant)
    text = blob.decode("utf-8", errors="replace")
    if text.count("V296_TILE_SLICE_FLOORPLAN die260_core240") != 1:
        raise ValueError("Wrong floorplan provenance")
    if "V296_CTS45_DETAIL_BEGIN" not in text:
        raise ValueError("Detailed routing was not started")
    stages = {}
    for name, area, slew, cap, slack in RE_STAGE.findall(text):
        if name in stages:
            raise ValueError("Duplicate stage: " + name)
        stages[name] = {"area_um2": float(area), "slew": int(slew),
                        "cap": int(cap), "reported_worst_slack_ns": float(slack)}
    if "cts45_postcts_global" not in stages:
        raise ValueError("Missing post-CTS global-route checkpoint")
    violations = [int(x) for x in RE_VIOL.findall(text)]
    iterations = [int(x) for x in RE_ITER.findall(text)]
    if len(iterations) != len(violations) + 1 or iterations != list(range(len(iterations))):
        raise ValueError("Incomplete or inconsistent DRT iteration sequence")
    if not violations:
        raise ValueError("Missing detailed-route DRC evidence")
    if "V296_CTS45_DONE" in text:
        raise ValueError("Unexpected completed route: use the original physical audit instead")
    return {"variant": variant, "sha256_log": digest, "stages": stages,
            "drc_violations_after_iteration": dict(enumerate(violations)),
            "drc_first": violations[0], "drc_last_completed_iteration": violations[-1],
            "last_completed_iteration": iterations[-2], "complete": False}

def load(path, variant):
    with zipfile.ZipFile(path) as z:
        matches = [n for n in z.namelist() if n.endswith("/" + PINNED[variant][1]) or n == PINNED[variant][1]]
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous log in ZIP")
        return inspect_log(z.read(matches[0]), variant)

def report(p, s):
    a, b = p["stages"]["cts45_postcts_global"], s["stages"]["cts45_postcts_global"]
    common = min(p["last_completed_iteration"], s["last_completed_iteration"])
    comparison = {
        "common_completed_drt_iteration": common,
        "pairwise_drc_at_common_iteration": p["drc_violations_after_iteration"][common],
        "serial_drc_at_common_iteration": s["drc_violations_after_iteration"][common],
        "pairwise_global_area_um2": a["area_um2"],
        "serial_global_area_um2": b["area_um2"],
        "global_area_saving_fraction": (b["area_um2"] - a["area_um2"]) / b["area_um2"],
        "pairwise_global_reported_slack_ns": a["reported_worst_slack_ns"],
        "serial_global_reported_slack_ns": b["reported_worst_slack_ns"],
        "global_slack_lead_ns": a["reported_worst_slack_ns"] - b["reported_worst_slack_ns"],
        "setup_guard_ns": 0.05,
        "candidate_global_setup_guard_deficit_ns": 0.05 - a["reported_worst_slack_ns"],
        "serial_global_setup_guard_deficit_ns": 0.05 - b["reported_worst_slack_ns"],
        "both_global_estimates_below_guard": a["reported_worst_slack_ns"] < .05 and b["reported_worst_slack_ns"] < .05,
        "postroute_electrical_closure": "UNMEASURED",
        "physical_verdict": "INCOMPLETE_TIMEOUT_NO_PHYSICAL_CLAIM",
    }
    assert comparison["pairwise_drc_at_common_iteration"] > 0
    assert comparison["serial_drc_at_common_iteration"] > 0
    return {"source_run": 40244774412, "pairwise": p, "serial_onehot": s,
            "comparison": comparison, "holdouts": "SEALED",
            "same_clock_admission_speedup": 0.0}

def self_test():
    for variant in PINNED:
        sample = ("V296_TILE_SLICE_FLOORPLAN die260_core240\n"
                  "V296_STAGE_BEGIN cts45_postcts_global\n"
                  "V296_METRIC stage=cts45_postcts_global area_um2=100 slew=0 cap=0\n"
                  "worst slack -0.2\nV296_CTS45_DETAIL_BEGIN\n"
                  "[INFO DRT-0195] Start 0th optimization iteration.\n"
                  "[INFO DRT-0199]   Number of violations = 10.\n"
                  "[INFO DRT-0195] Start 1st optimization iteration.\n").encode()
        assert inspect_log(sample, variant, check_hash=False)["drc_first"] == 10
        for bad in [sample + b"V296_CTS45_DONE\n",
                    sample.replace(b"1st", b"2nd"),
                    sample.replace(b"die260_core240", b"die140_core120")]:
            try: inspect_log(bad, variant, check_hash=False)
            except ValueError: pass
            else: raise AssertionError("Mutation accepted")
        try: inspect_log(sample, variant, check_hash=True)
        except ValueError: pass
        else: raise AssertionError("Wrong hash accepted")
    print("V296_TIMEOUT_FORENSICS_SELFTEST_PASS")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise", type=Path)
    parser.add_argument("--serial", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test()
    if args.pairwise and args.serial:
        print(json.dumps(report(load(args.pairwise, "pairwise"),
                                load(args.serial, "serial_onehot")), indent=2, sort_keys=True))
    elif not args.self_test:
        parser.error("Supply both ZIPs or --self-test")

if __name__ == "__main__":
    main()
