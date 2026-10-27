#!/usr/bin/env python3
"""Independent D4/D8 OpenROAD detailed-route convergence audit from original ZIPs.

Download the four artifact ZIPs from GitHub Actions run #40557136436.
Keep filenames github-actions-artifact-<artifact_id>.zip, then invoke
python3 research/v296/deep_bank_detailed_route_forensics.py /path/to/zips
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ARTIFACTS = {
    "D4_pairwise": (12770962531, "pairwise", "9a1ad570dacfc3895336e2ec279b5e057a0d54d0ec8e511dc884f04c20b2958d", 124),
    "D4_serial_onehot": (12769708334, "serial_onehot", "edeb136bc054eddf7434119115df198e7d4403c9bd01c0a726df7fb30519755b", 0),
    "D8_pairwise": (12769775926, "pairwise", "92a84c3923eb62cd506241bcb1d8da06cfcfbd6a13328c8e050b14f301086f4b", 0),
    "D8_serial_onehot": (12769658115, "serial_onehot", "63f8e5db3a0d8c460f384b6804462eb95fdd35d461f5d2edfed9d24476187dd4", 124),
}


def inspect(archive, variant, expected_sha, expected_exit):
    raw = archive.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected_sha, "artifact SHA-256 mismatch"
    with zipfile.ZipFile(archive) as z:
        s = z.read(f"{variant}.high.log").decode("utf-8", errors="replace")
        exit_text = z.read(f"{variant}.deep_bank.exit.txt").decode()
    assert f"EXIT_CODE={expected_exit}" in exit_text
    starts = [(int(m.group(1)), m.start()) for m in re.finditer(
        r"Start (\d+)(?:th|st|nd|rd) optimization iteration", s)]
    counts = [int(x) for x in re.findall(r"Number of violations = (\d+)", s)]
    assert starts, "no detailed-route iteration found"
    last_started, offset = starts[-1]
    progress = re.findall(r"Completing (\d+)% with (\d+) violations", s[offset:])
    last_progress = {"percent": int(progress[-1][0]),
                     "violations": int(progress[-1][1])} if progress else None
    completed = min(len(starts), len(counts))
    assert abs(len(starts) - len(counts)) <= 1
    if expected_exit == 0:
        assert counts and counts[-1] == 0, "complete run missing zero final DRC"
    else:
        assert not counts or counts[-1] != 0, "timeout after zero DRC needs investigation"
    return {"zip_sha256_verified": True, "exit_code": expected_exit,
            "iterations_started": len(starts), "iterations_completed": completed,
            "last_iteration_index": last_started,
            "completed_iteration_drc_counts": counts,
            "last_completed_drc_count": counts[-1] if counts else None,
            "last_partial_iteration_progress": last_progress,
            "zero_drc_routing_completion": expected_exit == 0 and counts[-1] == 0}


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = {}
    for label, (artifact_id, variant, sha, rc) in ARTIFACTS.items():
        p = base / f"github-actions-artifact-{artifact_id}.zip"
        results[label] = inspect(p, variant, sha, rc)
    assert results["D4_pairwise"]["last_completed_drc_count"] == 19252
    assert results["D8_serial_onehot"]["last_partial_iteration_progress"]["violations"] == 33054
    assert results["D4_serial_onehot"]["iterations_completed"] == 26
    assert results["D8_pairwise"]["iterations_completed"] == 12
    print("V296_DEEP_ROUTE_ORIGINAL_ZIP_SHA_AND_CONVERGENCE_PASS")
    print(json.dumps({"source_run": 40557136436, "results": results}, indent=2))


if __name__ == "__main__":
    main()
