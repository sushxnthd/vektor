#!/usr/bin/env python3
"""Fail-closed original-vs-reconstituted extracted timing path audit. No STA fabrication."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ORIGINAL = {
    "pairwise": {"area_um2": 17857.644252217142, "setup_ns": -1.047895,
                 "hold_ns": -0.036622, "slew": 0, "cap": 3},
    "serial_onehot": {"area_um2": 18953.830505097358, "setup_ns": -1.859922,
                      "hold_ns": -0.019796, "slew": 0, "cap": 3},
}
ROOT = Path("original")
STAGES = ("setup", "hold")


def one(pattern, data, description, flags=0):
    matches = list(re.finditer(pattern, data, flags))
    if len(matches) != 1:
        raise ValueError(f"{description}: expected one match, got {len(matches)}")
    return matches[0]


def section(data, start, end):
    a = one(r"^" + re.escape(start) + r"$", data, start, re.M)
    b = one(r"^" + re.escape(end) + r"$", data, end, re.M)
    if b.start() <= a.end():
        raise ValueError("Reversed markers " + start)
    return data[a.end():b.start()]


def slack_from(block):
    return float(one(r"^worst slack\s+(-?[0-9.]+)$", block, "worst slack", re.M).group(1))


def original_measurements(log, variant):
    if log.splitlines().count("V296_CTS45_DONE") != 1:
        raise ValueError("Original route did not finish")
    if log.splitlines().count("V296_CTS45_RC_MULTIPLIER 2.0") != 1:
        raise ValueError("Wrong original RC multiplier")
    s = section(log, "V296_STAGE_BEGIN cts45_extracted",
                "V296_STAGE_END cts45_extracted")
    m = one(r"^V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$",
            s, "original metric", re.M)
    h = section(log, "V296_CTS45_HOLD_BEGIN", "V296_CTS45_HOLD_END")
    vals = dict(area_um2=float(m.group(1)), setup_ns=slack_from(s),
                hold_ns=slack_from(h), slew=int(m.group(2)), cap=int(m.group(3)))
    reference = ORIGINAL[variant]
    for k, value in reference.items():
        if abs(vals[k] - value) > (0.0001 if k in ("setup_ns", "hold_ns") else 0.01 if k == "area_um2" else 0):
            raise ValueError("Original measurement differs from archived reference: " + k)
    return vals


def reconstructed_measurements(log, variant):
    if log.splitlines().count(f"V296_FORENSIC_DONE {variant}") != 1:
        raise ValueError("Reconstruction did not complete")
    if "STA-1648" in log or "instance " in log and " not found." in log:
        raise ValueError("Missing postroute instances in SPEF reconstruction")
    m = one(r"^V296_FORENSIC_COUNTS area_um2=([0-9.eE+\-]+) slew=(\d+) cap=(\d+)$",
            log, "reconstructed metric", re.M)
    result = dict(area_um2=float(m.group(1)), slew=int(m.group(2)), cap=int(m.group(3)))
    for stage in STAGES:
        result[stage + "_ns"] = slack_from(section(log,
            f"V296_FORENSIC_{stage.upper()}_SLACK_BEGIN",
            f"V296_FORENSIC_{stage.upper()}_SLACK_END"))
    result["setup_paths"] = section(log, "V296_FORENSIC_SETUP_PATHS_BEGIN",
                                    "V296_FORENSIC_SETUP_PATHS_END")
    result["hold_paths"] = section(log, "V296_FORENSIC_HOLD_PATHS_BEGIN",
                                   "V296_FORENSIC_HOLD_PATHS_END")
    result["cap_violators"] = section(log, "V296_FORENSIC_CAP_VIOLATORS_BEGIN",
                                      "V296_FORENSIC_CAP_VIOLATORS_END")
    return result


def evaluate(original, reconstruction):
    diff = {}
    for k in ("area_um2", "setup_ns", "hold_ns", "slew", "cap"):
        if not math.isfinite(reconstruction[k]):
            raise ValueError("Nonfinite reconstructed " + k)
        diff[k] = reconstruction[k] - original[k]
    agrees = (abs(diff["area_um2"]) <= .01 and
              abs(diff["setup_ns"]) <= .005 and
              abs(diff["hold_ns"]) <= .005 and
              diff["slew"] == 0 and diff["cap"] == 0)
    if not agrees:
        return {"verdict": "RECONSTRUCTION_MISMATCH_NO_PATH_CLAIM",
                "delta": diff, "extracted_path_attribution": None}
    setup = re.findall(r"^Startpoint:\s*(.+)$", reconstruction["setup_paths"], re.M)
    endpoints = re.findall(r"^Endpoint:\s*(.+)$", reconstruction["setup_paths"], re.M)
    hold = re.findall(r"^Startpoint:\s*(.+)$", reconstruction["hold_paths"], re.M)
    if not setup or not endpoints or not hold:
        return {"verdict": "INCOMPLETE_PATH_REPORT_NO_PATH_CLAIM",
                "delta": diff, "extracted_path_attribution": None}
    return {"verdict": "EXTRACTED_PATHS_RECONSTRUCTED_BOTH_INFEASIBLE",
            "delta": diff, "extracted_path_attribution": {
                "setup_startpoints": setup[:5], "setup_endpoints": endpoints[:5],
                "hold_startpoints": hold[:5],
                "cap_violator_excerpt": reconstruction["cap_violators"].strip()[:2400]}}


def self_test():
    a = ORIGINAL["pairwise"].copy()
    r = dict(a, setup_paths="Startpoint: A\nEndpoint: B\n",
             hold_paths="Startpoint: C\nEndpoint: D\n", cap_violators="C")
    assert evaluate(a, r)["verdict"].startswith("EXTRACTED_PATHS")
    for key, value in (("setup_ns", -.01), ("hold_ns", -.01),
                       ("area_um2", 1), ("cap", -1)):
        bad = dict(r)
        bad[key] += value
        assert evaluate(a, bad)["verdict"] == "RECONSTRUCTION_MISMATCH_NO_PATH_CLAIM"
    assert evaluate(a, dict(r, setup_paths=""))["verdict"] == "INCOMPLETE_PATH_REPORT_NO_PATH_CLAIM"
    try:
        section("A\nB\n", "B", "A")
    except ValueError:
        pass
    else:
        raise AssertionError("Reversed markers accepted")
    print("V296_EXTRACTED_PATH_AUDIT_SELFTEST_PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.root:
        rows = {}
        for variant in ORIGINAL:
            try:
                source = args.root / f"{variant}.high.log"
                sta = args.root / f"{variant}.sta.log"
                log = source.read_text(errors="replace")
                reconstructed = sta.read_text(errors="replace")
                obs = original_measurements(log, variant)
                pred = reconstructed_measurements(reconstructed, variant)
                row = evaluate(obs, pred)
                row["original"] = obs
                row["reconstructed"] = {k: pred[k] for k in obs}
                row["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (source, sta, args.root / f"{variant}.v",
                                           args.root / f"{variant}.high.cts45.def",
                                           args.root / f"{variant}.high.cts45.spef")}
                rows[variant] = row
            except (OSError, ValueError, KeyError, TypeError) as exc:
                rows[variant] = {"verdict": "INCOMPLETE", "error": str(exc)}
        ok = all(r["verdict"] == "EXTRACTED_PATHS_RECONSTRUCTED_BOTH_INFEASIBLE"
                 for r in rows.values())
        result = {"original_run": 40156470550, "evidence_tier": "read-only reconstructed post-route STA; not signoff",
                  "decision": "RECONSTRUCTION_VALIDATED" if ok else "NO_EXTRACTED_PATH_CLAIM",
                  "rows": rows, "original_physical_gate": "BOTH_INFEASIBLE",
                  "gpu_speedup": "NOT_ESTABLISHED", "holdouts": "SEALED"}
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if not ok:
            raise SystemExit(3)
    if not args.self_test and not args.root:
        ap.error("Specify --self-test or --root")


if __name__ == "__main__":
    main()
