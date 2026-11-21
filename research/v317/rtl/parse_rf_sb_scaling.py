"""Prospective nine-point V317 bank-credit scaling audit.

Source-equivalent generic RTL cost only; NOT mapped area, timing, power, or GPU IPC.
"""
import json
from pathlib import Path
import sys

from research.v317.rtl.parse_rf_exact_cost import summarize
from research.v317.rtl.parse_rf_rotating_cost import depth

SLOTS = (2, 4, 8)
BANKS = (4, 16, 64)


def analyze(root):
    root = Path(root)
    records = []
    for slots in SLOTS:
        for banks in BANKS:
            prefix = f"S{slots}_B{banks}"
            baseline = summarize(root / f"{prefix}_bankmask.json", "v317_bankmask_param")
            candidate = summarize(root / f"{prefix}_pairwise.json", "v317_pairwise_param")
            baseline["generic_logic_levels"] = depth(root / f"{prefix}_bankmask.log")
            candidate["generic_logic_levels"] = depth(root / f"{prefix}_pairwise.log")
            records.append({
                "slots": slots,
                "banks": banks,
                "bankmask": baseline,
                "pairwise": candidate,
                "pairwise_to_bankmask_cell_ratio": (
                    candidate["generic_cells"] / baseline["generic_cells"]
                ),
                "pairwise_to_bankmask_depth_ratio": (
                    candidate["generic_logic_levels"] /
                    max(1, baseline["generic_logic_levels"])
                ),
                "pairwise_fewer_cells": (
                    candidate["generic_cells"] < baseline["generic_cells"]
                ),
            })
    ratios = {(r["slots"], r["banks"]): r["pairwise_to_bankmask_cell_ratio"]
              for r in records}
    return {
        "evidence_tier": "NINE_POINT_GENERIC_YOSYS_NOT_MAPPED_OR_ROUTED",
        "records": records,
        "prediction_p2_S4_B16_fewer_cells": ratios[4, 16] < 1,
        "prediction_p2_S4_ratio_nonincreasing_B": (
            ratios[4, 4] >= ratios[4, 16] >= ratios[4, 64]
        ),
        "prediction_p3_S8_B4_pairwise_loses": ratios[8, 4] >= 1,
        "same_policy_incremental_service_gain": 0,
        "mapped_timing": False,
        "electrical_signoff": False,
        "gpu_ipc_measured": False,
    }


if __name__ == "__main__":
    print(json.dumps(analyze(sys.argv[1]), indent=2, sort_keys=True))
