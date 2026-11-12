"""Exact adversarial audit of the V317 matched physical/workload gate.

This is a falsification of evidence sufficiency, NOT a routed GPU measurement.
The current gate compares completed *counts*, not independently established
work units, and accepts an unverified Boolean as extracted-RC evidence.
It also allows fractional violation counts. This checker keeps those
limitations visible rather than silently treating a WIN as signoff.
"""
from decimal import Decimal
import importlib.util
from pathlib import Path

GATE = Path(__file__).with_name("v317_matched_physical_workload_gate_20261112.py")
spec = importlib.util.spec_from_file_location("v317_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def record(rtl, cycles):
    return dict(experiment_id="frozen", library_sha="lib", constraints_sha="sdc",
                corner="ss", routing_mode="detailed", workload_sha="w",
                post_route_extracted_rc=True, setup_wns_ns="0", hold_wns_ns="0",
                max_cap_violations=0, max_slew_violations=0, drc_violations=0,
                area_um2=100, period_ns=1, workload_completed=1000,
                workload_cycles=cycles, rtl_sha=rtl)

def audit():
    baseline, candidate = record("baseline", 1000), record("candidate", 900)
    pair = dict(candidate=candidate, baseline=baseline)
    assert gate.evaluate(pair)["decision"] == "WIN"
    # Counts do not prove that a completed unit is identical in work/quality.
    # Example: candidate completes 1000 trivial units, baseline 1000 full units.
    # That counterfactual is consistent with the accepted input schema.
    assert "work_unit_sha" not in candidate and "work_unit_sha" not in baseline
    # A caller's True flag cannot certify an actual SPEF/RC extraction.
    assert candidate["post_route_extracted_rc"] is True
    # No evidence of extracted paths or timing reports is required by the gate.
    assert not any(k in candidate for k in ("spef_sha","timing_report_sha","drc_report_sha"))
    # A fractional count is physically meaningless, yet positive nonzero
    # fractional values are rejected only because they are nonzero.
    # Negative zero in Decimal is also treated as zero; signed zero is benign.
    candidate["max_cap_violations"] = "-0"
    assert gate.evaluate(pair)["decision"] == "WIN"
    candidate["max_cap_violations"] = 0
    # Exact area-clock-work boundary for equal completed work:
    # candidate WIN iff Cc*Pc*Ac < Cb*Pb*Ab.
    for cycles in (800, 900, 1000, 1100, 1200):
        candidate["workload_cycles"] = cycles
        for area in (80, 100, 120):
            candidate["area_um2"] = area
            expected = "WIN" if Decimal(cycles)*area < 100000 else "NO_WIN"
            assert gate.evaluate(pair)["decision"] == expected
    print("PASS: 15 exact boundary checks; evidence-sufficiency counterexamples retained")
    print("RESEARCH VERDICT: current gate is necessary arithmetic, not sufficient physical signoff")

if __name__ == "__main__":
    audit()
