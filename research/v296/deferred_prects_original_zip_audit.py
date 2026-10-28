#!/usr/bin/env python3
"""Independent fail-closed audit of the original four incomplete pre-CTS ZIPs.

Recovered metrics are intermediate observations, NOT a completed physical pass.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import zipfile

PINNED = {
    "D4_pairwise": (12794977675, "5ec6995b5ce9707fda4906d0bf6b064316894e05eb9856acf9d6d47a0e95e2f1"),
    "D4_serial_onehot": (12794237947, "666cf495e6db09363744b82869c8d7671c855ecf9026041fc93b8d920981b64c"),
    "D8_pairwise": (12794218649, "eceb43084f2e0d3a339bf6cf7d4aff316a84403d97eefae7edd27fc1984f5638"),
    "D8_serial_onehot": (12794458273, "bade1b570b498b823ba8c2e67c8cde8af34f862101a9ec0e46ba1f84f4024063"),
}

def one(pattern, text, name):
    hits = re.findall(pattern, text, re.M)
    if len(hits) != 1:
        raise ValueError(f"Expected exactly one {name}; found {len(hits)}")
    return hits[0]

def audit_zip(path, key):
    aid, expected_sha = PINNED[key]
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError(f"Original ZIP digest mismatch: {key}")
    depth = int(key[1])
    variant = key.split("_", 1)[1]
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        def read(suffix):
            matching = [n for n in names if n == variant + suffix]
            if len(matching) != 1:
                raise ValueError(f"Missing or duplicate {variant + suffix}")
            return z.read(matching[0]).decode()
        log = read(".high.log")
        exit_txt = read(".deferred_prects.exit.txt").strip()
        manifest = json.loads(z.read("deferred_prects_manifest.json"))
        if (manifest["depth"] != depth or manifest["bits"] != (2 if depth == 4 else 3)
                or manifest["clock_ns"] != 3.5 or manifest["rc_multiplier"] != 2.0
                or manifest["density"] != 0.45 or manifest["ports_per_bank"] != 2
                or manifest["control"] != "V295_SERIAL_FIFTH_STAGE"
                or manifest["holdouts"] != "SEALED"):
            raise ValueError(f"Frozen constraints differ: {key}")
        if one(r"^V296_CTS45_EXTRA_REPAIR (\d+)\s*$", log, "control repair") != ("0" if variant == "pairwise" else "1"):
            raise ValueError("Serial repair mismatch")
        if (log.count("V296_CTS45_FIFTH_DONE") == 1) != (variant == "serial_onehot"):
            raise ValueError("Fifth stage mismatch")
        if exit_txt != "EXIT_CODE=4" or log.count("[ERROR STA-0563] report_checks -group_path_count is not a known keyword or flag.") != 1:
            raise ValueError("Original failure not preserved")
        if "V296_DEFERRED_PRECTS_DONE" in log or "V296_DEFERRED_PRECTS_PATHS_END" in log:
            raise ValueError("Unexpected completed diagnostics in failed run")
        if len(re.findall(r"\[ERROR", log)) != 1:
            raise ValueError("Unexpected additional OpenROAD errors")
        def metric(label):
            return Decimal(one(r"^" + re.escape(label) + r"\s+([-+]?\d+(?:\.\d+)?)\s*$", log, label))
        area = metric("V296_DEFERRED_PRECTS_AREA_UM2")
        cap = metric("V296_DEFERRED_PRECTS_CAP_COUNT")
        slew = metric("V296_DEFERRED_PRECTS_SLEW_COUNT")
        setup = one(r"V296_DEFERRED_PRECTS_SETUP_BEGIN\s*worst slack\s+([-+]?\d+(?:\.\d+)?)\s*V296_DEFERRED_PRECTS_SETUP_END", log, "setup block")
        slack = Decimal(setup)
        if not (Decimal(0) < area < Decimal(30000) and cap == 0 and slew == 0 and slack >= Decimal("0.05")):
            raise ValueError(f"Intermediate physical gate failed: {key}")
        return {"artifact_id": aid, "zip_sha256": expected_sha, "depth": depth, "variant": variant,
                "area_um2": str(area), "setup_slack_ns": str(slack), "cap_violations": int(cap),
                "slew_violations": int(slew), "runner_exit_code": 4,
                "status": "INTERMEDIATE_METRICS_PASS_BUT_RUN_FAILED_AT_PATH_REPORT"}

def audit(folder):
    rows = {}
    for key, (aid, _) in PINNED.items():
        rows[key] = audit_zip(folder / f"github-actions-artifact-{aid}.zip", key)
    comparisons = {}
    for depth in (4, 8):
        p, s = rows[f"D{depth}_pairwise"], rows[f"D{depth}_serial_onehot"]
        pa, sa = Decimal(p["area_um2"]), Decimal(s["area_um2"])
        ps, ss = Decimal(p["setup_slack_ns"]), Decimal(s["setup_slack_ns"])
        comparisons[f"D{depth}"] = {
            "area_saving_um2": str(sa - pa),
            "area_saving_percent_of_serial": str((sa - pa) * 100 / sa),
            "setup_slack_difference_ps": str((ps - ss) * 1000),
            "slices_at_30000_um2": {"pairwise": int(Decimal(30000) // pa),
                                    "serial": int(Decimal(30000) // sa)},
            "two_pairwise_slice_budget_um2": str(2 * pa),
            "two_serial_slice_budget_um2": str(2 * sa)}
    return {"source_run": 40629351716,
            "evidence_tier": "INCOMPLETE_PRECTS_ESTIMATED_RC_INTERMEDIATE_METRICS",
            "completed_physical_pair": False, "routed_signoff": False, "gpu_advantage": False,
            "failure": "STA-0563 unsupported report_checks -group_path_count option",
            "rows": rows, "comparisons": comparisons}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--artifact-dir", type=Path, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = audit(a.artifact_dir)
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.output:
        a.output.write_text(output)
    print(output)

if __name__ == "__main__":
    main()
