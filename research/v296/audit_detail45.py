#!/usr/bin/env python3
"""Fail-closed independent audit for matched 45% extracted detailed-route experiment.

Incomplete control is not a candidate victory. This is pre-CTS, not signoff.
"""
import json
import math
import re
import sys
from pathlib import Path

VARIANTS = ("pairwise", "serial_onehot")
NUM = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
AREA_CEILING = 7400.0
SETUP_GUARDBAND_NS = 0.050


def stage_metrics(log, stage):
    match = re.search(r"(?ms)^V296_STAGE_BEGIN " + re.escape(stage) +
                      r"\r?\n(.*?)^V296_STAGE_END " + re.escape(stage) + r"\r?$", log)
    if not match:
        return None
    body = match.group(1)
    a = re.search(r"(?m)^V296_METRIC stage=" + re.escape(stage) +
                  r" area_um2=" + NUM + r" slew=(\d+) cap=(\d+)\r?$", body)
    t = re.search(r"(?mi)^worst slack(?:\s+max)?\s+" + NUM + r"\s*$", body)
    if not a or not t:
        raise ValueError("Malformed stage " + stage)
    result = dict(area_um2=float(a.group(1)), slew=int(a.group(2)),
                  cap=int(a.group(3)), setup_ns=float(t.group(1)))
    if not all(math.isfinite(x) for x in result.values()) or result["area_um2"] <= 0:
        raise ValueError("Nonfinite or invalid stage " + stage)
    return result


