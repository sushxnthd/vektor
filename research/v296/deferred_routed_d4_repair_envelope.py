#!/usr/bin/env python3
"""Independent necessary physical feasibility envelope for V296 routed D4.

Source: original Actions #40646515864 D4 job stdout. No hidden workload
access, no inferred D8 results, no power/signoff/throughput claims.
"""
import argparse
import json
from decimal import Decimal as D

SOURCE = {
    "workflow_run": 40646515864,
    "commit": "84245c21f485c191aea7d352652c0ef036d6d047",
    "depth": 4,
    "candidate": {"job": 122676592244, "artifact": 12800301495,
                  "area": "19543.01964701699", "setup": "0.066661", "hold": "0.010758",
                  "cap": 0, "slew": 0, "complete": True},
    "serial": {"job": 122676592295, "artifact": 12800782354,
               "area": "21914.94274939032", "setup": "-0.323617", "hold": "-0.011207",
               "cap": 0, "slew": 0, "complete": True},
}
GUARD = D("0.050")
AREA_LIMIT = D("30000")
CLOCK = D("3.5")


def classify(row):
    if row.get("complete") is not True or row.get("cap") != 0 or row.get("slew") != 0:
        return "INCOMPLETE_OR_ELECTRICAL_FAIL"
    try:
        area, setup, hold = (D(row[k]) for k in ("area", "setup", "hold"))
    except (KeyError, ValueError, TypeError, ArithmeticError):
        return "INVALID_EVIDENCE"
    if not all(x.is_finite() for x in (area, setup, hold)) or area <= 0:
        return "INVALID_EVIDENCE"
    if area > AREA_LIMIT or setup < GUARD or hold < 0:
        return "PHYSICAL_GATE_FAIL"
    return "NECESSARY_METRIC_PASS_NOT_SIGNOFF"


def evaluate(source):
    c, s = source["candidate"], source["serial"]
    if source.get("depth") != 4:
        raise ValueError("Only D4 original results pinned; D8 censored")
    if any(classify(r) in ("INVALID_EVIDENCE", "INCOMPLETE_OR_ELECTRICAL_FAIL") for r in (c, s)):
        return {"verdict": "INCOMPLETE_OR_INVALID_NO_COMPARISON"}
    ca, sa = D(c["area"]), D(s["area"])
    cs, ss = D(c["setup"]), D(s["setup"])
    ch, sh = D(c["hold"]), D(s["hold"])
    cpass, spass = classify(c), classify(s)
    if cpass == "NECESSARY_METRIC_PASS_NOT_SIGNOFF" and spass == "NECESSARY_METRIC_PASS_NOT_SIGNOFF":
        decision = "BOTH_PASS_COMPARE_PARETO"
    elif cpass == "NECESSARY_METRIC_PASS_NOT_SIGNOFF":
        decision = "CONTROL_FAILS_NO_MATCHED_PARETO"
    else:
        decision = "CANDIDATE_FAILS_NO_MATCHED_PARETO"
    return {
        "verdict": decision,
        "candidate_metric_status": cpass, "serial_metric_status": spass,
        "candidate_setup_guard_headroom_ps": str((cs - GUARD) * 1000),
        "serial_setup_repair_needed_ps": str(max(D(0), GUARD - ss) * 1000),
        "serial_hold_repair_needed_ps": str(max(D(0), -sh) * 1000),
        "candidate_hold_headroom_ps": str(ch * 1000),
        "area_saving_um2": str(sa - ca),
        "area_saving_percent": str((sa - ca) / sa * 100),
        "candidate_setup_lead_ps": str((cs - ss) * 1000),
        "candidate_2_slice_threshold_um2": str(2 * ca),
        "serial_2_slice_threshold_um2": str(2 * sa),
        "30k_capacity_candidate_serial": [int(AREA_LIMIT // ca), int(AREA_LIMIT // sa)],
        "serial_clock_period_for_setup_guard_only_ns": str(CLOCK + max(D(0), GUARD - ss)),
        "serial_clock_relaxation_does_not_fix_hold": sh < 0,
        "d8": "CENSORED_PENDING_ORIGINAL_JOB_RESULTS",
        "d4_frozen_win_prediction": "FALSIFIED" if decision != "BOTH_PASS_COMPARE_PARETO" else "NOT_FALSIFIED_BY_GATE",
        "equal_consumed_area": False, "gpu_speedup": False, "production_signoff": False,
        "source_run": source["workflow_run"], "source_commit": source["commit"],
        "source_jobs": [c["job"], s["job"]],
    }


def selftest():
    r = evaluate(SOURCE)
    assert r["verdict"] == "CONTROL_FAILS_NO_MATCHED_PARETO"
    assert D(r["candidate_setup_guard_headroom_ps"]) == D("16.661")
    assert D(r["serial_setup_repair_needed_ps"]) == D("373.617")
    assert D(r["serial_hold_repair_needed_ps"]) == D("11.207")
    assert r["30k_capacity_candidate_serial"] == [1, 1]
    assert r["d4_frozen_win_prediction"] == "FALSIFIED"
    assert classify(dict(SOURCE["serial"], setup="0.051", hold="0.000")) == "NECESSARY_METRIC_PASS_NOT_SIGNOFF"
    assert classify(dict(SOURCE["candidate"], setup="0.049")) == "PHYSICAL_GATE_FAIL"
    assert classify(dict(SOURCE["candidate"], area="NaN")) == "INVALID_EVIDENCE"
    assert classify(dict(SOURCE["candidate"], complete=False)) == "INCOMPLETE_OR_ELECTRICAL_FAIL"
    assert classify(dict(SOURCE["candidate"], cap=1)) == "INCOMPLETE_OR_ELECTRICAL_FAIL"
    try:
        evaluate(dict(SOURCE, depth=8))
    except ValueError:
        pass
    else:
        raise AssertionError("Unobserved D8 result silently accepted")
    print("V296_D4_ROUTED_ENVELOPE_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if a.self_test:
        selftest()
    if a.json:
        print(json.dumps(evaluate(SOURCE), indent=2, sort_keys=True))
    if not (a.self_test or a.json):
        p.error("Specify --self-test or --json")
