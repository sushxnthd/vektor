#!/usr/bin/env python3
"""Independent SHA-pinned candidate-only extracted-RC falsification from original Actions ZIP.

Standard library only. A successful replay of the negative result is not a
physical pass, a matched serial comparison, or GPU evidence.
"""
import argparse
import hashlib
import json
import math
import re
import tempfile
import zipfile
from pathlib import Path

RUN_ID = 40469489684
ARTIFACT_ID = 12721519936
ARTIFACT_SHA256 = "7342c8e1b16b5193279c6d2ad5d15ddb6cb849c9fc0aa06a984297efeef6404b"
RTL_TOP = "v296_tile_slice_fixed_word"
SETUP_GUARD_NS = 0.050
HOLD_GUARD_NS = 0.0
AREA_CEILING_UM2 = 30000.0


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_match(pattern, content, label):
    matches = re.findall(pattern, content, flags=re.MULTILINE | re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {label}, found {len(matches)}")
    return matches[0]


def check(zip_path, expected_sha=ARTIFACT_SHA256):
    raw = Path(zip_path).read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError("Artifact ZIP SHA-256 mismatch")
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or any(n.startswith("/") or ".." in Path(n).parts for n in names):
            raise ValueError("Duplicate or unsafe archive paths")
        required = (
            "fixed_word_postcts_manifest.json", "pairwise.tile.audit.json",
            "pairwise.high.log", "pairwise.high.cts45.drc.rpt",
            "pairwise.high.cts45.def", "pairwise.high.cts45.spef",
            "pairwise.inputs.sha256", "pairwise.fixed_word_postcts.exit.txt",
            "run_fixed_word_postcts.sh", "run_bank_decode_postcts.sh",
            "cts45_tile.tcl",
        )
        if not set(required).issubset(names):
            raise ValueError("Missing physical/provenance evidence")
        manifest = json.loads(z.read("fixed_word_postcts_manifest.json"))
        expected_manifest = {
            "rtl_top": RTL_TOP, "same_rtl_for_both": True,
            "strongest_serial_fifth_stage_required": True,
            "candidate_extra_repair": 0, "serial_extra_repair": 1,
            "clock_ns": 3.5, "rc_multiplier": 2.0,
            "placement_density": 0.45, "holdouts": "SEALED",
        }
        if any(manifest.get(k) != v for k, v in expected_manifest.items()):
            raise ValueError("Changed frozen candidate protocol")
        for filename, key in (
            ("run_fixed_word_postcts.sh", "derived_runner_sha256"),
            ("run_bank_decode_postcts.sh", "source_runner_sha256"),
            ("cts45_tile.tcl", "unchanged_physical_tcl_sha256"),
        ):
            if sha(z.read(filename)) != manifest[key]:
                raise ValueError("Changed source/physical constraint: " + filename)
        inputs = z.read("pairwise.inputs.sha256").decode()
        source = "research/v296/" + RTL_TOP + ".sv"
        rtl_hashes = [line.split()[0] for line in inputs.splitlines()
                      if line.endswith("  " + source)]
        if rtl_hashes != [manifest["source_rtl_sha256"]]:
            raise ValueError("Wrong RTL source hash")
        if "V296_FIXED_WORD_POSTCTS_RUN_EXIT_CODE=0" not in z.read(
                "pairwise.fixed_word_postcts.exit.txt").decode():
            raise ValueError("Nonzero or missing physical runner exit")
        if (z.getinfo("pairwise.high.cts45.def").file_size < 100000 or
                z.getinfo("pairwise.high.cts45.spef").file_size < 100000):
            raise ValueError("Missing routed DEF or extracted SPEF")
        if z.read("pairwise.high.cts45.drc.rpt").strip():
            raise ValueError("Nonempty DRC report")
        log = z.read("pairwise.high.log").decode(errors="replace")
        for marker in (
            "V296_CTS45_EXTRA_REPAIR 0", "V296_CTS45_CLOCKS_PROPAGATED 1",
            "V296_CTS45_RC_MULTIPLIER 2.0", "V296_CTS45_DRC_COUNT 0",
            "V296_CTS45_IS_ROUTED 1", "V296_CTS45_DONE",
            "V296_STAGE_BEGIN cts45_extracted", "V296_STAGE_END cts45_extracted",
            "V296_CTS45_HOLD_BEGIN", "V296_CTS45_HOLD_END",
        ):
            if log.count(marker) != 1:
                raise ValueError("Missing or ambiguous extracted marker: " + marker)
        hold_section = unique_match(
            r"V296_CTS45_HOLD_BEGIN\s*\n(.*?)\nV296_CTS45_HOLD_END",
            log, "hold section")
        hold = float(unique_match(r"worst slack\s+(-?[0-9.]+)", hold_section, "hold slack"))
        extracted_section = unique_match(
            r"V296_STAGE_BEGIN cts45_extracted\s*\n(.*?)\nV296_STAGE_END cts45_extracted",
            log, "extracted stage")
        area, slew, cap = unique_match(
            r"V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=([0-9]+) cap=([0-9]+)",
            extracted_section, "extracted area/electrical metrics")
        setup = float(unique_match(
            r"worst slack\s+(-?[0-9.]+)", extracted_section, "setup slack"))
        area, slew, cap = float(area), int(slew), int(cap)
        row = json.loads(z.read("pairwise.tile.audit.json"))
        f = row["final"]
        for key, value in (
            ("area_um2", area), ("setup_ns", setup), ("hold_ns", hold),
            ("slew", slew), ("cap", cap),
        ):
            if not math.isfinite(float(value)) or abs(float(f[key]) - float(value)) > 1e-6:
                raise ValueError("Independent log/audit mismatch: " + key)
        if row.get("variant") != "pairwise" or row.get("complete") is not True:
            raise ValueError("Incomplete candidate evidence")
        if not re.search(r"\[INFO DRT-0198\] Complete detail routing\.", log):
            raise ValueError("Detailed routing not complete")
        passed = dict(
            setup=setup >= SETUP_GUARD_NS, hold=hold >= HOLD_GUARD_NS,
            cap=cap == 0, slew=slew == 0, drc=True,
            area=area <= AREA_CEILING_UM2,
        )
        feasible = all(passed.values())
        if row.get("feasible") != feasible:
            raise ValueError("Mismatch with original feasibility classification")
        verdict = ("CANDIDATE_FIXED_WORD_REPAIR_REJECTED" if not feasible
                   else "CANDIDATE_ONLY_GATES_PASS_SERIAL_PENDING")
        return {
            "decision": verdict,
            "evidence_tier": "ORIGINAL_SHA256_VERIFIED_ROUTED_EXTRACTED_RC_NOT_SIGNOFF",
            "github_run": RUN_ID, "artifact_id": ARTIFACT_ID,
            "artifact_zip_sha256": sha(raw),
            "physical": {
                "area_um2": area, "setup_ns": setup, "hold_ns": hold,
                "cap_violations": cap, "slew_violations": slew,
                "drc_violations": 0,
            },
            "frozen_gates": passed,
            "setup_guard_remaining_ps": round(1000 * (setup - SETUP_GUARD_NS), 6),
            "hold_shortfall_ps": round(1000 * max(0, HOLD_GUARD_NS - hold), 6),
            "prects_to_extracted_setup_deterioration_ps":
                round(1000 * (0.230183 - setup), 6),
            "prects_to_extracted_hold_deterioration_ps":
                round(1000 * (0.112255 - hold), 6),
            "serial_matched_verdict": "PENDING",
            "retired_variant": "fixed_word_2word_RF_implementation_only",
            "sole_provisional_mechanism": "V296_pairwise_bank_admission",
            "production_deep_bank_transfer": False,
            "measured_gpu_speedup": False, "holdouts": "SEALED",
        }


def self_test(zip_path):
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(zip_path).read_bytes()
        bad = Path(tmp) / "bad.zip"
        bad.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        try:
            check(bad)
        except ValueError as error:
            assert "SHA-256 mismatch" in str(error)
        else:
            raise AssertionError("Corrupted artifact accepted")
        result = check(zip_path)
        assert result["decision"] == "CANDIDATE_FIXED_WORD_REPAIR_REJECTED"
        assert result["frozen_gates"]["hold"] is False
        assert all(value for key, value in result["frozen_gates"].items()
                   if key != "hold")
        assert result["hold_shortfall_ps"] == 12.622
    print("V296_FIXED_WORD_ORIGINAL_ARTIFACT_INDEPENDENT_HOLD_FALSIFICATION_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_zip", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test(args.artifact_zip)
    result = check(args.artifact_zip)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
