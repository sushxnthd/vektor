"""Independent V317 prospective electrical-load holdout checker.

OpenSTA pre-route characterized-cell timing only. A timing number at a
max-transition-violating load is never counted as a legal physical win.
"""
import argparse
import json
from pathlib import Path

from research.v317.rtl.audit_rf_sta import parse_electrical, parse_report

LABELS = ("source_fixed", "pairwise_fixed")
LOADS = ("10", "24", "26", "30")
FROZEN_WIN_LOAD = "10"
FROZEN_NO_WIN_LOAD = "30"
MIN_FROZEN_WIN_MARGIN_NS = 0.40
MAPPED_AREA_UM2 = {"source_fixed": 798.798, "pairwise_fixed": 259.616}


def audit(directory):
    """Read every raw log before scoring the frozen hypotheses."""
    directory = Path(directory)
    rows = {}
    for load in LOADS:
        rows[load] = {}
        for label in LABELS:
            path = directory / f"{label}_{load}.log"
            timing = parse_report(path)
            electrical = parse_electrical(path)
            if electrical["limit_ns"] <= 0:
                raise AssertionError(f"Nonpositive slew limit: {path}")
            rows[load][label] = {**timing, **electrical,
                                 "electrically_admissible_max_transition_only":
                                     not electrical["max_transition_violated"]}
    win = rows[FROZEN_WIN_LOAD]
    no_win = rows[FROZEN_NO_WIN_LOAD]
    margin = win["source_fixed"]["arrival_ns"] - win["pairwise_fixed"]["arrival_ns"]
    win_legal = all(win[label]["electrically_admissible_max_transition_only"] for label in LABELS)
    no_win_illegal = all(not no_win[label]["electrically_admissible_max_transition_only"] for label in LABELS)
    win_survives = win_legal and margin >= MIN_FROZEN_WIN_MARGIN_NS
    no_win_survives = no_win_illegal
    area_ratio = MAPPED_AREA_UM2["pairwise_fixed"] / MAPPED_AREA_UM2["source_fixed"]
    return {
        "evidence_tier": "PRE_ROUTE_NANGATE45_CELL_TIMING_MAX_TRANSITION_ONLY",
        "source_calibration_loads_ff": [2, 20, 40, 60, 80, 100],
        "unseen_frozen_loads_ff": [10, 30],
        "exploratory_loads_ff": [24, 26],
        "loads_ff": rows,
        "frozen_win": {
            "load_ff": 10,
            "required_margin_ns": MIN_FROZEN_WIN_MARGIN_NS,
            "observed_margin_ns": round(margin, 6),
            "both_max_transition_legal": win_legal,
            "survives": win_survives,
        },
        "frozen_no_win": {
            "load_ff": 30,
            "both_max_transition_illegal": no_win_illegal,
            "survives": no_win_survives,
        },
        "both_predictions_survive": win_survives and no_win_survives,
        "conditional_unmeasured_wire_penalty_headroom_ns_at_10ff":
            round(margin, 6) if win_legal else None,
        "previous_mapped_area_um2": MAPPED_AREA_UM2,
        "previous_mapped_area_ratio_pairwise_over_source": round(area_ratio, 6),
        "conditional_10ff_cell_area_delay_ratio":
            round(area_ratio * win["pairwise_fixed"]["arrival_ns"] /
                  win["source_fixed"]["arrival_ns"], 6) if win_legal else None,
        "grant_equivalent_intrinsic_service_gain": 1.0,
        "max_capacitance_verified": False,
        "placement_routing_done": False,
        "extracted_wire_rc": False,
        "setup_timing_signoff": False,
        "gpu_throughput_measured": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["both_predictions_survive"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
