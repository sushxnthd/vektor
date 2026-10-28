#!/usr/bin/env python3
"""Independent fail-closed audit of V296 final-repair Actions artifact ZIPs.

Usage: python3 research/v296/v296_final_repair_forensics.py PAIRWISE.zip SERIAL.zip
Intermediate routing violations are NOT final DRC or signoff.
"""
import argparse
import hashlib
import io
import json
import re
import zipfile
from decimal import Decimal
from pathlib import Path

DIGESTS = {
    "pairwise": "fb607ec0d632662ef60da23ac70a914cf60c04a9f113e7a5604df54235f62ee7",
    "serial_onehot": "404ea1a9e98a5348009c67ed31044cdf7610a7a1b9927e6e9da6c83e4eeb58ea",
}
FROZEN = {"clock_ns": 3.5, "rc_multiplier": 2.0, "density": 0.45,
          "setup_guard_ns": 0.25, "hold_guard_ns": 0.0,
          "area_limit_um2": 30000, "same_tcl_both": True, "holdouts": "SEALED"}

def inspect(blob, variant):
    digest = hashlib.sha256(blob).hexdigest()
    if digest != DIGESTS[variant]:
        raise ValueError("SHA256 artifact mismatch: " + variant)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP members")
        manifest = json.loads(z.read("upstream_repair_manifest.json"))
        for key, val in FROZEN.items():
            if manifest.get(key) != val:
                raise ValueError("Frozen constraint mismatch: " + key)
        log = z.read(variant + ".high.log").decode("utf-8", "replace")
        lines = log.splitlines()
        if z.read(variant + ".upstream_repair.exit.txt").decode().strip() != "EXIT_CODE=124":
            raise ValueError("Exit not the documented timeout")
        markers = ["V296_UPSTREAM_REPAIR_BEGIN", "V296_UPSTREAM_REPAIR_END",
                   "V296_CTS45_DETAIL_BEGIN",
                   "V296_CTS45_EXTRA_REPAIR " + ("1" if variant == "serial_onehot" else "0")]
        if any(lines.count(m) != 1 for m in markers):
            raise ValueError("Missing/duplicated repair provenance marker")
        if not (lines.index(markers[0]) < lines.index(markers[1]) < lines.index(markers[2])):
            raise ValueError("Repair did not precede detailed routing")
        if variant == "serial_onehot" and lines.count("V296_CTS45_FIFTH_DONE") != 1:
            raise ValueError("Strongest serial fifth-stage control missing")
        if any(x in log for x in ("V296_CTS45_DETAIL_DONE", "V296_CTS45_EXTRACTED_DONE")):
            raise ValueError("Unexpected route completion; audit requires revision")
        if any(name.endswith(".spef") for name in names):
            raise ValueError("Unexpected SPEF in censored ZIP")
        match = re.findall(
            r"^V296_METRIC stage=cts45_postcts_global area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$",
            log, re.M)
        if len(match) != 1:
            raise ValueError("Missing/duplicated post-CTS global metric")
        area, slew, cap = match[0]
        iters = re.findall(r"^\[INFO DRT-0195\] Start (\w+) optimization iteration\.", log, re.M)
        if not iters or iters[0] != "0th":
            raise ValueError("No detailed routing started")
        intermediate = re.findall(r"^\[INFO DRT-0199\]\s+Number of violations = (\d+)\.", log, re.M)
        return {
            "artifact_sha256": digest, "exit_code": 124,
            "complete": False, "extracted_rc": False,
            "pre_detail_area_um2": str(Decimal(area)),
            "pre_detail_slew_violations": int(slew),
            "pre_detail_cap_violations": int(cap),
            "detailed_iterations_started": iters,
            "last_completed_iteration_intermediate_violations":
                int(intermediate[-1]) if intermediate else None,
            "derived_tcl_sha256": manifest["derived_tcl_sha256"],
            "original_rtl_sha256": manifest["original_rtl_sha256"],
        }

def audit(pair_blob, serial_blob):
    rows = {"pairwise": inspect(pair_blob, "pairwise"),
            "serial_onehot": inspect(serial_blob, "serial_onehot")}
    for field in ("derived_tcl_sha256", "original_rtl_sha256"):
        if rows["pairwise"][field] != rows["serial_onehot"][field]:
            raise ValueError("Unmatched source: " + field)
    a = Decimal(rows["pairwise"]["pre_detail_area_um2"])
    b = Decimal(rows["serial_onehot"]["pre_detail_area_um2"])
    return {
        "run_id": 40718719600,
        "source_commit": "a62a79744acea3eee91376536e723bbb58fbea5d",
        "decision": "CENSORED_NO_MATCHED_PHYSICAL_WIN",
        "pre_detail_area_saving_um2": str(b - a),
        "pre_detail_area_saving_percent": str((b - a) * 100 / b),
        "final_drc": "UNAVAILABLE", "final_setup_hold": "UNAVAILABLE",
        "physical_feasibility": "UNESTABLISHED",
        "matched_clock_admission_ratio": 1,
        "gpu_performance_claim": False,
        "rows": rows,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("pairwise", type=Path)
    p.add_argument("serial", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    a, b = args.pairwise.read_bytes(), args.serial.read_bytes()
    result = audit(a, b)
    if args.self_test:
        for bad in (a + b"X", a[:-1] + bytes([a[-1] ^ 1])):
            try:
                audit(bad, b)
            except ValueError:
                pass
            else:
                raise AssertionError("Mutated artifact passed")
        assert result["rows"]["pairwise"]["detailed_iterations_started"] == ["0th"]
        assert result["rows"]["serial_onehot"]["detailed_iterations_started"] == ["0th", "1st"]
        print("V296_FINAL_REPAIR_FORENSICS_SELFTEST_PASS")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
