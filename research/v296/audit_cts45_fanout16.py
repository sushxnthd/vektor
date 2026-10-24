#!/usr/bin/env python3
"""Independent audit for the preregistered V296 symmetric fanout-16 intervention.

Reuses the already-tested CTS physical evidence parser, then independently
resolves every extracted slew violator to its SPEF net. A control failure
never becomes a candidate Pareto victory.
"""
import json
import sys
from pathlib import Path

import audit_cts45
import cts45_slew_net_forensics

VARIANTS = ("pairwise", "serial_onehot")
POLICY = "V296_CTS45_FANOUT_POLICY 16"


def policy_marker(log):
    lines = log.splitlines()
    if lines.count(POLICY) != 1:
        raise ValueError("missing, duplicated, or changed frozen fanout-16 intervention")
    if any(x.startswith("V296_CTS45_FANOUT_POLICY ") and x != POLICY for x in lines):
        raise ValueError("ambiguous fanout policy marker")
    if lines.index(POLICY) < lines.index("V296_CTS45_CTS_END"):
        raise ValueError("fanout intervention occurred before CTS")
    if lines.index(POLICY) > lines.index("V296_CTS45_DETAIL_BEGIN"):
        raise ValueError("slew intervention occurred after detailed routing")


def case(root, variant):
    row = audit_cts45.case(root, variant)
    if not row.get("complete"):
        return row
    log = (root / (variant + ".high.log")).read_text(errors="replace")
    policy_marker(log)
    spef = (root / (variant + ".high.cts45.spef")).read_text(errors="replace")
    nets = cts45_slew_net_forensics.audit(log, spef)
    if nets["violator_count"] != row["final"]["slew"]:
        raise ValueError("extracted slew counts disagree with independent SPEF audit")
    net_data, pin_map = cts45_slew_net_forensics.parse_spef(spef)
    port_key = pin_map.get("issue_wave0[0]")
    if port_key is None or port_key not in net_data:
        raise ValueError("issue_wave0[0] output port absent from extracted SPEF")
    row["fanout16_policy_limit"] = 16
    row["issue_wave0_output_net"] = {"net_id": port_key, **net_data[port_key]}
    row["slew_net_forensics"] = nets
    return row


def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = case(root, variant)
        except (ValueError, OSError, IndexError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    p, c = (rows[v] for v in VARIANTS)
    decision = "INCOMPLETE_NO_PHYSICAL_CLAIM"
    comparison = None
    if p.get("complete") and c.get("complete"):
        pv, cv = p["final"], c["final"]
        saving = (cv["area_um2"] - pv["area_um2"]) / cv["area_um2"]
        lead = pv["setup_ns"] - cv["setup_ns"]
        comparison = {"candidate_area_saving_fraction": saving,
                      "candidate_extracted_setup_lead_ns": lead,
                      "candidate_feasible": p["feasible"],
                      "control_feasible": c["feasible"],
                      "strict_equal_consumed_area": False}
        if p.get("issue_wave0_output_net", {}).get("load_count", 999) > 16:
            decision = "FANOUT16_TOPOLOGY_PREDICTION_FAIL"
        elif not p["feasible"]:
            decision = "FANOUT16_CANDIDATE_PHYSICAL_GATE_FAIL"
        elif not c["feasible"]:
            decision = "FANOUT16_CONTROL_INFEASIBLE_NO_PARETO_CLAIM"
        elif saving + 1e-12 < 0.10 or lead + 1e-12 < 0.200:
            decision = "FANOUT16_FEASIBLE_PARETO_FALSIFIED"
        else:
            decision = "FANOUT16_FEASIBLE_PARETO_SUPPORTED"
    elif p.get("complete") and p.get("issue_wave0_output_net", {}).get("load_count", 999) > 16:
        decision = "FANOUT16_TOPOLOGY_PREDICTION_FAIL"
    elif p.get("complete") and not p["feasible"]:
        decision = "FANOUT16_CANDIDATE_PHYSICAL_GATE_FAIL"
    return {"decision": decision, "rows": rows, "comparison": comparison,
            "baseline_10_percent_margin": "HISTORICAL_ONLY_NOT_A_NEW_HOLDOUT",
            "workload_holdouts": "SEALED", "signoff": False,
            "equal_consumed_area": "NOT_EVALUATED"}


def self_test():
    sample = ("V296_CTS45_CTS_END\n" + POLICY +
              "\nV296_CTS45_DETAIL_BEGIN\n")
    policy_marker(sample)
    for changed in (
        sample.replace(" 16", " 10"),
        sample.replace(POLICY, POLICY + "\n" + POLICY),
        sample.replace("V296_CTS45_CTS_END\n", ""),
        sample.replace("V296_CTS45_DETAIL_BEGIN\n", ""),
    ):
        try:
            policy_marker(changed)
        except (ValueError, IndexError):
            pass
        else:
            raise AssertionError("policy parser failed open")
    audit_cts45.self_test()
    cts45_slew_net_forensics.self_test()
    print("V296_CTS45_FANOUT16_INDEPENDENT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 4 and sys.argv[1] == "--single":
        root, variant = Path(sys.argv[2]), sys.argv[3]
        if variant not in VARIANTS:
            raise SystemExit("invalid variant")
        try:
            outcome = case(root, variant)
        except (ValueError, OSError, IndexError) as exc:
            outcome = {"variant": variant, "complete": False, "error": str(exc)}
        (root / (variant + ".fanout16.audit.json")).write_text(json.dumps(outcome, indent=2) + "\n")
        print(json.dumps(outcome, indent=2))
        if not outcome.get("complete"):
            raise SystemExit(3)
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2])
        outcome = aggregate(root)
        (root / "aggregate.fanout16.json").write_text(json.dumps(outcome, indent=2) + "\n")
        print(json.dumps(outcome, indent=2))
        if outcome["decision"] != "FANOUT16_FEASIBLE_PARETO_SUPPORTED":
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT | --aggregate ROOT")
