#!/usr/bin/env python3
"""V296 pre-CTS skew/penalty feasibility envelope, not clock-tree signoff.

One *optimistic*, freely selectable common launch-to-capture skew per design is
assumed. Real CTS paths have correlated and sometimes incompatible skews.
No hidden workloads, physical design artifacts or new measurements are read.
"""
import argparse
import json
import math

# Independent fourth-round extracted high-RC reference (2026-10-24).
# Evidence: GitHub Actions run 40027903793, artifact 12534554683.
REFERENCE = {
    "original": {"setup_ns": -0.113988, "hold_ns": 0.249579, "area_um2": 7196.363949, "slew": 0},
    "optimized_onehot": {"setup_ns": -0.168119, "hold_ns": 0.270420, "area_um2": 6949.250064, "slew": 15},
    "v296_pairwise": {"setup_ns": 0.418903, "hold_ns": 0.282110, "area_um2": 5987.926155, "slew": 0},
}


def envelope(setup_ns, hold_ns, setup_penalty_ns=0.0, hold_penalty_ns=0.0, guard_ns=0.0):
    """Existential optimistic skew interval for simultaneous setup/hold margins.

    setup' = setup + skew - setup_penalty
    hold'  = hold - skew - hold_penalty
    Both must exceed guard_ns. Penalties are NON-skew losses; no double count.
    """
    values = (setup_ns, hold_ns, setup_penalty_ns, hold_penalty_ns, guard_ns)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError("all timing inputs must be finite numeric scalars")
    if min(setup_penalty_ns, hold_penalty_ns, guard_ns) < 0:
        raise ValueError("penalties and guardband must be nonnegative")
    lower = guard_ns + setup_penalty_ns - setup_ns
    upper = hold_ns - hold_penalty_ns - guard_ns
    total_budget = setup_ns + hold_ns - 2 * guard_ns
    penalty_total = setup_penalty_ns + hold_penalty_ns
    balanced_skew = (hold_ns - hold_penalty_ns - setup_ns + setup_penalty_ns) / 2
    balanced_margin = (setup_ns + hold_ns - setup_penalty_ns - hold_penalty_ns) / 2
    return {
        "skew_lower_ns": lower,
        "skew_upper_ns": upper,
        "skew_interval_width_ns": upper - lower,
        "optimistic_feasible": lower <= upper + 1e-12,
        "balanced_skew_ns": balanced_skew,
        "balanced_setup_hold_margin_ns": balanced_margin,
        "combined_non_skew_penalty_budget_ns": total_budget,
        "specified_non_skew_penalty_ns": penalty_total,
    }


def evaluate():
    cases = {
        "ideal_no_guard": {"guard_ns": 0.0},
        "frozen_guard_50ps": {"guard_ns": 0.05},
        "frozen_guard_50ps_plus_20ps_each": {"guard_ns": 0.05, "setup_penalty_ns": 0.02, "hold_penalty_ns": 0.02},
        "frozen_guard_50ps_plus_100ps_each": {"guard_ns": 0.05, "setup_penalty_ns": 0.10, "hold_penalty_ns": 0.10},
    }
    results = {}
    for name, config in cases.items():
        results[name] = {
            variant: {**envelope(row["setup_ns"], row["hold_ns"], **config),
                      "measured_slew_violations": row["slew"]}
            for variant, row in REFERENCE.items()
        }
    # Hypothetical maximum setup gain for control from skew, at 50ps hold floor.
    # Candidate held at measured skew. This is a *control-favourable* bound,
    # not an achievable CTS outcome or an area/electrical closure claim.
    control_bound = {
        name: {
            "optimistic_control_setup_ns": row["setup_ns"] + row["hold_ns"] - 0.05,
            "candidate_setup_lead_ns": REFERENCE["v296_pairwise"]["setup_ns"] - (row["setup_ns"] + row["hold_ns"] - 0.05),
        }
        for name, row in REFERENCE.items() if name != "v296_pairwise"
    }
    return {
        "evidence_tier": "ANALYTICAL_SENSITIVITY_ONLY_PRE_CTS",
        "source_run": 40027903793,
        "source_artifact": 12534554683,
        "not_evidence_of": ["CTS feasibility", "post-CTS hold closure", "equal-area comparison", "power", "GPU throughput"],
        "assumptions": "single freely adjustable effective skew per design; fixed data paths and parasitics; non-skew setup/hold penalties specified independently; no added CTS area, congestion or slew repair modeled",
        "reference": REFERENCE,
        "frozen_scenarios": results,
        "adversarial_control_50ps_hold_floor": control_bound,
        "original_six_case_gate": "FAILED",
        "holdouts": "SEALED",
    }


def self_test():
    o = envelope(-0.113988, 0.249579)
    assert abs(o["skew_lower_ns"] - 0.113988) < 1e-12
    assert abs(o["skew_upper_ns"] - 0.249579) < 1e-12
    assert abs(o["balanced_setup_hold_margin_ns"] - 0.0677955) < 1e-12
    x = evaluate()["frozen_scenarios"]
    assert all(r["optimistic_feasible"] for r in x["ideal_no_guard"].values())
    assert all(r["optimistic_feasible"] for r in x["frozen_guard_50ps"].values())
    assert x["frozen_guard_50ps_plus_20ps_each"]["v296_pairwise"]["optimistic_feasible"]
    assert not x["frozen_guard_50ps_plus_20ps_each"]["original"]["optimistic_feasible"]
    assert not x["frozen_guard_50ps_plus_20ps_each"]["optimized_onehot"]["optimistic_feasible"]
    assert x["frozen_guard_50ps_plus_100ps_each"]["v296_pairwise"]["optimistic_feasible"]
    assert abs(x["frozen_guard_50ps"]["optimized_onehot"]["combined_non_skew_penalty_budget_ns"] - 0.002301) < 1e-12
    for bad in (float("nan"), float("inf"), True):
        try:
            envelope(bad, 0.2)
        except ValueError:
            continue
        raise AssertionError("accepted invalid scalar")
    try:
        envelope(0.1, 0.1, guard_ns=-0.01)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted negative guard")
    print("V296_CTS_SKEW_ENVELOPE_SELFTEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(evaluate(), indent=2, sort_keys=True))
