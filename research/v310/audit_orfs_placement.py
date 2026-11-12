#!/usr/bin/env python3
"""V310 prospective matched-placement audit; never a routed signoff claim."""
import json
from pathlib import Path
import re
import sys

ROOT = Path("build/v310_orfs")
DESIGNS = ("compact_greedy", "verified_coalescer")
VARIANTS = ("dense", "relaxed")
ARRIVAL = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s+data arrival time\s*$", re.M)
AREA = re.compile(r"Chip area for module\s+[^:\n]+:\s*([0-9]+(?:\.[0-9]+)?)")
FROZEN_WIN = 1.5625
AREA_CEILING = 1.50


def parse_timing(raw: str, zero_wire: bool) -> float:
    begin, end = (
        ("V310_SAME_NETLIST_ZERO_WIRE_BEGIN", "V310_SAME_NETLIST_ZERO_WIRE_END")
        if zero_wire else
        ("V310_PLACEMENT_ESTIMATED_RC_BEGIN", "V310_PLACEMENT_ESTIMATED_RC_END")
    )
    if raw.count(begin) != 1 or raw.count(end) != 1:
        raise AssertionError("missing or duplicated provenance markers")
    if not zero_wire:
        if raw.count("V310_PLACEMENT_ELECTRICAL_BEGIN") != 1 or raw.count("V310_PLACEMENT_ELECTRICAL_END") != 1:
            raise AssertionError("missing electrical report markers")
    if re.search(r"^(?:Error:|ERROR|\[ERROR)", raw, re.M):
        raise AssertionError("OpenROAD reported error")
    section = raw.split(begin, 1)[1].split(end, 1)[0]
    arrivals = ARRIVAL.findall(section)
    if len(arrivals) != 1:
        raise AssertionError(f"not exactly one actual data arrival time: {arrivals}")
    value = float(arrivals[0])
    if not (0 < value < 100):
        raise AssertionError("impossible delay")
    return value


def parse_area(raw: str) -> float:
    areas = [float(x) for x in AREA.findall(raw)]
    if not areas:
        raise AssertionError("no matched standard-cell area in synthesis log")
    if not 0 < areas[-1] < 1_000_000:
        raise AssertionError("invalid area")
    return areas[-1]


def selftest():
    raw = ("V310_PLACEMENT_ESTIMATED_RC_BEGIN\n"
           "  0.46 data arrival time\n"
           "  1.00 data required time\n"
           "V310_PLACEMENT_ELECTRICAL_BEGIN\n"
           "No violations\nV310_PLACEMENT_ELECTRICAL_END\n"
           "V310_PLACEMENT_ESTIMATED_RC_END\n")
    assert parse_timing(raw, False) == 0.46
    for bad in (
        raw.replace("0.46 data arrival time", "1.00 data required time"),
        raw.replace("V310_PLACEMENT_ESTIMATED_RC_BEGIN", "UNVERIFIED"),
        raw.replace("No violations", "Error: invalid"),
        raw.replace("V310_PLACEMENT_ELECTRICAL_END", "MISSING"),
    ):
        try:
            parse_timing(bad, False)
        except AssertionError:
            pass
        else:
            raise AssertionError("forged timing/electrical evidence accepted")
    assert parse_area("Chip area for module '\\x': 251.370000") == 251.37
    try:
        parse_area("Number of cells: 500")
    except AssertionError:
        pass
    else:
        raise AssertionError("generic cell count accepted as mapped area")


def main():
    selftest()
    zero_wire = {}
    areas = {}
    for name in DESIGNS:
        zero_wire[name] = parse_timing((ROOT / f"{name}.zero_wire.sta.log").read_text(), True)
        areas[name] = parse_area((ROOT / f"{name}.synthesis.log").read_text())
    area_ratio = areas["verified_coalescer"] / areas["compact_greedy"]
    corners = {}
    for variant in VARIANTS:
        delays = {}
        for name in DESIGNS:
            delays[name] = parse_timing((ROOT / f"{name}_{variant}.sta.log").read_text(), False)
        ratio = delays["verified_coalescer"] / delays["compact_greedy"]
        corners[variant] = dict(delay_ns=delays, delay_ratio=ratio,
                                frozen_q075_optimistic_issue_times_frequency=FROZEN_WIN / ratio)
    timing_survives = all(c["delay_ratio"] < FROZEN_WIN for c in corners.values())
    area_survives = area_ratio <= AREA_CEILING
    result = dict(
        evidence_tier="Nangate45_placed_estimated_RC_NOT_routed_or_extracted",
        equal_top_level_input_width=40, equal_top_level_output_width=4,
        mapped_area=areas, mapped_area_ratio=area_ratio, frozen_area_ceiling=AREA_CEILING,
        same_netlist_zero_wire_ns=zero_wire,
        same_netlist_zero_wire_delay_ratio=zero_wire["verified_coalescer"] / zero_wire["compact_greedy"],
        placed_corners=corners, frozen_q075_ideal_issue_gain=FROZEN_WIN,
        controller_area_gate="PASS" if area_survives else "KILL",
        optimistic_clock_limited_timing_gate="PASS" if timing_survives else "KILL",
        electrical_signoff="NOT_ESTABLISHED",
        register_identity_comparator_and_operand_fanout="NOT_INCLUDED",
        strong_existing_operand_reuse_baseline="NOT_YET_MEASURED",
        actual_GPU_throughput_or_power="NOT_MEASURED",
    )
    ROOT.joinpath("independent_physical_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not area_survives or not timing_survives:
        sys.exit("V310_FROZEN_PHYSICAL_PREFILTER_KILL")


if __name__ == "__main__":
    main()
