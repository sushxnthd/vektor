#!/usr/bin/env python3
"""Fail-closed raw-report screening; NOT physical signoff.

Usage: python v317_report_evidence_audit_20261112.py manifest.json
Manifest keys: run_id, baseline, candidate. Each implementation must contain
run_id, report, spef, rtl_sha256, constraints_sha256, library_sha256.
Reports require exact anchored fields documented in FIELDS. No Boolean
self-declared legality flags are accepted. SPEF presence is not SPEF validation.
"""
import json
import re
import sys
from pathlib import Path

FIELDS = {
    "area_um2": r"(?im)^\s*Design area\s+([0-9]+(?:\.[0-9]+)?)\s+um\^2\s*$",
    "setup_wns_ns": r"(?im)^\s*setup wns\s+(-?[0-9]+(?:\.[0-9]+)?)\s*$",
    "hold_wns_ns": r"(?im)^\s*hold wns\s+(-?[0-9]+(?:\.[0-9]+)?)\s*$",
    "max_cap_violations": r"(?im)^\s*max_cap_violations\s+(\d+)\s*$",
    "max_slew_violations": r"(?im)^\s*max_slew_violations\s+(\d+)\s*$",
    "drc_violations": r"(?im)^\s*drc_violations\s+(\d+)\s*$",
}

def parse(report):
    values = {}
    for key, expression in FIELDS.items():
        matches = re.findall(expression, report)
        if len(matches) != 1:
            raise ValueError(f"{key}: expected one report field; found {len(matches)}")
        values[key] = float(matches[0]) if key.endswith(("um2", "_ns")) else int(matches[0])
    return values

def audit(manifest, directory):
    if set(manifest) != {"run_id", "baseline", "candidate"} or not manifest["run_id"]:
        raise ValueError("invalid manifest")
    output = {}
    for label in ("baseline", "candidate"):
        entry = manifest[label]
        required = {"run_id", "report", "spef", "rtl_sha256", "constraints_sha256", "library_sha256"}
        if set(entry) != required or entry["run_id"] != manifest["run_id"]:
            raise ValueError(f"{label}: provenance mismatch")
        for key in ("rtl_sha256", "constraints_sha256", "library_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                raise ValueError(f"{label}: invalid {key}")
        for key in ("report", "spef"):
            path = (directory / entry[key]).resolve()
            if not path.is_relative_to(directory.resolve()) or not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f"{label}: absent/empty/nonlocal {key}")
        result = parse((directory / entry["report"]).read_text())
        result["screen_legal"] = (
            result["area_um2"] > 0
            and result["setup_wns_ns"] >= 0
            and result["hold_wns_ns"] >= 0
            and all(result[key] == 0 for key in
                    ("max_cap_violations", "max_slew_violations", "drc_violations"))
        )
        output[label] = result
    if manifest["baseline"]["rtl_sha256"] == manifest["candidate"]["rtl_sha256"]:
        raise ValueError("identical RTL identity")
    for key in ("constraints_sha256", "library_sha256"):
        if manifest["baseline"][key] != manifest["candidate"][key]:
            raise ValueError(f"unmatched {key}")
    return {"evidence_tier": "raw-report-screen-only; no physical signoff",
            "both_screen_legal": all(x["screen_legal"] for x in output.values()),
            "implementations": output}

def selftest():
    report = "\n".join(("Design area 21314.6 um^2", "setup wns 0.02",
                         "hold wns 0.01", "max_cap_violations 0",
                         "max_slew_violations 0", "drc_violations 0"))
    assert parse(report)["area_um2"] == 21314.6
    for invalid in (report.replace("drc_violations 0", ""),
                    report + "\nsetup wns 0.5"):
        try:
            parse(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted missing or duplicate field")
    assert parse(report.replace("max_cap_violations 0", "max_cap_violations 21"))["max_cap_violations"] == 21

if __name__ == "__main__":
    selftest()
    if len(sys.argv) == 2:
        manifest_path = Path(sys.argv[1]).resolve()
        print(json.dumps(audit(json.loads(manifest_path.read_text()), manifest_path.parent),
                         sort_keys=True, indent=2))
    elif len(sys.argv) == 1:
        print("selftest passed; no physical evidence audited")
    else:
        raise SystemExit("usage: script.py [manifest.json]")
