"""Prospective V317 seven-point unseen synthesis law test.

Do not alter predictions after observing results. Prediction misses are data,
not CI failures; equivalence failures remain fatal in the RTL testbench.
"""
import json
from pathlib import Path
import sys

from research.v317.rtl.parse_rf_exact_cost import summarize
from research.v317.rtl.parse_rf_rotating_cost import depth

FROZEN = (
    (2, 8, 34, 0.0),
    (4, 32, 320, 0.0),
    (8, 8, 1000, 0.0),
    (3, 8, 105, 0.10),
    (5, 32, 531, 0.10),
    (6, 32, 794, 0.10),
    (7, 8, 749, 0.10),
)


def audit(directory):
    root = Path(directory)
    records = []
    for slots, banks, prediction, tolerance in FROZEN:
        prefix = f"S{slots}_B{banks}"
        base = summarize(root / f"{prefix}_bankmask.json", "v317_bankmask_param")
        candidate = summarize(root / f"{prefix}_pairwise.json", "v317_pairwise_param")
        base["generic_logic_levels"] = depth(root / f"{prefix}_bankmask.log")
        candidate["generic_logic_levels"] = depth(root / f"{prefix}_pairwise.log")
        observed = candidate["generic_cells"]
        error = abs(observed - prediction) / prediction
        records.append({
            "slots": slots, "banks": banks,
            "frozen_predicted_pairwise_cells": prediction,
            "observed_pairwise_cells": observed,
            "relative_absolute_error": error,
            "frozen_tolerance": tolerance,
            "prediction_survives": error <= tolerance,
            "bankmask": base, "pairwise": candidate,
            "pairwise_to_bankmask_cells": observed / base["generic_cells"],
        })
    return {
        "tier": "PROSPECTIVE_UNSEEN_GENERIC_YOSYS_NOT_MAPPED_OR_ROUTED",
        "records": records,
        "all_frozen_predictions_survive": all(x["prediction_survives"] for x in records),
        "physical_signoff": False,
        "gpu_ipc_measured": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(sys.argv[1]), indent=2, sort_keys=True))
