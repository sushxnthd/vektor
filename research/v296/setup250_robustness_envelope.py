#!/usr/bin/env python3
"""V296 extracted-CTS Pareto robustness envelope, not statistical PVT evidence.

This is an independent algebraic stress test of frozen setup250 measurements.
The user-supplied uncertainties are hypothetical adversarial bounds, not
measured variation. It never converts controller slack into GPU fmax.
"""
import argparse
import json
import math

MEASURED = {
    "candidate_area_um2": 6239.828209686493,
    "control_area_um2": 7284.9419829879025,
    "candidate_setup_ps": 430.410,
    "control_setup_ps": 104.791,
    "candidate_hold_ps": 284.848,
    "control_hold_ps": 249.547,
}
AREA_CEILING = 7400.0
SETUP_MIN_PS = 50.0
HOLD_MIN_PS = 0.0
SAVING_MIN = 0.10
LEAD_MIN_PS = 200.0


def finite_nonnegative(value, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(label + ": expected number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(label + ": expected nonnegative finite number")
    return float(value)


def envelope(candidate_area_up=0.0, control_area_down=0.0,
             candidate_setup_down=0.0, control_setup_up=0.0,
             candidate_hold_down=0.0, control_hold_down=0.0):
    inputs = locals().copy()
    d = {k: finite_nonnegative(v, k) for k, v in inputs.items()}
    a_v = MEASURED["candidate_area_um2"] + d["candidate_area_up"]
    a_c = MEASURED["control_area_um2"] - d["control_area_down"]
    s_v = MEASURED["candidate_setup_ps"] - d["candidate_setup_down"]
    s_c = MEASURED["control_setup_ps"] + d["control_setup_up"]
    h_v = MEASURED["candidate_hold_ps"] - d["candidate_hold_down"]
    h_c = MEASURED["control_hold_ps"] - d["control_hold_down"]
    if a_c <= 0:
        raise ValueError("adverse control area is nonphysical")
    saving = 1 - a_v / a_c
    lead = s_v - s_c
    return {
        "adverse_candidate_area_um2": a_v,
        "adverse_control_area_um2": a_c,
        "adverse_candidate_setup_ps": s_v,
        "adverse_control_setup_ps": s_c,
        "adverse_candidate_hold_ps": h_v,
        "adverse_control_hold_ps": h_c,
        "adverse_area_saving_fraction": saving,
        "adverse_setup_lead_ps": lead,
        "area_pareto_gate": saving >= SAVING_MIN,
        "timing_pareto_gate": lead >= LEAD_MIN_PS,
        "controller_feasibility_gate": (
            a_v <= AREA_CEILING and a_c <= AREA_CEILING
            and s_v >= SETUP_MIN_PS and s_c >= SETUP_MIN_PS
            and h_v >= HOLD_MIN_PS and h_c >= HOLD_MIN_PS
        ),
        "physical_closure_under_perturbation": "NOT_EVALUATED",
        "strict_equal_consumed_area": False,
        "measured_PVT_distribution": False,
        "evidence_tier": "ALGEBRAIC_SENSITIVITY_ONLY",
    }


def self_test():
    r = envelope()
    assert abs(r["adverse_area_saving_fraction"] - 0.14346219582009057) < 1e-12
    assert abs(r["adverse_setup_lead_ps"] - 325.619) < 1e-9
    assert r["area_pareto_gate"] and r["timing_pareto_gate"]
    assert r["controller_feasibility_gate"]
    mild = envelope(50, 50, 50, 50)
    assert mild["area_pareto_gate"] and mild["timing_pareto_gate"]
    severe = envelope(50, 50, 75, 75)
    assert severe["area_pareto_gate"] and not severe["timing_pareto_gate"]
    assert not envelope(candidate_area_up=320)["area_pareto_gate"]
    assert not envelope(candidate_setup_down=381)["controller_feasibility_gate"]
    assert not envelope(control_hold_down=250)["controller_feasibility_gate"]
    for bad in (-1, float("nan"), float("inf"), True):
        try:
            envelope(candidate_area_up=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid uncertainty accepted")
    print("V296_SETUP250_ROBUSTNESS_ENVELOPE_SELFTEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--area-um2", type=float, default=0.0,
                        help="Candidate grows and control shrinks by this hypothetical bound")
    parser.add_argument("--setup-ps", type=float, default=0.0,
                        help="Candidate slack falls and control slack rises by this bound")
    parser.add_argument("--hold-ps", type=float, default=0.0,
                        help="Both hold slacks fall by this bound")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(envelope(
            candidate_area_up=args.area_um2, control_area_down=args.area_um2,
            candidate_setup_down=args.setup_ps, control_setup_up=args.setup_ps,
            candidate_hold_down=args.hold_ps, control_hold_down=args.hold_ps
        ), indent=2))
