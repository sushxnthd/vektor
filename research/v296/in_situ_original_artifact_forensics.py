#!/usr/bin/env python3
"""Fail-closed audit of V296 original in-situ path attempt (run 40173311725).

This run completed detailed routing and extracted STA, but its path report
failed because pinned OpenSTA rejects -group_path_count. Do not infer endpoints.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ZIP_SHA = "9ce2ede807ba5858efcd113b3cd4c2f9e8e5d4a6d97a7b04eb663dd354786259"
LOG_SHA = "07edee2e676af1cb8486ffe30c4c4b6fb0a04c261ab47e9920705d69c20d3cc5"
ORIGINAL = dict(area=17857.644252217142, setup=-1.047895, hold=-0.036622, slew=0, cap=3)

def one(pattern, text, flags=0):
    hits = re.findall(pattern, text, flags)
    if len(hits) != 1:
        raise ValueError("Missing or ambiguous physical evidence: " + pattern)
    return hits[0]

def audit_log(log):
    if log.count("V296_CTS45_DRC_COUNT 0") != 1 or log.count("V296_CTS45_IS_ROUTED 1") != 1:
        raise ValueError("Detailed-route or DRC completion absent")
    stage = one(r"V296_STAGE_BEGIN cts45_extracted\s+(.*?)V296_STAGE_END cts45_extracted", log, re.S)
    area, slew, cap = one(r"^V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$", stage, re.M)
    setup = float(one(r"^worst slack\s+(-?[0-9.]+)$", stage, re.M))
    repeat = float(one(r"V296_IN_SITU_SETUP_SLACK_BEGIN\s+worst slack\s+(-?[0-9.]+)\s+V296_IN_SITU_SETUP_SLACK_END", log))
    hold = float(one(r"V296_IN_SITU_HOLD_SLACK_BEGIN\s+worst slack\s+(-?[0-9.]+)\s+V296_IN_SITU_HOLD_SLACK_END", log))
    vals = dict(area=float(area), setup=setup, hold=hold, slew=int(slew), cap=int(cap))
    if any(abs(vals[k] - ORIGINAL[k]) > 1e-6 for k in ORIGINAL) or abs(setup - repeat) > 1e-9:
        raise ValueError("Original physical result not exactly reproduced")
    err = "[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag."
    if log.count(err) != 1 or log.count("V296_IN_SITU_SETUP_PATHS_BEGIN") != 1:
        raise ValueError("Tool incompatibility not proven")
    if "V296_IN_SITU_SETUP_PATHS_END" in log or "V296_IN_SITU_DONE" in log:
        raise ValueError("Contradictory path completion markers")
    return dict(decision="EXTRACTED_SLACK_REPRODUCED_PATH_REPORT_UNAVAILABLE",
                run_id=40173311725, artifact_id=12592692428,
                original_gate="BOTH_INFEASIBLE", physical_gate="FAIL",
                pairwise=dict(area_um2=vals["area"], setup_ns=setup, hold_ns=hold,
                              slew_violations=vals["slew"], cap_violations=vals["cap"],
                              drc_violations=0, detailed_route_complete=True),
                path_endpoints="NOT_OBSERVED", gpu_speedup="NOT_ESTABLISHED")

def audit_zip(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ZIP_SHA:
        raise ValueError("Original artifact SHA-256 mismatch")
    with zipfile.ZipFile(path) as z:
        log = z.read("pairwise.high.log")
    if hashlib.sha256(log).hexdigest() != LOG_SHA:
        raise ValueError("Original log SHA-256 mismatch")
    result = audit_log(log.decode(errors="replace"))
    result.update(zip_sha256=ZIP_SHA, log_sha256=LOG_SHA)
    return result

def self_test():
    log = ("V296_CTS45_DRC_COUNT 0\nV296_CTS45_IS_ROUTED 1\n"
           "V296_STAGE_BEGIN cts45_extracted\n"
           "V296_METRIC stage=cts45_extracted area_um2=17857.644252217142 slew=0 cap=3\n"
           "worst slack -1.047895\nV296_STAGE_END cts45_extracted\n"
           "V296_IN_SITU_SETUP_SLACK_BEGIN\nworst slack -1.047895\nV296_IN_SITU_SETUP_SLACK_END\n"
           "V296_IN_SITU_HOLD_SLACK_BEGIN\nworst slack -0.036622\nV296_IN_SITU_HOLD_SLACK_END\n"
           "V296_IN_SITU_SETUP_PATHS_BEGIN\n"
           "[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag.\n")
    assert audit_log(log)["physical_gate"] == "FAIL"
    for bad in (log.replace("cap=3", "cap=0"),
                log.replace("-1.047895", "-0.547895", 1),
                log.replace("DRC_COUNT 0", "DRC_COUNT 2"),
                log.replace("PATHS_BEGIN", "PATHS_END"),
                log + "V296_IN_SITU_DONE\n"):
        try:
            audit_log(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Tampered evidence accepted")
    print("V296_IN_SITU_ARTIFACT_FORENSICS_SELFTEST_PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--zip", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
    if args.zip:
        print(json.dumps(audit_zip(args.zip), indent=2))
    if not args.zip and not args.self_test:
        p.error("Provide --zip or --self-test")
