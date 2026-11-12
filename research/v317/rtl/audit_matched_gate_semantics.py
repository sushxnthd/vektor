#!/usr/bin/env python3
"""Adversarial audit of V317's matched_physical_gate.py (no physical signoff claim).

Run from repo root:
 python3 research/v317/rtl/audit_matched_gate_semantics.py

The legacy gate lacks setup slack, provenance and power-measurement fields.
This audit demonstrates a *false positive* if an electrically failing result
is represented with zero hold/max-cap violations. It does not fabricate a
measurement or modify historical artifacts.
"""
import importlib.util
from pathlib import Path

p = Path(__file__).with_name("matched_physical_gate.py")
spec = importlib.util.spec_from_file_location("legacy_gate", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def record(period):
    return dict(area_um2=100, period_ns=period,
                useful_service_per_cycle=2, useful_fraction=1,
                dynamic_power_mw=10, hold_violations=0,
                max_cap_violations=0)

def audit():
    baseline = record(3.0)
    candidate = record(2.9)
    legacy = mod.assess(dict(candidate=candidate, baseline=baseline))
    assert legacy["passes"] is True, legacy

    # Negative setup slack is a disqualifying electrical failure; the old
    # schema silently discards it. These are *synthetic counterexamples*.
    candidate["setup_wns_ns"] = -0.02
    baseline["setup_wns_ns"] = 0.0
    assert mod.assess(dict(candidate=candidate, baseline=baseline))["passes"]

    # Missing extracted-RC, measurement provenance and power characterization
    # also cannot be certified by the legacy interface.
    assert "setup_wns_ns" not in mod.assess(dict(candidate=candidate, baseline=baseline))
    print("FAIL-CLOSED AUDIT: legacy PASS despite negative setup WNS; "
          "do not treat legacy passes=True as physical signoff")

if __name__ == "__main__":
    audit()
