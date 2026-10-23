#!/usr/bin/env python3
"""V296 prospective wire-switching activity boundary from immutable SPEF totals.

This is an activity-weighted *interconnect* capacitance proxy, not power,
not a per-net matched toggle trace, and not physical closure.
"""
import argparse
import json
import math

# OpenROAD extracted SPEF *D_NET sums, pF; run 39995731088/artifact 12523741140.
SPEF_PF = {
    "nominal": {"original": 7.531230, "optimized": 7.760770, "pairwise": 6.995384},
    "high": {"original": 16.040663, "optimized": 16.142257, "pairwise": 14.361370},
}
HOT_NET_PF = {"high": 0.127312}  # issue_wave0[0], 79 cell-input connections.


def positive(name, value, *, allow_zero=False):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{name} must be positive" if not allow_zero else f"{name} must be nonnegative")
    return float(value)


def activity_proxy(candidate_cap_pf, control_cap_pf, *, control_alpha,
                   candidate_background_alpha, candidate_hot_cap_pf=0,
                   candidate_hot_alpha=None):
    """Relative alpha*C wire proxy; equal V and clock, cell/internal energy excluded.

    alpha denotes effective weighted transition activity, NOT necessarily the
    simple binary probability of toggling (glitches/coupling may contribute).
    """
    cp = positive("candidate_cap_pf", candidate_cap_pf)
    cc = positive("control_cap_pf", control_cap_pf)
    hot = positive("candidate_hot_cap_pf", candidate_hot_cap_pf, allow_zero=True)
    if hot > cp:
        raise ValueError("hot net capacitance exceeds total")
    ac = positive("control_alpha", control_alpha)
    ab = positive("candidate_background_alpha", candidate_background_alpha, allow_zero=True)
    ah = ab if candidate_hot_alpha is None else positive("candidate_hot_alpha", candidate_hot_alpha, allow_zero=True)
    baseline = cc * ac
    candidate = (cp - hot) * ab + hot * ah
    return {
        "control_alpha_c_pf": baseline,
        "candidate_alpha_c_pf": candidate,
        "candidate_to_control_wire_proxy_ratio": candidate / baseline,
        "candidate_wire_proxy_saving_fraction": 1 - candidate / baseline,
        "candidate_uniform_activity_break_even_ratio": cc / cp,
        "candidate_hot_activity_break_even": (
            (baseline - (cp - hot) * ab) / hot if hot else None
        ),
        "scope": "INTERCONNECT_ALPHA_C_ONLY; NOT POWER OR SILICON",
    }


def prospective_sweep():
    cases = {}
    for rc, vals in SPEF_PF.items():
        candidate = vals["pairwise"]
        lowest_cap_control = min(vals["original"], vals["optimized"])
        hot = HOT_NET_PF.get(rc, 0.0)
        cases[rc] = {
            "spef_pf": vals,
            "uniform_vs_optimized": activity_proxy(candidate, vals["optimized"],
                control_alpha=.05, candidate_background_alpha=.05),
            "uniform_vs_lowest_cap_control": activity_proxy(candidate, lowest_cap_control,
                control_alpha=.05, candidate_background_alpha=.05),
            "candidate_20pct_higher_uniform_activity_vs_optimized": activity_proxy(
                candidate, vals["optimized"], control_alpha=.05,
                candidate_background_alpha=.06),
            "candidate_20pct_higher_uniform_activity_vs_lowest_cap_control": activity_proxy(
                candidate, lowest_cap_control, control_alpha=.05,
                candidate_background_alpha=.06),
        }
        if hot:
            cases[rc]["candidate_hot_net_activity_1_vs_control_uniform_005"] = activity_proxy(
                candidate, lowest_cap_control, control_alpha=.05,
                candidate_background_alpha=.05, candidate_hot_cap_pf=hot,
                candidate_hot_alpha=1.0)
    return {
        "source": "immutable run 39995731088, artifact 12523741140; SPEF net totals only",
        "cases": cases,
        "assumptions": ["equal voltage and clock frequency", "identical interpretation of effective activity",
                        "SPEF D_NET totals used as capacitance proxies",
                        "no cell internal/short-circuit/leakage/clock-tree power"],
        "evidence_tier": "MEASURED_SPEF_INPUTS_ANALYTICAL_ACTIVITY_SENSITIVITY",
        "physical_gate": "DETAILED_PHYSICAL_GATE_FAIL",
        "holdouts": "SEALED",
    }


def self_test():
    r = activity_proxy(8, 10, control_alpha=.05, candidate_background_alpha=.05)
    assert abs(r["candidate_wire_proxy_saving_fraction"] - .2) < 1e-12
    assert abs(r["candidate_uniform_activity_break_even_ratio"] - 1.25) < 1e-12
    s = prospective_sweep()["cases"]
    for rc in ("nominal", "high"):
        assert s[rc]["uniform_vs_lowest_cap_control"]["candidate_wire_proxy_saving_fraction"] > 0
        assert s[rc]["candidate_20pct_higher_uniform_activity_vs_lowest_cap_control"]["candidate_wire_proxy_saving_fraction"] < 0
    assert s["high"]["candidate_hot_net_activity_1_vs_control_uniform_005"]["candidate_wire_proxy_saving_fraction"] < 0
    for kwargs in (
        {"candidate_cap_pf": -1, "control_cap_pf": 10, "control_alpha": .1, "candidate_background_alpha": .1},
        {"candidate_cap_pf": 1, "control_cap_pf": 10, "control_alpha": 0, "candidate_background_alpha": .1},
        {"candidate_cap_pf": 1, "control_cap_pf": 10, "control_alpha": .1, "candidate_background_alpha": .1, "candidate_hot_cap_pf": 2},
        {"candidate_cap_pf": float("nan"), "control_cap_pf": 10, "control_alpha": .1, "candidate_background_alpha": .1},
    ):
        try:
            activity_proxy(**kwargs)
        except ValueError:
            continue
        raise AssertionError("Invalid activity proxy accepted")
    print("V296_WIRE_ACTIVITY_BOUNDARY_SELFTEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.sweep:
        print(json.dumps(prospective_sweep(), indent=2))
    else:
        parser.error("Specify --self-test or --sweep")
