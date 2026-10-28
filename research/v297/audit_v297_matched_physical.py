#!/usr/bin/env python3
"""Independent, fail-closed V297 matched physical evidence checker.

Never interprets a tool timeout or missing routed artifact as a timing failure
or a pass. Raw evidence is retained for all contestants.
"""
import json
import re
import sys
from pathlib import Path

VARIANTS = ("compact", "maxpair", "rotating")

def field(log, name):
    matches = re.findall(r"^" + re.escape(name) + r"\s+([^\s]+)", log, re.M)
    if len(matches) != 1:
        raise ValueError(f"{name}: expected exactly one occurrence, found {len(matches)}")
    return matches[0]

def slack(log, label):
    start, end = label + "_BEGIN", label + "_END"
    if log.count(start) != 1 or log.count(end) != 1:
        raise ValueError(f"{label}: missing or duplicated marker")
    block = log.split(start, 1)[1].split(end, 1)[0]
    values = re.findall(r"worst\s+slack\s+([-+]?\d+(?:\.\d+)?)", block, re.I)
    if len(values) != 1:
        raise ValueError(f"{label}: no unique numeric worst slack")
    return float(values[0])

def parse(log):
    if log.count("V297_EXTRACTED_DONE") != 1:
        raise ValueError("No unique extracted-RC completion marker")
    if field(log, "V297_FROZEN_CLOCK_NS") != "3.5":
        raise ValueError("Clock mismatch")
    if field(log, "V297_FROZEN_RC_MULTIPLIER") != "2.0":
        raise ValueError("RC mismatch")
    if field(log, "V297_FROZEN_DENSITY") != "0.45":
        raise ValueError("Density mismatch")
    if int(field(log, "V297_IS_ROUTED")) != 1:
        raise ValueError("Not routed")
    area = float(field(log, "V297_EXTRACTED_AREA_UM2"))
    setup = slack(log, "V297_EXTRACTED_MAX_SLACK")
    hold = slack(log, "V297_EXTRACTED_MIN_SLACK")
    drc = int(field(log, "V297_DRC_COUNT"))
    cap = int(field(log, "V297_EXTRACTED_CAP_COUNT"))
    slew = int(field(log, "V297_EXTRACTED_SLEW_COUNT"))
    if not (0 < area < 30000):
        raise ValueError("Invalid area or tile budget")
    feasible = setup >= 0.05 and hold >= 0 and drc == 0 and cap == 0 and slew == 0
    return dict(area_um2=area, setup_slack_ns=setup, hold_slack_ns=hold,
                drc=drc, cap_violations=cap, slew_violations=slew, feasible=feasible)

def self_test():
    good = """V297_FROZEN_CLOCK_NS 3.5
V297_FROZEN_RC_MULTIPLIER 2.0
V297_FROZEN_DENSITY 0.45
V297_DRC_COUNT 0
V297_IS_ROUTED 1
V297_EXTRACTED_AREA_UM2 123.4
V297_EXTRACTED_MAX_SLACK_BEGIN
worst slack 0.060
V297_EXTRACTED_MAX_SLACK_END
V297_EXTRACTED_MIN_SLACK_BEGIN
worst slack 0.010
V297_EXTRACTED_MIN_SLACK_END
V297_EXTRACTED_CAP_COUNT 0
V297_EXTRACTED_SLEW_COUNT 0
V297_EXTRACTED_DONE
"""
    assert parse(good)["feasible"]
    assert not parse(good.replace("worst slack 0.010", "worst slack -0.001"))["feasible"]
    assert not parse(good.replace("V297_DRC_COUNT 0", "V297_DRC_COUNT 1"))["feasible"]
    assert not parse(good.replace("V297_EXTRACTED_CAP_COUNT 0", "V297_EXTRACTED_CAP_COUNT 1"))["feasible"]
    for bad in (good.replace("V297_EXTRACTED_DONE", ""),
                good.replace("V297_FROZEN_CLOCK_NS 3.5", "V297_FROZEN_CLOCK_NS 6.0"),
                good.replace("V297_EXTRACTED_MAX_SLACK_BEGIN", ""),
                good + "V297_EXTRACTED_DONE\n"):
        try:
            parse(bad)
        except ValueError:
            continue
        raise AssertionError("Negative mutation escaped checker")
    print("V297_PHYSICAL_AUDIT_SELF_TEST_PASS")

def audit(root):
    root = Path(root)
    result = {"method": "pinned Nangate45, 3.5 ns, 2x RC, matched registered shell",
              "variants": {}, "scientific_status": "NO_PHYSICAL_PERFORMANCE_CLAIM"}
    common_hashes = None
    for v in VARIANTS:
        row = {"status": "CENSORED_OR_FAILED"}
        log_path = root / f"{v}.physical.log"
        exit_path = root / f"{v}.exit.txt"
        try:
            if not exit_path.is_file():
                raise ValueError("Missing runner exit code")
            exit_code = int(exit_path.read_text().strip())
            row["runner_exit_code"] = exit_code
            if exit_code != 0:
                raise ValueError(f"Nonzero runner exit {exit_code}")
            for suffix in ("physical.log", "spef", "final.def", "inputs.sha256",
                           "openroad.version", "synth.log"):
                p = root / f"{v}.{suffix}"
                if not p.is_file() or p.stat().st_size == 0:
                    raise ValueError(f"Missing {p.name}")
            hashes = (root / f"{v}.inputs.sha256").read_text().strip().splitlines()
            if common_hashes is None:
                common_hashes = hashes
            elif common_hashes != hashes:
                raise ValueError("Input provenance mismatch between contestants")
            row.update(parse(log_path.read_text(errors="replace")))
            row["status"] = "COMPLETE_EXTRACTED"
        except (ValueError, OSError) as exc:
            row["reason"] = str(exc)
        result["variants"][v] = row
    rows = result["variants"]
    if all(rows[v]["status"] == "COMPLETE_EXTRACTED" for v in VARIANTS):
        c, m, r = (rows[v] for v in VARIANTS)
        result["scientific_status"] = (
            "MAXPAIR_PHYSICAL_AREA_DOMINATES; QUEUE_CHECK_REQUIRED"
            if m["feasible"] and c["feasible"] and m["area_um2"] <= c["area_um2"]
            else "PHYSICAL_COMPLETE; NO_UNCONDITIONAL_WIN"
        )
        result["compact_vs_maxpair_area_ratio"] = c["area_um2"] / m["area_um2"]
    (root / "v297_physical_independent_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result

if __name__ == "__main__":
    self_test()
    if len(sys.argv) > 1 and sys.argv[1] != "--self-test":
        audit(sys.argv[1])
