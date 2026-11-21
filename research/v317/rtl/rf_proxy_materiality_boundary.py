#!/usr/bin/env python3
"""Independent algebraic materiality and common-area dilution audit for V317.

This does NOT re-read the raw OpenROAD archive: observations are transcribed
from the frozen extracted-RC workflow audit. Raw-provenance validation is
performed separately by audit_rf_proxy_density_repair.py. No silicon claim.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

def evaluate(row: dict, threshold_pct: float) -> dict:
    s, p = row["source"], row["pairwise"]
    for x in (s, p):
        for k in ("area_um2", "hold_slack_ps", "wire_um", "power_proxy_mw"):
            if not math.isfinite(float(x[k])):
                raise ValueError(f"nonfinite {k}")
        if x["area_um2"] <= 0 or x["wire_um"] <= 0:
            raise ValueError("nonpositive physical measurement")
    delta = s["area_um2"] - p["area_um2"]
    fraction = threshold_pct / 100.0
    required = fraction * s["area_um2"]
    electrical_clean = all(
        x["hold_slack_ps"] >= 0 and
        x["hold_violations"] == 0 and
        x["max_cap_violations"] == 0 for x in (s, p)
    )
    # Equal common tile hardware H>=0 can only dilute an observed saving:
    # (A_s-A_p)/(A_s+H). A negative H_max proves no legal H>=0 can reach target.
    h_max = delta / fraction - s["area_um2"]
    return {
        "density": row["density"],
        "historical": row["historical"],
        "both_electrically_clean": electrical_clean,
        "raw_area_saving_pct": 100.0 * delta / s["area_um2"],
        "raw_area_pass": delta >= required,
        "legal_material_win": electrical_clean and delta >= required,
        "materiality_shortfall_um2": max(0.0, required - delta),
        "extra_pairwise_area_reduction_needed_pct":
            100.0 * max(0.0, required - delta) / p["area_um2"],
        "max_added_common_hardware_um2_for_materiality": h_max,
        "pairwise_wire_change_pct":
            100.0 * (p["wire_um"] / s["wire_um"] - 1.0),
        "pairwise_power_proxy_saving_pct":
            100.0 * (1.0 - p["power_proxy_mw"] / s["power_proxy_mw"]),
    }

def self_test() -> None:
    a = {"area_um2": 100.0, "hold_slack_ps": 1.0,
         "hold_violations": 0, "max_cap_violations": 0,
         "wire_um": 10.0, "power_proxy_mw": 1.0}
    b = dict(a, area_um2=97.0)
    r = evaluate({"density": 0, "historical": False,
                  "source": a, "pairwise": b}, 2.0)
    assert r["legal_material_win"] and math.isclose(
        r["max_added_common_hardware_um2_for_materiality"], 50.0)
    b2 = dict(b, max_cap_violations=1)
    r2 = evaluate({"density": 0, "historical": False,
                   "source": a, "pairwise": b2}, 2.0)
    assert r2["raw_area_pass"] and not r2["legal_material_win"]
    b3 = dict(a, area_um2=99.0)
    r3 = evaluate({"density": 0, "historical": False,
                   "source": a, "pairwise": b3}, 2.0)
    assert not r3["raw_area_pass"] and r3[
        "max_added_common_hardware_um2_for_materiality"] < 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--observations", type=Path,
        default=Path(__file__).resolve().parents[1] /
        "RF_PROXY_DENSITY_OBSERVATIONS_20261102.json")
    args = ap.parse_args()
    self_test()
    data = json.loads(args.observations.read_text(encoding="utf-8"))
    assert data["threshold_pct"] == 2.0
    assert [r["density"] for r in data["rows"]] == [0.05, 0.15, 0.35]
    out = [evaluate(row, data["threshold_pct"]) for row in data["rows"]]
    assert all(not r["raw_area_pass"] and not r["legal_material_win"]
               for r in out), "Frozen no-material-win prediction falsified"
    assert all(r["max_added_common_hardware_um2_for_materiality"] < 0
               for r in out), "Common-area monotonic bound falsified"
    print(json.dumps({"source_sha": data["provenance"]["source_sha"],
        "evidence_tier": "flop RF proxy; NOT SRAM/GPU",
        "prospective_density_electrical_gate": "FAIL",
        "prospective_legal_materiality_gate": "INDETERMINATE_ELECTRICAL",
        "raw_area_below_frozen_2pct": True,
        "rows": out}, indent=2, sort_keys=True))
