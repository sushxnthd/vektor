#!/usr/bin/env python3
"""Independent prelayout STA delay-ratio audit, not routed signoff."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("build/v309_sta")
CORNERS = ("optimistic", "nominal", "stressed")
DESIGNS = ("compact_greedy", "factored_exact_max")
FROZEN_MAX_OPTIMISTIC_RATIO = 1.0973483338585934


def arrival(path):
    raw = path.read_text()
    # OpenSTA reports a data arrival time for the worst constrained path.
    # OpenSTA 2.0.17 puts the value BEFORE the label. A loose regex using
    # \\s+ after the label crosses a newline and incorrectly captures the
    # following 1.00 ns required-time clock. Never accept that false pass.
    vals = re.findall(
        r"^\s*([0-9]+(?:\.[0-9]+)?)\s+data arrival time\s*$",
        raw, re.MULTILINE)
    if len(vals) != 1:
        raise AssertionError(f"expected exactly one positive arrival path in {path}; found {vals}")
    result = float(vals[0])
    if not (result > 0):
        raise AssertionError(f"invalid nonpositive data arrival time in {path}: {result}")
    return result


def main():
    results = {}
    for corner in CORNERS:
        values = {name: arrival(ROOT / f"{name}_{corner}.log")
                  for name in DESIGNS}
        ratio = values["factored_exact_max"] / values["compact_greedy"]
        results[corner] = {
            "compact_greedy_arrival_ns": values["compact_greedy"],
            "factored_exact_max_arrival_ns": values["factored_exact_max"],
            "factored_to_compact_delay_ratio": ratio,
        }
    optimistic_ratio = results["optimistic"]["factored_to_compact_delay_ratio"]
    passed = optimistic_ratio < FROZEN_MAX_OPTIMISTIC_RATIO
    out = {
        "evidence_tier": "Nangate45_preplacement_zero_extracted_wire_RC",
        "matched_input_output_contract": True,
        "frozen_optimistic_ratio_ceiling": FROZEN_MAX_OPTIMISTIC_RATIO,
        "corners": results,
        "optimistic_timing_gate": "PASS_FOR_FURTHER_PHYSICAL" if passed else "FAIL_KILL_FACTORED_RTL",
        "electrical_violation_reports_need_separate_audit": True,
        "placed_routed_frequency_power_or_GPU_speedup_claimed": False,
    }
    (ROOT / "independent_sta_summary.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    if not passed:
        sys.exit("FROZEN_OPTIMISTIC_PRELAYOUT_TIMING_FAIL: kill factored mechanism")


if __name__ == "__main__":
    main()
