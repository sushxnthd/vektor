#!/usr/bin/env python3
"""Independent fail-closed V296 fourth-round high-RC extracted-PPA audit.

New experiment only; never reclassifies the frozen six-case physical failure.
"""
import json
import math
from pathlib import Path
import re
import sys

from audit_detailed_route import extract_metric

VARIANTS = ("original", "optimized", "pairwise")
REQUIRED = (
    "V296_CLOCK_PERIOD_NS 3.5",
    "V296_CAP_MARGIN_PERCENT 20",
    "V296_THIRD_PHYSICAL_DONE",
    "V296_FOURTH_BEGIN",
    "V296_FOURTH_SLEW_MARGIN_PERCENT 25",
    "V296_FOURTH_DETAIL_BEGIN",
    "V296_FOURTH_IS_ROUTED 1",
    "V296_FOURTH_DETAIL_RC_MULTIPLIER 2.0",
    "V296_FOURTH_HOLD_BEGIN",
    "V296_FOURTH_HOLD_END",
    "V296_FOURTH_SLEW_VIOLATORS_BEGIN",
    "V296_FOURTH_SLEW_VIOLATORS_END",
    "V296_FOURTH_DONE",
)


def parse_log(log):
    for token in REQUIRED:
        if token not in log:
            raise ValueError("Missing protocol marker: " + token)
    drc = re.search(r"(?m)^V296_FOURTH_DRC_COUNT (\d+)\r?$", log)
    hold = re.search(
        r"(?ms)^V296_FOURTH_HOLD_BEGIN\r?\n(.*?)^V296_FOURTH_HOLD_END\r?$",
        log,
    )
    if not drc or not hold:
        raise ValueError("Missing DRC or hold block")
    match = re.search(
        r"(?mi)^worst slack(?:\s+min)?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$",
        hold.group(1),
    )
    if not match:
        raise ValueError("Missing finite hold slack")
    row = extract_metric(log, "extracted_fourth")
    row["hold_ns"] = float(match.group(1))
    row["drc"] = int(drc.group(1))
    if not math.isfinite(row["hold_ns"]):
        raise ValueError("Nonfinite hold slack")
    return row


def audit(root):
    rows = {}
    for variant in VARIANTS:
        stem = variant + ".high"
        log = (root / (stem + ".log")).read_text()
        row = parse_log(log)
        for suffix in (".fourth.def", ".fourth.spef", ".fourth.drc.rpt", ".fourth.guide"):
            file = root / (stem + suffix)
            if not file.is_file():
                raise ValueError(f"{stem}: missing {suffix}")
            if suffix != ".fourth.drc.rpt" and file.stat().st_size == 0:
                raise ValueError(f"{stem}: empty {suffix}")
        spef = (root / (stem + ".fourth.spef")).read_text()
        if "*D_NET" not in spef or "*SPEF" not in spef:
            raise ValueError(f"{stem}: malformed SPEF")
        rows[variant] = row

    cand = rows["pairwise"]
    controls = [rows["original"], rows["optimized"]]
    best_area = min(x["area_um2"] for x in controls)
    best_slack = max(x["setup_ns"] for x in controls)
    area_saving_pct = 100 * (best_area - cand["area_um2"]) / best_area
    lead_ns = cand["setup_ns"] - best_slack
    clean = cand["slew"] == 0 and cand["cap"] == 0 and cand["drc"] == 0
    timed = cand["setup_ns"] >= 0 and cand["hold_ns"] >= 0
    predicted = area_saving_pct >= 10 and lead_ns >= 0.20
    decision = (
        "TARGETED_HIGH_RC_PROVISIONAL_PASS"
        if clean and timed and predicted
        else "FOURTH_ROUND_HIGH_RC_FALSIFIED"
    )
    return {
        "decision": decision,
        "candidate_clean": clean,
        "candidate_timed": timed,
        "prediction_P1_supported": clean and timed,
        "prediction_P2_supported": predicted,
        "area_saving_pct_vs_smaller_control": area_saving_pct,
        "setup_lead_ns_vs_faster_control": lead_ns,
        "all_controls_clean": all(x["slew"] == 0 and x["cap"] == 0 and x["drc"] == 0 for x in controls),
        "all_controls_timed": all(x["setup_ns"] >= 0 and x["hold_ns"] >= 0 for x in controls),
        "rows": rows,
        "frozen_six_case_gate": "DETAILED_PHYSICAL_GATE_FAIL",
        "holdouts": "SEALED",
        "limitations": "Pre-CTS high-RC-only extracted result; no equal-resource control Pareto, signoff, power, tile or throughput validation.",
    }


def self_test():
    sample = (
        "\n".join(REQUIRED) + "\n"
        + "V296_FOURTH_DRC_COUNT 0\n"
        + "V296_FOURTH_HOLD_BEGIN\nworst slack min 0.12\nV296_FOURTH_HOLD_END\n"
        + "V296_STAGE_BEGIN extracted_fourth\n"
        + "V296_METRIC stage=extracted_fourth area_um2=5000 slew=0 cap=0\n"
        + "worst slack max 0.36\nV296_STAGE_END extracted_fourth\n"
    )
    # The synthetic log contains a duplicate hold marker; the parser must
    # select the complete hold block and reject malformed evidence.
    assert parse_log(sample)["setup_ns"] == 0.36
    for altered in (
        sample.replace("V296_FOURTH_SLEW_MARGIN_PERCENT 25", "V296_FOURTH_SLEW_MARGIN_PERCENT 10"),
        sample.replace("V296_FOURTH_DRC_COUNT 0", "V296_FOURTH_DRC_COUNT x"),
        sample.replace("worst slack min 0.12", "worst slack min nan"),
        sample.replace("V296_FOURTH_DONE", "V296_FOURTH_ABORT"),
    ):
        try:
            parse_log(altered)
        except ValueError:
            continue
        raise AssertionError("Accepted malformed physical evidence")
    print("V296_FOURTH_HIGH_RC_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_fourth_high_rc.py ROOT | --self-test")
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    try:
        result = audit(root)
    except (OSError, ValueError) as exc:
        result = {"decision": "FOURTH_ROUND_INCOMPLETE_EVIDENCE", "error": str(exc), "holdouts": "SEALED"}
    (root / "fourth_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["decision"] != "TARGETED_HIGH_RC_PROVISIONAL_PASS":
        raise SystemExit(3)
