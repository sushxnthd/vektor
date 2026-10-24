#!/usr/bin/env python3
"""Fail-closed independent audit for V296 symmetric 250ps post-CTS setup-margin control rescue.

Physical evidence parsing is reused from the frozen fanout16 audit. This checker
adds a separate intervention-provenance gate and never awards a Pareto victory
unless both independently routed implementations are feasible.
"""
import json
import sys
from pathlib import Path
import audit_cts45_fanout16 as base

VARIANTS = ("pairwise", "serial_onehot")
MARGIN_MARKER = "V296_CTS45_SETUP_MARGIN 0.250"


def require_margin_policy(log: str) -> None:
    lines = log.splitlines()
    if lines.count(MARGIN_MARKER) != 1:
        raise ValueError("missing, duplicate, or changed setup-margin policy marker")
    if any(s.startswith("V296_CTS45_SETUP_MARGIN ") and s != MARGIN_MARKER for s in lines):
        raise ValueError("ambiguous setup-margin policy")
    for marker in ("V296_CTS45_CTS_END", base.POLICY, "V296_CTS45_DETAIL_BEGIN"):
        if lines.count(marker) != 1:
            raise ValueError("missing or duplicate required physical-stage marker: " + marker)
    if not (lines.index("V296_CTS45_CTS_END") <
            lines.index(base.POLICY) <
            lines.index(MARGIN_MARKER) <
            lines.index("V296_CTS45_DETAIL_BEGIN")):
        raise ValueError("setup-margin intervention outside frozen post-CTS window")


def case(root: Path, variant: str):
    row = base.case(root, variant)
    if not row.get("complete"):
        return row
    require_margin_policy((root / (variant + ".high.log")).read_text(errors="replace"))
    row["setup_margin_ns"] = 0.250
    return row


def aggregate(root: Path):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = case(root, variant)
        except (ValueError, OSError, IndexError, KeyError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    p, c = (rows[v] for v in VARIANTS)
    decision = "INCOMPLETE_NO_PHYSICAL_CLAIM"
    comparison = None
    if p.get("complete") and c.get("complete"):
        pv, cv = p["final"], c["final"]
        saving = (cv["area_um2"] - pv["area_um2"]) / cv["area_um2"]
        lead = pv["setup_ns"] - cv["setup_ns"]
        comparison = {
            "candidate_area_saving_fraction": saving,
            "candidate_extracted_setup_lead_ns": lead,
            "candidate_feasible": p["feasible"],
            "control_feasible": c["feasible"],
            "strict_equal_consumed_area": False,
        }
        if not p["feasible"]:
            decision = "CANDIDATE_GATE_FAIL"
        elif not c["feasible"]:
            decision = "CONTROL_RESCUE_FAIL_NO_PARETO_CLAIM"
        elif saving + 1e-12 < 0.10 or lead + 1e-12 < 0.200:
            decision = "FEASIBLE_PARETO_FALSIFIED"
        else:
            decision = "FEASIBLE_PARETO_SUPPORTED"
    return {
        "decision": decision, "rows": rows, "comparison": comparison,
        "setup_margin_ns": 0.250, "fanout_limit": 16,
        "workload_holdouts": "SEALED",
        "signoff": False, "equal_consumed_area": "NOT_EVALUATED",
    }


def self_test():
    base.self_test()
    sample = ("V296_CTS45_CTS_END\n" + base.POLICY + "\n" +
              MARGIN_MARKER + "\nV296_CTS45_DETAIL_BEGIN\n")
    require_margin_policy(sample)
    bad = (
        sample.replace(MARGIN_MARKER, "V296_CTS45_SETUP_MARGIN 0.100"),
        sample.replace(MARGIN_MARKER, MARGIN_MARKER + "\n" + MARGIN_MARKER),
        sample.replace("V296_CTS45_CTS_END\n", ""),
        sample.replace(base.POLICY + "\n", ""),
        sample.replace("V296_CTS45_DETAIL_BEGIN\n", ""),
        sample.replace(base.POLICY + "\n" + MARGIN_MARKER,
                       MARGIN_MARKER + "\n" + base.POLICY),
    )
    for text in bad:
        try:
            require_margin_policy(text)
        except ValueError:
            pass
        else:
            raise AssertionError("setup-margin provenance gate failed open")
    print("V296_CTS45_SETUP250_INDEPENDENT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 4 and sys.argv[1] == "--single":
        root, variant = Path(sys.argv[2]), sys.argv[3]
        if variant not in VARIANTS:
            raise SystemExit("invalid variant")
        try:
            row = case(root, variant)
        except (ValueError, OSError, IndexError, KeyError) as exc:
            row = {"variant": variant, "complete": False, "error": str(exc)}
        (root / (variant + ".setup250.audit.json")).write_text(
            json.dumps(row, indent=2) + "\n")
        print(json.dumps(row, indent=2))
        if not row.get("complete"):
            raise SystemExit(3)
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2])
        result = aggregate(root)
        (root / "aggregate.setup250.json").write_text(
            json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if result["decision"] != "FEASIBLE_PARETO_SUPPORTED":
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT | --aggregate ROOT")
