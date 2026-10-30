#!/usr/bin/env python3
"""Independent three-width cycle-response model falsification for two pinned workloads.

Input MUST be the already independently audited buswidth-transfer.json.
This tests a conditional performance law, not a physical GPU architecture.
"""
import argparse
import copy
import json
from pathlib import Path

TIER = "PASS_INDEPENDENT_TWO_WORKLOAD_SENSITIVITY_AUDIT"
EXPECTED = ("pathfinder-rodinia-2.0-ft", "lud-rodinia-2.0-ft")


def natural(v, name):
    if type(v) is not int or v <= 0:
        raise ValueError("invalid positive cycle count: " + name)
    return v


def check(report):
    if report.get("status") != TIER or report.get("all_frozen_predictions_survived") is not True:
        raise ValueError("upstream independent transfer audit not accepted")
    if any(report.get(k) is not False for k in
           ("hardware_calibrated", "physical_speedup_demonstrated", "RTX_5090_equivalence")):
        raise ValueError("hardware/equivalence overclaim")
    predictions = report.get("frozen_predictions")
    if not isinstance(predictions, dict) or set(predictions) != {
        "P1_LUD_widening_below_2pct", "P2_LUD_narrowing_not_faster",
        "P3_both_widening_below_2pct"
    } or not all(v is True for v in predictions.values()):
        raise ValueError("frozen predictions inconsistent")
    out = {}
    for key, identity in zip(("first", "second"), EXPECTED):
        name = report.get(key + "_original_workload")
        if not isinstance(name, str) or identity not in name or not name.endswith("/kernelslist.g"):
            raise ValueError("workload identity drift: " + key)
        row = report.get(key)
        if not isinstance(row, dict) or row.get("cache_counter_invariance") is not True:
            raise ValueError("invalid independently accepted row")
        t8 = natural(row.get("narrow_cycles"), key + " 8B")
        t16 = natural(row.get("baseline_cycles"), key + " 16B")
        t32 = natural(row.get("wide_cycles"), key + " 32B")
        if not (t8 >= t16 >= t32):
            raise ValueError("nonmonotone response outside frozen regime")
        f8 = (t8 - t16) / t16
        f32 = 2 * (t16 - t32) / t16
        if abs(f8 - row.get("narrowing_cycle_penalty_fraction", float("nan"))) > 1e-12:
            raise ValueError("narrowing fraction does not match raw cycles")
        if abs((t16-t32)/t16 - row.get("widening_gain_fraction", float("nan"))) > 1e-12:
            raise ValueError("widening fraction does not match raw cycles")
        # If T(w)=T_fixed + K/w for all three widths, T8-T16=2*(T16-T32).
        residual = (t8 - t16) - 2*(t16-t32)
        out[key] = {
            "workload": identity, "cycles_8B": t8, "cycles_16B": t16,
            "cycles_32B": t32, "observed_widening_gain_percent": 100*(t16-t32)/t16,
            "width_fraction_inferred_from_halving": f8,
            "width_fraction_inferred_from_doubling": f32,
            "smooth_inverse_width_residual_cycles": residual,
            "smooth_inverse_width_law_consistent_with_1cycle": abs(residual) <= 1,
            "at_least_2pct_width_limited_fraction_rejected_under_smooth_law":
                (t16-t32) < 0.01*t16,
            "plateau_from_16B_to_32B": t16 == t32
        }
    return {
        "status": "PASS_CONDITIONAL_BOUNDARY_FALSIFICATION",
        "law_tested": "T(w)=T_fixed+K/w; requires equal work and a single unsaturated width-limited service fraction",
        "law_identity": "(T8-T16)=2*(T16-T32)",
        "first": out["first"], "second": out["second"],
        "finding": "Pathfinder rejects the exact smooth inverse-width law; LUD is consistent with K=0. Both plateau at 16B-to-32B. A threshold/floor model remains possible but not identifiable.",
        "scope": "two source-pinned simulator workloads only; no physical width change, no RTL, no measured GPU cycles",
        "physical_speedup_demonstrated": False, "hardware_calibrated": False,
        "equal_resource_architecture_comparison": False, "RTX_5090_equivalence": False
    }


def selftest():
    def row(t8, t16, t32):
        return {"narrow_cycles": t8, "baseline_cycles": t16, "wide_cycles": t32,
                "narrowing_cycle_penalty_fraction": (t8-t16)/t16,
                "widening_gain_fraction": (t16-t32)/t16,
                "cache_counter_invariance": True}
    a = {"status": TIER, "all_frozen_predictions_survived": True,
         "frozen_predictions": {k: True for k in
             ("P1_LUD_widening_below_2pct", "P2_LUD_narrowing_not_faster",
              "P3_both_widening_below_2pct")},
         "hardware_calibrated": False, "physical_speedup_demonstrated": False,
         "RTX_5090_equivalence": False,
         "first_original_workload": "rodinia/pathfinder-rodinia-2.0-ft/traces/kernelslist.g",
         "second_original_workload": "rodinia/lud-rodinia-2.0-ft/traces/kernelslist.g",
         "first": row(28729, 28717, 28717), "second": row(127309, 127309, 127309)}
    o = check(a)
    assert o["first"]["smooth_inverse_width_residual_cycles"] == 12
    assert not o["first"]["smooth_inverse_width_law_consistent_with_1cycle"]
    assert o["second"]["smooth_inverse_width_law_consistent_with_1cycle"]
    # An exactly smooth, nonzero inverse-width response is accepted as consistent.
    b = copy.deepcopy(a)
    b["first"] = row(1100, 1000, 950)
    assert check(b)["first"]["smooth_inverse_width_law_consistent_with_1cycle"]
    mutations = [
        lambda x: x.update(status="PASS_FAKE"),
        lambda x: x.update(hardware_calibrated=True),
        lambda x: x.update(physical_speedup_demonstrated=True),
        lambda x: x.update(RTX_5090_equivalence=True),
        lambda x: x.update(all_frozen_predictions_survived=False),
        lambda x: x["frozen_predictions"].update(P1_LUD_widening_below_2pct=False),
        lambda x: x.update(second_original_workload=x["first_original_workload"]),
        lambda x: x["first"].update(narrow_cycles=-1),
        lambda x: x["first"].update(widening_gain_fraction=0.5),
        lambda x: x["second"].update(cache_counter_invariance=False),
        lambda x: x["second"].update(wide_cycles=127310),
    ]
    for mutation in mutations:
        bad = copy.deepcopy(a)
        mutation(bad)
        try:
            check(bad)
        except (ValueError, TypeError, KeyError):
            continue
        raise AssertionError("forged evidence was accepted")
    return {"status": "PASS", "positive_controls": 3, "negative_controls": len(mutations)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--transfer")
    p.add_argument("--out")
    a = p.parse_args()
    if a.selftest:
        result = selftest()
    else:
        if not a.transfer or not a.out:
            p.error("provide --transfer and --out")
        result = check(json.loads(Path(a.transfer).read_text()))
        Path(a.out).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
