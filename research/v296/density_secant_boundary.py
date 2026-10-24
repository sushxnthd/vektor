#!/usr/bin/env python3
"""Reproduce V296 two-density *descriptive* feasibility secants from the frozen audit.

A secant through two placement targets is NOT a predictive physical law.
Do not extrapolate beyond the measured interval or call global route signoff.
"""
import json
import math
import sys
from pathlib import Path

AREA_LIMIT = 7400.0
SETUP_GUARD_NS = 0.050
DENSITIES = {"d045": 0.45, "d065": 0.65}


def finite(x):
    y = float(x)
    if not math.isfinite(y):
        raise ValueError("non-finite measurement")
    return y


def compute(audit):
    rows = audit["rows"]
    p45, p65 = (rows["pairwise." + d] for d in ("d045", "d065"))
    if not p45["complete_global_route"] or not p65["complete_global_route"]:
        raise ValueError("V296 global-route pair incomplete")
    if p45["feasible_with_50ps_ideal_guardband"] is not True:
        raise ValueError("45%-density feasibility not established")
    if p65["feasible_with_50ps_ideal_guardband"] is not False:
        raise ValueError("65%-density failure not established")
    a0, a1 = finite(p45["final"]["area_um2"]), finite(p65["final"]["area_um2"])
    t0, t1 = finite(p45["final"]["setup_ns"]), finite(p65["final"]["setup_ns"])
    if not (a0 > 0 and a1 > 0 and a0 < AREA_LIMIT < a1 and
            t0 > SETUP_GUARD_NS > t1):
        raise ValueError("boundary ordering not satisfied")
    d0, d1 = DENSITIES["d045"], DENSITIES["d065"]
    area_cross = d0 + (d1-d0)*(AREA_LIMIT-a0)/(a1-a0)
    setup_cross = d0 + (d1-d0)*(SETUP_GUARD_NS-t0)/(t1-t0)
    controls = {}
    for name in ("serial_onehot", "original"):
        row = rows[name + ".d045"]
        if not row["complete_global_route"] or row["feasible_with_50ps_ideal_guardband"] is not True:
            raise ValueError("45%-density matched control incomplete: " + name)
        a, t = finite(row["final"]["area_um2"]), finite(row["final"]["setup_ns"])
        controls[name] = {
            "v296_area_reduction_percent": 100*(a-a0)/a,
            "v296_setup_lead_ps": 1000*(t0-t),
            "global_only_pareto": bool(a0 < a and t0 > t),
        }
    return {
        "evidence_tier": "matched-floorplan ideal-clock global route; NOT signoff",
        "aggregate_gate": audit.get("status"),
        "pairwise_45_area_um2": a0,
        "pairwise_65_area_um2": a1,
        "area_increase_um2": a1-a0,
        "area_increase_percent": 100*(a1/a0-1),
        "setup_loss_ps": 1000*(t0-t1),
        "observed_45_feasible": True,
        "observed_65_feasible": False,
        "linear_area_ceiling_interpolation_density": area_cross,
        "linear_50ps_setup_interpolation_density": setup_cross,
        "linear_interpolation_validated": False,
        "discrete_cap_violations_interpolated": False,
        "matched_45_controls": controls,
        "strict_equal_consumed_area": "NOT_EVALUATED",
        "detailed_route_CTS_power": "NOT_EVALUATED",
    }


def self_test():
    def row(area, setup, cap, feasible):
        return {"complete_global_route": True,
                "feasible_with_50ps_ideal_guardband": feasible,
                "final": {"area_um2": area, "setup_ns": setup,
                          "slew": 0, "cap": cap}}
    rows = {
        "pairwise.d045": row(5987.926154915613, 0.678804, 0, True),
        "pairwise.d065": row(7911.106436608861, 0.004863, 2, False),
        "serial_onehot.d045": row(6942.599828363427, 0.190476, 0, True),
        "original.d045": row(7192.639817077406, 0.112566, 0, True),
    }
    result = compute({"status": "INCOMPLETE", "rows": rows})
    assert abs(result["linear_area_ceiling_interpolation_density"] - 0.5968477873) < 1e-9
    assert abs(result["linear_50ps_setup_interpolation_density"] - 0.6366050589) < 1e-9
    assert all(v["global_only_pareto"] for v in result["matched_45_controls"].values())
    rows["pairwise.d065"]["complete_global_route"] = False
    try:
        compute({"rows": rows})
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete candidate was accepted")
    print("V296_DENSITY_SECANT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 2:
        print(json.dumps(compute(json.loads(Path(sys.argv[1]).read_text())),
                         indent=2, sort_keys=True))
    else:
        raise SystemExit("usage: density_secant_boundary.py --self-test | AUDIT_JSON")
