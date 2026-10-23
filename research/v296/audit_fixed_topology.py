#!/usr/bin/env python3
"""Independent fail-closed V296 fixed-topology sensitivity audit; not signoff."""
import hashlib
import json
import math
import pathlib
import re
import sys

VARIANTS = ("original", "optimized", "pairwise")
RC = ("05", "10", "20")
LOAD = ("025", "050", "100")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stage(log, key):
    pat = r"(?m)^V296_STAGE_BEGIN " + re.escape(key) + r"\r?\n(.*?)^V296_STAGE_END " + re.escape(key) + r"(?:\r?\n|\Z)"
    m = re.search(pat, log, re.S | re.M)
    if not m:
        raise ValueError("Missing complete stage " + key)
    b = m.group(1)
    p = re.search(r"V296_METRIC stage=" + re.escape(key) + r" area_um2=([0-9.eE+-]+) slew=(\d+) cap=(\d+)", b)
    s = re.search(r"worst slack(?:\s+max)?\s+([-+]?[0-9]+(?:\.[0-9]+)?)", b, re.I)
    if not p or not s:
        raise ValueError("Missing metric " + key)
    area, slack = float(p.group(1)), float(s.group(1))
    if not math.isfinite(area) or area <= 0 or not math.isfinite(slack):
        raise ValueError("Invalid numerical metric")
    return dict(area_um2=area, slack_ns=slack, slew=int(p.group(2)), cap=int(p.group(3)))

def audit(root):
    rows, hashes = {}, {}
    for variant in VARIANTS:
        prefix = variant + ".nominal"
        log = (root / (prefix + ".log")).read_text()
        if "V296_CLOCK_PERIOD_NS 3.5" not in log or "V296_PHYSICAL_DONE" not in log:
            raise ValueError("Nominal physical result missing: " + variant)
        if "V296_FIXED_BEGIN" not in log or "V296_FIXED_END" not in log:
            raise ValueError("Fixed-topology sweep incomplete: " + variant)
        reference = stage(log, "routed")
        h = digest(root / (prefix + ".routed.def"))
        if digest(root / (prefix + ".fixed_reference.def")) != h:
            raise ValueError("Nominal DEF mismatch: " + variant)
        hashes[variant] = h
        rows[variant] = {}
        for rc in RC:
            for load in LOAD:
                key = "fixed_rc" + rc + "_load" + load
                row = stage(log, key)
                if digest(root / (prefix + "." + key + ".def")) != h:
                    raise ValueError("Topology mutated: " + variant + "/" + key)
                if abs(row["area_um2"] - reference["area_um2"]) > 0.0001:
                    raise ValueError("Cell area mutated: " + variant + "/" + key)
                rows[variant][key] = row
        same = rows[variant]["fixed_rc10_load050"]
        if (abs(same["slack_ns"] - reference["slack_ns"]) > 0.0001 or
            same["slew"] != reference["slew"] or same["cap"] != reference["cap"]):
            raise ValueError("Nominal recheck differs: " + variant)
    comparisons = {}
    all_clean, all_timed, smaller, faster = True, True, True, True
    candidate_only = []
    for rc in RC:
        for load in LOAD:
            key = "fixed_rc" + rc + "_load" + load
            cand = rows["pairwise"][key]
            controls = [rows[v][key] for v in ("original", "optimized")]
            area_save = min(x["area_um2"] for x in controls) - cand["area_um2"]
            slack_lead = cand["slack_ns"] - max(x["slack_ns"] for x in controls)
            smaller &= area_save > 0
            faster &= slack_lead > 0
            all_clean &= all(x["slew"] == 0 and x["cap"] == 0 for x in [cand] + controls)
            all_timed &= all(x["slack_ns"] >= 0 for x in [cand] + controls)
            if (cand["slew"] + cand["cap"] > 0 and
                all(x["slew"] + x["cap"] == 0 for x in controls)):
                candidate_only.append(key)
            comparisons[key] = dict(area_saving_um2=area_save, slack_lead_ns=slack_lead)
    decision = ("FIXED_TOPOLOGY_PROVISIONAL_PASS" if
                smaller and faster and all_clean and all_timed and not candidate_only else
                "FIXED_TOPOLOGY_SENSITIVITY_FAIL")
    return dict(decision=decision, holdouts="SEALED", clock_ns=3.5,
                evidence="fixed-DEF global-route RC estimate; not detailed SPEF or signoff",
                topology_sha256=hashes, rows=rows, comparisons=comparisons,
                candidate_only_electrical=candidate_only,
                smaller_all=smaller, slack_lead_all=faster,
                all_electrically_clean=all_clean, all_meet_clock=all_timed,
                note="Independent adaptive nine-case gate remains failed. Same-clock throughput gain = 0.")

def self_test():
    sample = ("V296_STAGE_BEGIN fixed_rc10_load050\n"
              "V296_METRIC stage=fixed_rc10_load050 area_um2=5299.784 slew=0 cap=0\n"
              "worst slack max 0.764527\nV296_STAGE_END fixed_rc10_load050\n")
    assert stage(sample, "fixed_rc10_load050")["slack_ns"] == 0.764527
    try:
        stage(sample, "fixed_rc10_load05")
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted prefix collision")
    print("V296_FIXED_AUDIT_SELFTEST_PASS")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        sys.exit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_fixed_topology.py BUILD_DIR | --self-test")
    root = pathlib.Path(sys.argv[1])
    try:
        result = audit(root)
    except (OSError, ValueError) as exc:
        result = dict(decision="FIXED_TOPOLOGY_UNSUPPORTED", holdouts="SEALED", error=str(exc))
    root.mkdir(parents=True, exist_ok=True)
    (root / "fixed_topology_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "comparisons")}, indent=2))
    if result["decision"] != "FIXED_TOPOLOGY_PROVISIONAL_PASS":
        sys.exit(3)
