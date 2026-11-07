#!/usr/bin/env python3
"""Independent falsification: a reported period is not a clock certificate.

Run: python3 research/v317/rtl/audit_period_provenance.py
Synthetic data only. This demonstrates a logical limitation, not an actual
timing failure of any Vektor RTL.
"""
from matched_physical_gate import assess, MATCHED, PROVENANCE

def packet():
    d = dict(area_um2=100, period_ns=3.0, useful_service_per_cycle=2,
             useful_fraction=1, dynamic_power_mw=10, leakage_power_mw=1,
             setup_wns_ns=0.1, hold_wns_ns=0.1,
             setup_violations=0, hold_violations=0,
             max_cap_violations=0, max_transition_violations=0,
             **{k: "a" * 64 for k in PROVENANCE},
             **{k: "same" for k in MATCHED})
    return dict(candidate=dict(d), baseline=dict(d))

def main():
    p = packet()
    # Both inputs have the SAME timing report, SAME netlist, SAME constraints,
    # SAME parasitics, and SAME STA slack. Only a claimed period is edited.
    p["candidate"]["period_ns"] = 2.0
    r = assess(p)
    assert r["passes"] is True
    assert abs(r["throughput_gain"] - 0.5) < 1e-12
    for k in ("netlist_sha256", "constraints_sha256", "parasitics_sha256",
              "sta_report_sha256"):
        assert p["candidate"][k] == p["baseline"][k]
    print("FALSIFICATION PASS: supplied-measurement gate accepts a 50%")
    print("claimed throughput gain with identical physical artifact digests.")
    print("This is NOT evidence of a real hardware gain.")
    # Remedy: derive period from authenticated STA clock constraints and
    # verified endpoint/path slack, or reject unmatched effective periods
    # until independent timing-report parsing supports their comparison.

if __name__ == "__main__":
    main()
