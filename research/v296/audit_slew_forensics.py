#!/usr/bin/env python3
"""Independent, fail-closed audit of immutable V296 extracted-SPEF slew replay."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys

EXPECTED = {"area_um2": 5985.266061, "setup_ns": 0.361922,
            "hold_ns": 0.283003, "slew": 33, "cap": 0}
TOLERANCE = {"area_um2": 0.01, "setup_ns": 0.005, "hold_ns": 0.005}
INPUTS = ("pairwise.v", "pairwise.high.detail.def", "pairwise.high.detail.spef")


def block(log, label):
    m = re.search(r"(?ms)^V296_FORENSIC_" + label +
                  r"_BEGIN\r?\n(.*?)^V296_FORENSIC_" + label + r"_END\r?$", log)
    if not m:
        raise ValueError("Missing complete " + label + " block")
    return m.group(1)


def parse(log):
    if log.count("V296_FORENSIC_REPLAY_DONE") != 1:
        raise ValueError("Replay did not finish exactly once")
    m = re.search(r"(?m)^V296_FORENSIC_METRIC area_um2=([\d.eE+\-]+) slew=(\d+) cap=(\d+)\r?$", log)
    if not m:
        raise ValueError("Missing metric record")
    result = {"area_um2": float(m.group(1)), "slew": int(m.group(2)),
              "cap": int(m.group(3))}
    for label, field in (("SETUP", "setup_ns"), ("HOLD", "hold_ns")):
        s = block(log, label)
        v = re.search(r"(?mi)^worst slack(?:\s+(?:max|min))?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$", s)
        if not v:
            raise ValueError("Missing finite " + label + " slack")
        result[field] = float(v.group(1))
    for field in ("area_um2", "setup_ns", "hold_ns"):
        if not math.isfinite(result[field]):
            raise ValueError("Nonfinite " + field)
    slew_report = block(log, "SLEW_VIOLATORS")
    cap_report = block(log, "CAP_VIOLATORS")
    if not slew_report.strip() or "no violat" in slew_report.lower():
        raise ValueError("Missing nonempty slew-violator evidence")
    result["slew_report_sha256"] = hashlib.sha256(slew_report.encode()).hexdigest()
    result["slew_report_nonblank_lines"] = sum(bool(x.strip()) for x in slew_report.splitlines())
    result["cap_report_sha256"] = hashlib.sha256(cap_report.encode()).hexdigest()
    return result, slew_report


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit(root, logpath):
    log = logpath.read_text()
    values, report = parse(log)
    checks = {}
    for key, expected in EXPECTED.items():
        tol = TOLERANCE.get(key, 0)
        checks[key] = abs(values[key] - expected) <= tol
    manifest = {}
    for name in INPUTS:
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError("Missing/empty immutable input " + name)
        manifest[name] = sha256(path)
    # Output is evidence only; never edit the original input files.
    logpath.with_suffix(".slew.txt").write_text(report)
    return {"decision": "SLEW_FORENSICS_REPLAY_PASS" if all(checks.values()) else
            "SLEW_FORENSICS_REPRODUCIBILITY_FAIL", "checks": checks,
            "measured": values, "immutable_inputs_sha256": manifest,
            "holdouts": "SEALED", "limitations": "Diagnostic replay only. No repair, signoff, or distinct-net attribution."}


def self_test():
    log = ("V296_FORENSIC_METRIC area_um2=5985.266061 slew=33 cap=0\n"
           "V296_FORENSIC_SETUP_BEGIN\nworst slack max 0.361922\nV296_FORENSIC_SETUP_END\n"
           "V296_FORENSIC_HOLD_BEGIN\nworst slack min 0.283003\nV296_FORENSIC_HOLD_END\n"
           "V296_FORENSIC_SLEW_VIOLATORS_BEGIN\nU12/A 0.3 > 0.25\n"
           "V296_FORENSIC_SLEW_VIOLATORS_END\n"
           "V296_FORENSIC_CAP_VIOLATORS_BEGIN\nno violators\n"
           "V296_FORENSIC_CAP_VIOLATORS_END\nV296_FORENSIC_REPLAY_DONE\n")
    assert parse(log)[0]["slew"] == 33
    for bad in (log.replace("slew=33", "slew=nan"),
                log.replace("V296_FORENSIC_SLEW_VIOLATORS_END", ""),
                log.replace("U12/A 0.3 > 0.25", "No violations"),
                log.replace("V296_FORENSIC_REPLAY_DONE", "")):
        try:
            parse(bad)
        except ValueError:
            continue
        raise AssertionError("Malformed replay was accepted")
    print("V296_SLEW_FORENSICS_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 3:
        raise SystemExit("Usage: audit_slew_forensics.py ARTIFACT_DETAIL_DIR REPLAY_LOG")
    root, logpath = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        outcome = audit(root, logpath)
    except (ValueError, OSError) as exc:
        outcome = {"decision": "SLEW_FORENSICS_INCOMPLETE", "error": str(exc), "holdouts": "SEALED"}
    logpath.with_suffix(".audit.json").write_text(json.dumps(outcome, indent=2) + "\n")
    print(json.dumps(outcome, indent=2))
    if outcome["decision"] != "SLEW_FORENSICS_REPLAY_PASS":
        raise SystemExit(3)
