#!/usr/bin/env python3
"""Independent fail-closed V296 bank-decoder mapped-artifact audit.

python3 research/v296/bank_decode_mapped_independent_audit.py ARTIFACT.zip --self-test

Only four-way mapped Nangate45 evidence. No physical timing or GPU claim.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ARTIFACT_SHA256 = "0cafd08a8a4cbd2164336c9f2ad11e6037c3fac02aa42243ebd1a7641d704ba2"
LOGS = ("baseline_pairwise", "baseline_serial", "decode_pairwise", "decode_serial")
EXPECTED_FILES = {name + ".log" for name in LOGS} | {
    "library.sha256", "nangate.lib", "source.sha256", "yosys.version"
}


def last(pattern, content, label):
    matches = re.findall(pattern, content, re.MULTILINE)
    if not matches:
        raise ValueError("missing " + label)
    return matches[-1]


def audit(path, expected_digest=ARTIFACT_SHA256):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != expected_digest:
        raise ValueError("artifact SHA256 mismatch")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if set(names) != EXPECTED_FILES or len(names) != len(EXPECTED_FILES):
            raise ValueError("unexpected or duplicated archive members")
        if hashlib.sha256(z.read("nangate.lib")).hexdigest() not in z.read("library.sha256").decode():
            raise ValueError("library digest mismatch")
        sources = z.read("source.sha256").decode()
        for source in ("v296_tile_slice_return_tree.sv", "v296_tile_slice_operand_capture.sv",
                       "v296_tile_slice_bank_decode.sv", "v296_issue_core.sv", "v295_issue_core.sv"):
            if source not in sources:
                raise ValueError("missing source anchor " + source)
        results = {}
        for name in LOGS:
            data = z.read(name + ".log").decode("utf-8")
            top = "v296_tile_slice_bank_decode" if name.startswith("decode_") else "v296_tile_slice_operand_capture"
            areas = re.findall(r"Chip area for module '.*?" + re.escape(top) +
                               r"':\s*([0-9]+(?:\.[0-9]+)?)", data)
            if len(areas) != 1:
                raise ValueError(name + ": ambiguous or missing mapped area")
            depth = int(last(r"Longest topological path in " + re.escape(top) +
                             r" \(length=(\d+)\):", data, name + " depth"))
            cells = int(last(r"Number of cells:\s+(\d+)", data, name + " cells"))
            dff = int(last(r"^\s+DFF_X1\s+(\d+)\s*$", data, name + " DFF_X1"))
            dffr = int(last(r"^\s+DFFR_X1\s+(\d+)\s*$", data, name + " DFFR_X1"))
            if dff != 256 or dffr != 132 or cells < 1000 or depth < 20:
                raise ValueError(name + ": unexpected state or netlist size")
            results[name] = {"area_um2": float(areas[0]), "logic_depth": depth,
                             "cells": cells, "dff": dff + dffr}
    bp, bs, dp, ds = (results[k]["area_um2"] for k in LOGS)
    candidate_growth = dp / bp - 1
    serial_growth = ds / bs - 1
    return {
        "evidence_tier": "FOURWAY_NANGATE45_MAPPED_ONLY_NO_PHYSICAL_TIMING",
        "run_id": 40337484954, "artifact_id": 12658617718,
        "artifact_sha256": digest, "contestants": results,
        "candidate_area_growth_pct": candidate_growth * 100,
        "serial_area_growth_pct": serial_growth * 100,
        "baseline_candidate_area_saving_pct": (1 - bp / bs) * 100,
        "decoded_candidate_area_saving_pct": (1 - dp / ds) * 100,
        "frozen_10pct_growth_gate": "PASS" if max(candidate_growth, serial_growth) <= .10 else "FAIL",
        "area_reinvestment_survives_decoder": dp < ds,
        "physical_signoff": "NOT_MEASURED"
    }


def self_test(path):
    result = audit(path)
    if abs(result["candidate_area_growth_pct"] - 9.5255) > .02:
        raise AssertionError("unexpected candidate growth")
    if result["area_reinvestment_survives_decoder"]:
        raise AssertionError("candidate should lose mapped area advantage")
    if result["frozen_10pct_growth_gate"] != "PASS":
        raise AssertionError("unexpected 10% mapped gate failure")
    try:
        audit(path, "0" * 64)
    except ValueError:
        pass
    else:
        raise AssertionError("corrupt SHA must fail")
    print("BANK_DECODE_MAPPED_INDEPENDENT_AUDIT_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_zip")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(args.artifact_zip)
    print(json.dumps(audit(args.artifact_zip), indent=2, sort_keys=True))
