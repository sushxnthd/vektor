#!/usr/bin/env python3
"""Independent V296 D4/D8 gate reconciliation and conditional repair sensitivity.

250 ps OpenROAD setup-repair target is NOT the 50 ps final acceptance gate.
Uses unchanged original extracted-RC observations. Frequency/path bounds are
conditional arithmetic, never STA signoff.
"""
import argparse
import json
import re
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 30
def D(x): return Decimal(str(x))
EXPECTED = {"D4_pairwise", "D4_serial_onehot", "D8_pairwise", "D8_serial_onehot"}
REQUIRED = ("setup_ns", "hold_ns", "area_um2", "cap", "slew")

def unique_constant(src, name):
    matches = re.findall(r"^" + re.escape(name) + r"\s*=\s*([0-9.]+)\s*$", src, re.M)
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous frozen gate: " + name)
    return D(matches[0])

def audit(doc, gate_src, flow_src):
    if doc.get("run_id") != 40557136436 or set(doc.get("observations", {})) != EXPECTED:
        raise ValueError("Unexpected source run or contestant set")
    limits = doc["frozen_limits"]
    period = D(limits["clock_period_ns"])
    area_cap = D(limits["max_area_um2"])
    guard = unique_constant(gate_src, "SETUP_GUARD_NS")
    if guard != D("0.050") or period != D("3.5") or area_cap != D("30000"):
        raise ValueError("Unexpected final gate or physical limits")
    if gate_src.count('f["setup_ns"] >= SETUP_GUARD_NS') != 1:
        raise ValueError("Final acceptance guard not enforced")
    anchor = '"repair_timing -setup -slack_margin 0.250"'
    if flow_src.count(anchor) != 1:
        raise ValueError("Missing or ambiguous setup repair target")
    repair_target = D("0.250")
    if D(limits["min_setup_ns"]) != repair_target:
        raise ValueError("Source JSON does not encode 250 ps threshold")
    rows = {}
    for name, item in sorted(doc["observations"].items()):
        if item.get("status") != "complete":
            rows[name] = {"complete": False, "feasible": False,
                          "reason": "censored_physical_run", "exit_code": item.get("exit_code")}
            continue
        final = item.get("final")
        if not isinstance(final, dict) or any(k not in final for k in REQUIRED):
            raise ValueError("Missing completed-run metric: " + name)
        vals = {k: D(final[k]) for k in REQUIRED}
        if not all(x.is_finite() for x in vals.values()):
            raise ValueError("Nonfinite metric: " + name)
        if vals["area_um2"] <= 0 or vals["cap"] < 0 or vals["slew"] < 0:
            raise ValueError("Invalid physical metric: " + name)
        deficit = max(D(0), guard - vals["setup_ns"])
        old_deficit = max(D(0), repair_target - vals["setup_ns"])
        effective_path = period - vals["setup_ns"]
        if effective_path <= 0:
            raise ValueError("Invalid effective path proxy")
        fraction = deficit / effective_path
        headroom = area_cap - vals["area_um2"]
        reasons = []
        if deficit > 0: reasons.append("setup")
        if vals["hold_ns"] < 0: reasons.append("hold")
        if headroom < 0: reasons.append("area")
        if vals["cap"] != 0: reasons.append("capacitance")
        if vals["slew"] != 0: reasons.append("slew")
        sensitivity = {}
        for f in (D("0.20"), D("0.25"), D("0.30"), D("0.50"), D("0.75")):
            # Necessary Amdahl-style path-speedup condition:
            # f * (1 - 1/s) >= deficit / effective_path.
            sensitivity[str(f)] = None if f <= fraction else str(f / (f - fraction))
        rows[name] = {
            "complete": True, "feasible": not reasons, "fail_reasons": reasons,
            "setup_recovery_to_actual_gate_ns": str(deficit),
            "setup_recovery_to_repair_target_ns": str(old_deficit),
            "prior_recovery_overstatement_ns": str(old_deficit - deficit),
            "conditional_fixed_delay_min_period_ns": str(period + deficit),
            "conditional_fixed_delay_max_mhz": str(D(1000) / (period + deficit)),
            "effective_path_delay_proxy_ns": str(effective_path),
            "minimum_fraction_of_effective_path_to_remove": str(fraction),
            "necessary_speedup_if_fraction_modifiable": sensitivity,
            "remaining_area_budget_um2": str(headroom),
            "unresolved_capacitance_violations": int(vals["cap"]),
        }
    matched = {depth: (rows[f"{depth}_pairwise"]["feasible"] and
                       rows[f"{depth}_serial_onehot"]["feasible"])
               for depth in ("D4", "D8")}
    return {"source_run": doc["run_id"], "final_acceptance_guard_ns": str(guard),
            "optimization_repair_target_ns": str(repair_target),
            "clock_period_ns": str(period), "rows": rows,
            "matched_feasible": matched, "any_matched_feasible": any(matched.values()),
            "evidence_tier": "original extracted-RC measurements; independent arithmetic correction",
            "fmax_measured": False, "gpu_throughput_measured": False,
            "holdouts_opened": False}

def self_test(doc, gate_src, flow_src):
    r = audit(doc, gate_src, flow_src)
    assert r["final_acceptance_guard_ns"] == "0.050"
    assert r["optimization_repair_target_ns"] == "0.250"
    assert not r["any_matched_feasible"]
    d8, d4 = r["rows"]["D8_pairwise"], r["rows"]["D4_serial_onehot"]
    assert D(d8["setup_recovery_to_actual_gate_ns"]) == D("0.734592")
    assert D(d4["setup_recovery_to_actual_gate_ns"]) == D("1.366510")
    assert D(d8["conditional_fixed_delay_min_period_ns"]) == D("4.234592")
    assert D(d4["conditional_fixed_delay_min_period_ns"]) == D("4.866510")
    assert D(d8["prior_recovery_overstatement_ns"]) == D("0.200")
    assert d8["fail_reasons"] == ["setup", "capacitance"]
    assert d4["fail_reasons"] == ["setup", "capacitance"]
    assert not r["rows"]["D4_pairwise"]["complete"]
    assert not r["rows"]["D8_serial_onehot"]["complete"]
    for corrupted in (gate_src.replace("0.050", "0.250"),
                      gate_src.replace('f["setup_ns"] >= SETUP_GUARD_NS', "False")):
        try: audit(doc, corrupted, flow_src)
        except ValueError: pass
        else: raise AssertionError("Modified final guard accepted")
    try: audit(doc, gate_src, flow_src.replace('"repair_timing -setup -slack_margin 0.250"', ""))
    except ValueError: pass
    else: raise AssertionError("Missing repair target accepted")
    broken = json.loads(json.dumps(doc))
    broken["observations"]["D8_pairwise"]["final"]["setup_ns"] = "NaN"
    try: audit(broken, gate_src, flow_src)
    except ValueError: pass
    else: raise AssertionError("NaN accepted")
    print("V296_GUARD_RECONCILIATION_SELFTEST_PASS")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence", type=Path)
    p.add_argument("gate_source", type=Path)
    p.add_argument("flow_source", type=Path)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    doc = json.loads(args.evidence.read_text())
    gate_src = args.gate_source.read_text()
    flow_src = args.flow_source.read_text()
    if args.self_test: self_test(doc, gate_src, flow_src)
    result = audit(doc, gate_src, flow_src)
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output: args.output.write_text(data)
    else: print(data)

if __name__ == "__main__":
    main()
