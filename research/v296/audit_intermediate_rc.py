#!/usr/bin/env python3
"""Prospective fixed-topology RC interpolation audit. Never a physical signoff gate.

The numerical forecast was frozen in FIXED_TOPOLOGY_SENSITIVITY_FALSIFICATION_20261023.md
before the intermediate-RC measurements were generated.
"""
import json
import pathlib
import sys

from audit_fixed_topology import VARIANTS, audit as fixed_audit, digest, stage

POINTS = (("125", 1.25), ("150", 1.50), ("175", 1.75))
TOLERANCE_NS = 0.040
AREA_TOLERANCE_UM2 = 0.0001


def evaluate(root):
    reference = fixed_audit(root)  # includes original failed electrical cases
    rows, predictions, errors = {}, {}, {}
    for variant in VARIANTS:
        prefix = variant + ".nominal"
        log = (root / (prefix + ".log")).read_text()
        if "V296_INTERMEDIATE_BEGIN" not in log or "V296_INTERMEDIATE_END" not in log:
            raise ValueError("Incomplete prospective sweep: " + variant)
        h = digest(root / (prefix + ".routed.def"))
        low = reference["rows"][variant]["fixed_rc10_load050"]
        high = reference["rows"][variant]["fixed_rc20_load050"]
        rows[variant], predictions[variant], errors[variant] = {}, {}, {}
        for label, rc in POINTS:
            key = "intermediate_rc" + label
            row = stage(log, key)
            if digest(root / (prefix + "." + key + ".def")) != h:
                raise ValueError("Topology changed in " + variant + "/" + key)
            if abs(row["area_um2"] - low["area_um2"]) > AREA_TOLERANCE_UM2:
                raise ValueError("Area changed in " + variant + "/" + key)
            prediction = low["slack_ns"] + (rc - 1.0) * (high["slack_ns"] - low["slack_ns"])
            rows[variant][label] = row
            predictions[variant][label] = prediction
            errors[variant][label] = row["slack_ns"] - prediction
    violations, leads = {}, {}
    for label, _ in POINTS:
        cand = rows["pairwise"][label]
        controls = [rows[x][label] for x in ("original", "optimized")]
        leads[label] = cand["slack_ns"] - max(x["slack_ns"] for x in controls)
        violations[label] = {v: rows[v][label]["cap"] + rows[v][label]["slew"] for v in VARIANTS}
    within = all(abs(e) <= TOLERANCE_NS for r in errors.values() for e in r.values())
    lead_positive = all(x > 0 for x in leads.values())
    candidate_only = [label for label, _ in POINTS
                      if violations[label]["pairwise"] > 0
                      and violations[label]["optimized"] == 0
                      and violations[label]["original"] == 0]
    monotone = all(
        rows[v]["125"]["slack_ns"] >= rows[v]["150"]["slack_ns"] >= rows[v]["175"]["slack_ns"]
        for v in VARIANTS
    )
    decision = ("BOUNDED_INTERPOLATION_SUPPORTED_NOT_PHYSICAL_PASS"
                if within and lead_positive and not candidate_only and monotone
                else "INTERPOLATION_FALSIFIED")
    return dict(decision=decision, holdouts="WORKLOAD_HOLDOUTS_SEALED",
                evidence="fixed-DEF global-route RC estimates; not extracted SPEF or signoff",
                clock_ns=3.5, tolerance_ns=TOLERANCE_NS, training_rc=[1.0, 2.0],
                prediction_rc=[rc for _, rc in POINTS], rows=rows, predictions=predictions,
                errors_ns=errors, slack_leads_ns=leads, electrical_violations=violations,
                within_tolerance=within, lead_positive=lead_positive,
                candidate_only_electrical=candidate_only, monotone_slack=monotone,
                parent_fixed_topology_gate=reference["decision"],
                disclaimer="This does not overturn the original failed electrical gate or prove throughput.")


def self_test():
    assert abs((0.764527 + .5 * (0.616108 - 0.764527)) - 0.6903175) < 1e-9
    assert abs((0.259952 + .5 * (0.094309 - 0.259952)) - 0.1771305) < 1e-9
    print("V296_INTERMEDIATE_RC_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        sys.exit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_intermediate_rc.py BUILD_DIR | --self-test")
    root = pathlib.Path(sys.argv[1])
    try:
        result = evaluate(root)
    except (OSError, ValueError, KeyError) as exc:
        result = dict(decision="INTERPOLATION_UNSUPPORTED", holdouts="WORKLOAD_HOLDOUTS_SEALED",
                      error=str(exc))
    root.mkdir(parents=True, exist_ok=True)
    (root / "intermediate_rc_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "predictions")},
                     indent=2))
    if result["decision"] != "BOUNDED_INTERPOLATION_SUPPORTED_NOT_PHYSICAL_PASS":
        sys.exit(3)
