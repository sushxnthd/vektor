#!/usr/bin/env python3
"""Independent V312 matched Nangate45 placement-RC audit; not extracted signoff."""
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path("build/v312_physical")
DESIGNS = ("compact_head_only", "factored_fallback")
CORNERS = ("dense", "relaxed")
ARRIVAL = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s+data arrival time\s*$", re.M)
AREA = re.compile(r"Chip area for module[^:]*:\s*([0-9]+(?:\.[0-9]+)?)", re.I)
TRANSFER_GAIN = 1.268568
F = 0.5
TRANSFER_AMDAHL = 1.0 / ((1-F) + F/TRANSFER_GAIN)


def unique_between(raw, begin, end):
    if raw.count(begin) != 1 or raw.count(end) != 1:
        raise AssertionError("missing or duplicate evidence delimiters")
    a, b = raw.index(begin) + len(begin), raw.index(end)
    if a >= b:
        raise AssertionError("reversed evidence delimiters")
    return raw[a:b]


def no_tool_error(raw):
    if re.search(r"^(?:Error:|ERROR|\[ERROR|ERROR\s*:)", raw, re.M):
        raise AssertionError("tool reported error")


def delay(raw, placed):
    no_tool_error(raw)
    if placed:
        timing = unique_between(raw, "V312_PLACED_RC_BEGIN", "V312_ELECTRICAL_BEGIN")
        elec = unique_between(raw, "V312_ELECTRICAL_BEGIN", "V312_ELECTRICAL_END")
        unique_between(raw, "V312_ELECTRICAL_END", "V312_PLACED_RC_END")
    else:
        timing = unique_between(raw, "V312_ZERO_BEGIN", "V312_ZERO_END")
        elec = None
    vals = ARRIVAL.findall(timing)
    if len(vals) != 1:
        raise AssertionError(f"expected exactly one data arrival, found {vals}")
    v = float(vals[0])
    if not math.isfinite(v) or not (0 < v < 100):
        raise AssertionError("invalid path delay")
    violation = False if elec is None else bool(re.search(r"(?i)\b(?:VIOLATED|VIOLATION\s*:\s*[1-9]|VIOLATORS\s*:\s*[1-9])\b", elec))
    return v, violation


def mapped_area(raw):
    no_tool_error(raw)
    vals = AREA.findall(raw)
    if not vals:
        raise AssertionError("no mapped cell area in Yosys synthesis report")
    v = float(vals[-1])
    if not math.isfinite(v) or v <= 0:
        raise AssertionError("invalid mapped area")
    return v


def selftest():
    a = "V312_PLACED_RC_BEGIN\n  0.43 data arrival time\n  1.00 data required time\nV312_ELECTRICAL_BEGIN\nNo violations\nV312_ELECTRICAL_END\nV312_PLACED_RC_END\n"
    assert delay(a, True) == (0.43, False)
    assert mapped_area("Chip area for module '\\foo': 251.370\n") == 251.370
    for forged in (a.replace("data arrival time", "data required time"),
                   a.replace("V312_PLACED_RC_BEGIN", "V312_PRELAYOUT_ONLY"),
                   a.replace("No violations", "Error: missing library"),
                   a.replace("No violations", "VIOLATED"),
                   a + "V312_PLACED_RC_BEGIN\n"):
        try:
            d, violation = delay(forged, True)
            if violation:
                raise AssertionError("violation correctly detected")
        except AssertionError:
            continue
        raise AssertionError("forged evidence accepted")


def main():
    selftest()
    area = {d: mapped_area((ROOT / f"{d}.synthesis.log").read_text()) for d in DESIGNS}
    zero = {d: delay((ROOT / f"{d}.zero.sta.log").read_text(), False)[0] for d in DESIGNS}
    corners = {}
    for corner in CORNERS:
        measurements = {d: delay((ROOT / f"{d}_{corner}.sta.log").read_text(), True) for d in DESIGNS}
        d = measurements["factored_fallback"][0] / measurements["compact_head_only"][0]
        corners[corner] = {
            "compact_head_only_ns": measurements["compact_head_only"][0],
            "factored_fallback_ns": measurements["factored_fallback"][0],
            "candidate_to_control_delay_ratio": d,
            "any_explicit_max_slew_or_cap_violation": any(x[1] for x in measurements.values()),
            "hotspot_f_half_upper_bound": (1 / (0.5 + 0.5 / 1.95)) / d,
            "transfer_f_half_upper_bound": TRANSFER_AMDAHL / d,
            "disjoint_clock_limited_ratio": 1 / d,
        }
    ratio = area["factored_fallback"] / area["compact_head_only"]
    failures = []
    if ratio > 1.5:
        failures.append("AREA_GT_1_50X")
    for corner, row in corners.items():
        if row["any_explicit_max_slew_or_cap_violation"]:
            failures.append(f"{corner}_ELECTRICAL_VIOLATION")
        if row["transfer_f_half_upper_bound"] <= 1.0:
            failures.append(f"{corner}_TRANSFER_UPPER_BOUND_NO_WIN")
    result = {
        "tier": "Nangate45_OpenROAD_placement_estimated_RC_NOT_routed_or_extracted",
        "baseline": "optimized_head_only_NOT_equal_information_buffered_collector",
        "area": area,
        "area_ratio": ratio,
        "zero_wire_ns": zero,
        "corners": corners,
        "frozen_transfer_admission_gain": TRANSFER_GAIN,
        "frozen_issue_limited_fraction": F,
        "routed_electrical_signoff": False,
        "gpu_throughput_measured": False,
        "novelty_established": False,
        "kill_reasons": failures,
        "decision": "KILL_THIS_RTL" if failures else "PREFILTER_ONLY_PASS",
    }
    ROOT.joinpath("independent_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if failures:
        sys.exit("V312_FROZEN_PHYSICAL_KILL: " + ",".join(failures))


if __name__ == "__main__":
    main()
