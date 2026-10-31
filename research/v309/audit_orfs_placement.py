#!/usr/bin/env python3
"""Independent matched placement-RC prefilter, not routed/extracted signoff."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("build/v309_orfs")
DESIGNS = ("compact_greedy", "factored_exact_max")
VARIANTS = ("dense", "relaxed")
ARRIVAL = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s+data arrival time\s*$", re.M)
HOT2_PREDICTED_ISSUE_RATIO = 1.0973483338585934


def parse(raw):
    if raw.count("V309_PLACEMENT_ESTIMATED_RC_BEGIN") != 1 or raw.count("V309_PLACEMENT_ESTIMATED_RC_END") != 1:
        raise AssertionError("missing unique OpenROAD placement-estimated-RC markers")
    if raw.count("V309_PLACEMENT_ELECTRICAL_BEGIN") != 1 or raw.count("V309_PLACEMENT_ELECTRICAL_END") != 1:
        raise AssertionError("missing electrical report markers")
    if re.search(r"^(?:Error:|ERROR|\[ERROR)", raw, re.M):
        raise AssertionError("OpenROAD error")
    section = raw.split("V309_PLACEMENT_ELECTRICAL_BEGIN")[0]
    values = ARRIVAL.findall(section)
    if len(values) != 1:
        raise AssertionError(f"expected exactly one max arrival path; got {values}")
    delay = float(values[0])
    if not 0 < delay < 100:
        raise AssertionError("invalid delay")
    return delay


def selftest():
    raw = ("V309_PLACEMENT_ESTIMATED_RC_BEGIN\n"
           "  0.46 data arrival time\n"
           "  1.00 data required time\n"
           "V309_PLACEMENT_ELECTRICAL_BEGIN\n"
           "No violations\nV309_PLACEMENT_ELECTRICAL_END\n"
           "V309_PLACEMENT_ESTIMATED_RC_END\n")
    assert parse(raw) == 0.46
    for fake in (raw.replace("0.46 data arrival time", "1.00 data required time"),
                 raw.replace("V309_PLACEMENT_ESTIMATED_RC_BEGIN", "V309_PRELAYOUT_ONLY"),
                 raw.replace("No violations", "Error: unknown command")):
        try:
            parse(fake)
        except AssertionError:
            pass
        else:
            raise AssertionError("adversarial false evidence accepted")


def main():
    selftest()
    rows = {}
    for variant in VARIANTS:
        delays = {}
        for design in DESIGNS:
            path = ROOT / f"{design}_{variant}.sta.log"
            if not path.is_file():
                raise AssertionError(f"missing actual OpenROAD evidence {path}")
            delays[design] = parse(path.read_text())
        ratio = delays["factored_exact_max"] / delays["compact_greedy"]
        rows[variant] = dict(delays, candidate_to_baseline_delay_ratio=ratio,
                             hot2_ideal_issue_times_frequency_upper_bound=HOT2_PREDICTED_ISSUE_RATIO / ratio)
    hot2_upper_bound = min(r["hot2_ideal_issue_times_frequency_upper_bound"] for r in rows.values())
    result = {
        "evidence_tier": "ORFS_Nangate45_placement_estimated_RC_NOT_routed_extracted",
        "frozen_hot2_issue_gain": HOT2_PREDICTED_ISSUE_RATIO,
        "corners": rows,
        "worst_corner_ideal_hot2_throughput_upper_bound": hot2_upper_bound,
        "optimistic_physical_timing_prefilter": "KILL_IF_CLOCK_LIMITED" if hot2_upper_bound <= 1 else "SURVIVES_ONLY_AS_UPPER_BOUND",
        "max_cap_slew_electrical_signoff": "UNVERIFIED_REPORT_REQUIRES_INDEPENDENT_VIOLATION_AUDIT",
        "routed_extracted_signoff_or_real_GPU_speedup_claimed": False,
    }
    ROOT.joinpath("placement_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if hot2_upper_bound <= 1:
        sys.exit("FROZEN_CLOCK_LIMITED_HOT2_NO_GO: kill factored mechanism under this placement model")


if __name__ == "__main__":
    main()