def audit_case(root, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown contestant")
    logpath = root / (variant + ".high.log")
    if not logpath.is_file():
        return {"variant": variant, "complete": False, "error": "missing log"}
    log = logpath.read_text(errors="replace")
    lines = set(log.splitlines())
    extra = int(variant == "serial_onehot")
    markers = ("V296_CLOCK_PERIOD_NS 3.5", "V296_PLACE_DENSITY 0.45",
               "V296_PARETO_VARIANT " + variant,
               "V296_PARETO_EXTRA_REPAIR " + str(extra))
    for marker in markers:
        if marker not in lines:
            raise ValueError("Missing frozen marker " + marker)
    for prefix in ("V296_CLOCK_PERIOD_NS ", "V296_PLACE_DENSITY ",
                   "V296_PARETO_VARIANT ", "V296_PARETO_EXTRA_REPAIR "):
        if any(line.startswith(prefix) and line not in markers for line in lines):
            raise ValueError("Contradictory frozen marker " + prefix)
    stages = ("placed", "repaired_first", "routed_first", "repaired_second",
              "routed_final", "repaired_third", "routed_third",
              "pareto_fourth_repaired", "pareto_fourth_routed",
              "pareto_control_fifth_repaired", "pareto_control_fifth_routed",
              "pareto_extracted")
    found = {s: v for s in stages if (v := stage_metrics(log, s)) is not None}
    last = next((s for s in reversed(stages) if s in found), None)
    result = {"variant": variant, "complete": False, "last_stage": last,
              "last_metrics": found.get(last),
              "evidence_tier": "ideal-clock detailed-route OpenRCX; not CTS/signoff"}
    if "V296_PARETO_DONE" not in lines:
        return result
    if "V296_PARETO_RC_MULTIPLIER 2.0" not in lines or any(
        x.startswith("V296_PARETO_RC_MULTIPLIER ") and
        x != "V296_PARETO_RC_MULTIPLIER 2.0" for x in lines
    ):
        raise ValueError("Wrong or missing extracted RC multiplier")
    for marker in ("V296_PARETO_FOURTH_DONE", "V296_PARETO_DETAIL_BEGIN",
                   "V296_PARETO_IS_ROUTED 1", "V296_PARETO_HOLD_BEGIN",
                   "V296_PARETO_HOLD_END"):
        if marker not in lines:
            raise ValueError("Incomplete detailed-route marker " + marker)
    if extra and "V296_PARETO_CONTROL_FIFTH_DONE" not in lines:
        raise ValueError("Missing control fifth repair")
    if not extra and "V296_PARETO_CONTROL_FIFTH_DONE" in lines:
        raise ValueError("Candidate received control-only repair")
    drc = re.search(r"(?m)^V296_PARETO_DRC_COUNT (\d+)\r?$", log)
    hold = re.search(r"(?ms)^V296_PARETO_HOLD_BEGIN\r?\n(.*?)^V296_PARETO_HOLD_END", log)
    hold_value = (re.search(r"(?mi)^worst slack(?:\s+min)?\s+" + NUM + r"\s*$",
                            hold.group(1)) if hold else None)
    if not drc or not hold_value or "pareto_extracted" not in found:
        raise ValueError("Missing DRC, extracted setup, or hold")
    files = [root / (variant + ".high." + ext) for ext in
             ("pareto.def", "pareto.spef", "pareto.drc.rpt")]
    if any(not p.is_file() for p in files) or files[0].stat().st_size <= 0 or files[1].stat().st_size <= 0:
        raise ValueError("Missing detailed-route DEF/SPEF/DRC report")
    spef = files[1].read_text(errors="replace")
    if "*SPEF" not in spef or "*D_NET" not in spef:
        raise ValueError("Malformed extracted SPEF")
    v = dict(found["pareto_extracted"])
    v["hold_ns"] = float(hold_value.group(1))
    v["drc"] = int(drc.group(1))
    if not math.isfinite(v["hold_ns"]):
        raise ValueError("Nonfinite hold slack")
    result.update(complete=True, final=v,
                  feasible=(v["area_um2"] <= AREA_CEILING and
                            v["setup_ns"] >= SETUP_GUARDBAND_NS and
                            v["hold_ns"] >= 0 and v["slew"] == 0 and
                            v["cap"] == 0 and v["drc"] == 0))
    return result


def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = audit_case(root, variant)
        except (ValueError, OSError) as e:
            rows[variant] = {"variant": variant, "complete": False, "error": str(e)}
    p, c = (rows[x] for x in VARIANTS)
    decision = "INCOMPLETE_NO_VICTORY"
    comparison = None
    if p.get("complete") and c.get("complete"):
        pv, cv = p["final"], c["final"]
        saving = (cv["area_um2"] - pv["area_um2"]) / cv["area_um2"]
        lead = pv["setup_ns"] - cv["setup_ns"]
        comparison = {"area_saving_fraction": saving, "setup_lead_ns": lead,
                      "candidate_feasible": p["feasible"], "control_feasible": c["feasible"],
                      "strict_equal_consumed_area": False}
        if not p["feasible"]:
            decision = "CANDIDATE_PHYSICAL_GATE_FAIL"
        elif not c["feasible"]:
            decision = "CONTROL_INFEASIBLE_NO_MATCHED_PARETO_CLAIM"
        elif saving >= 0.10 and lead >= 0.20:
            decision = "PREDICTED_PARETO_SURVIVES_EXTRACTED_IDEAL_CLOCK"
        else:
            decision = "PREDICTED_PARETO_FALSIFIED"
    elif p.get("complete") and not p.get("feasible"):
        decision = "CANDIDATE_PHYSICAL_GATE_FAIL"
    return {"decision": decision, "rows": rows, "comparison": comparison,
            "clock_tree": "NOT_EVALUATED", "power": "NOT_EVALUATED",
            "equal_consumed_area": "NOT_EVALUATED", "workload_holdouts": "SEALED"}


def self_test():
    import tempfile
    def block(stage, area=6000, slack=0.3):
        return (f"V296_STAGE_BEGIN {stage}\nV296_METRIC stage={stage} "
                f"area_um2={area} slew=0 cap=0\nworst slack {slack}\n"
                f"V296_STAGE_END {stage}\n")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for variant in VARIANTS:
            extra = int(variant == "serial_onehot")
            area = 6000 if variant == "pairwise" else 7000
            setup = 0.5 if variant == "pairwise" else 0.2
            log = ("V296_CLOCK_PERIOD_NS 3.5\nV296_PLACE_DENSITY 0.45\n"
                   f"V296_PARETO_VARIANT {variant}\nV296_PARETO_EXTRA_REPAIR {extra}\n"
                   "V296_PARETO_RC_MULTIPLIER 2.0\nV296_PARETO_FOURTH_DONE\n"
                   + ("V296_PARETO_CONTROL_FIFTH_DONE\n" if extra else "") +
                   "V296_PARETO_DETAIL_BEGIN\nV296_PARETO_IS_ROUTED 1\n"
                   "V296_PARETO_DRC_COUNT 0\nV296_PARETO_HOLD_BEGIN\n"
                   "worst slack 0.2\nV296_PARETO_HOLD_END\n" +
                   block("pareto_extracted", area, setup) + "V296_PARETO_DONE\n")
            (root / (variant + ".high.log")).write_text(log)
            (root / (variant + ".high.pareto.def")).write_text("VERSION 5.8 ;\n")
            (root / (variant + ".high.pareto.spef")).write_text('*SPEF "IEEE 1481-1998"\n*D_NET x 1\n')
            (root / (variant + ".high.pareto.drc.rpt")).write_text("")
            assert audit_case(root, variant)["feasible"]
            assert stage_metrics(log.replace("worst slack " + str(setup),
                                             "worst slack max " + str(setup)),
                                 "pareto_extracted")["setup_ns"] == setup
            for wrong in ("V296_PLACE_DENSITY 0.65", "V296_CLOCK_PERIOD_NS 4.0",
                          "V296_PARETO_RC_MULTIPLIER 1.0"):
                prefix = wrong.split()[0]
                broken = log.replace(next(x for x in log.splitlines() if x.startswith(prefix)), wrong)
                (root / (variant + ".high.log")).write_text(broken)
                try:
                    audit_case(root, variant)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Wrong physical constraint accepted")
            (root / (variant + ".high.log")).write_text(log)
        assert aggregate(root)["decision"] == "PREDICTED_PARETO_SURVIVES_EXTRACTED_IDEAL_CLOCK"
        p = root / "pairwise.high.log"
        clean = p.read_text()
        p.write_text(clean.replace("V296_PARETO_DRC_COUNT 0", "V296_PARETO_DRC_COUNT 1"))
        assert aggregate(root)["decision"] == "CANDIDATE_PHYSICAL_GATE_FAIL"
        p.write_text(clean.replace("V296_PARETO_DONE", "V296_PARETO_ABORTED"))
        assert aggregate(root)["decision"] == "INCOMPLETE_NO_VICTORY"
        p.write_text(clean)
        c = root / "serial_onehot.high.log"
        c.write_text(c.read_text().replace("area_um2=7000", "area_um2=5800"))
        assert aggregate(root)["decision"] == "PREDICTED_PARETO_FALSIFIED"
    print("V296_DETAIL45_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 4 and sys.argv[1] == "--single":
        root, variant = Path(sys.argv[2]), sys.argv[3]
        result = audit_case(root, variant)
        (root / (variant + ".audit.json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        if not result.get("complete"):
            raise SystemExit(3)
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2]); root.mkdir(parents=True, exist_ok=True)
        result = aggregate(root)
        (root / "aggregate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        if result["decision"] != "PREDICTED_PARETO_SURVIVES_EXTRACTED_IDEAL_CLOCK":
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT | --aggregate ROOT")
