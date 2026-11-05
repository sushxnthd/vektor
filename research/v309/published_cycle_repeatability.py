#!/usr/bin/env python3
"""Published Accel-Sim cycle repeatability audit; no hardware speedup inference.

Two public issue-comment tables, different simulator configurations/trace revisions.
No table is asserted to use V309's authenticated 2020 Tesla V100 trace digest.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import re
import urllib.request

ISSUE = "https://github.com/accel-sim/accel-sim-framework/issues/60"
SOURCES = {
    "qv100": (1361450799, 4),
    "rtx2060": (1486100160, 2),
}
# Independently transcribed, frozen exact per-kernel rows from the two comments.
# Key is full application/configuration path; no family-only joining is allowed.
CYCLES = {
    "backprop-rodinia-2.0-ft/4096___data_result_4096_txt--final_kernel": (14936, 27380, 26978),
    "bfs-rodinia-2.0-ft/__data_graph4096_txt___data_graph4096_result_txt--final_kernel": (122465, 128635, 128635),
    "hotspot-rodinia-2.0-ft/30_6_40___data_result_30_6_40_txt--final_kernel": (54701, 108656, 107971),
    "heartwall-rodinia-2.0-ft/__data_test_avi_1___data_result_1_txt--final_kernel": (9224, 10595, 10593),
    "lud-rodinia-2.0-ft/_v__b__i___data_64_dat--final_kernel": (136901, 185324, 185784),
    "nw-rodinia-2.0-ft/128_10___data_result_128_10_txt--final_kernel": (138970, 134363, 134362),
    "nn-rodinia-2.0-ft/__data_filelist_4_3_30_90___data_filelist_4_3_30_90_result_txt--final_kernel": (30800, 38416, 38634),
    "pathfinder-rodinia-2.0-ft/1000_20_5___data_result_1000_20_5_txt--final_kernel": (31713, 31969, 31974),
    "srad_v2-rodinia-2.0-ft/__data_matrix128x128_txt_0_127_0_127__5_2___data_result_matrix128x128_1_150_1_100__5_2_txt--final_kernel": (29798, 39680, 38897),
    "streamcluster-rodinia-2.0-ft/3_6_16_1024_1024_100_none_output_txt_1___data_result_3_6_16_1024_1024_100_none_1_txt--final_kernel": (1149457, 1145973, 1144202),
}
EXPECTED = {
    "qv100": {k: (v[0],) * 4 for k, v in CYCLES.items()},
    "rtx2060": {k: v[1:] for k, v in CYCLES.items()},
}


def parse_comment(body: str, repeat_count: int) -> dict[str, tuple[int, ...]]:
    """Independent markdown parser, scoped to full rodinia_2.0-ft paths."""
    found: dict[str, tuple[int, ...]] = {}
    for raw in body.splitlines():
        line = raw.strip().strip("|")
        fields = [s.strip().strip("`") for s in line.split("|")]
        if not fields or not re.fullmatch(
            r"[A-Za-z0-9_+.-]+-rodinia-2[.]0-ft/[^|]+--final_kernel",
            fields[0],
        ):
            continue
        if len(fields) != repeat_count + 1:
            raise ValueError("published cycle row has wrong number of repeats")
        if fields[0] in found:
            raise ValueError("duplicate workload key in source")
        if any(not re.fullmatch(r"[0-9]+", x) for x in fields[1:]):
            raise ValueError("noninteger published cycle count")
        cycles = tuple(int(x) for x in fields[1:])
        if any(x <= 0 for x in cycles):
            raise ValueError("nonpositive published cycle count")
        found[fields[0]] = cycles
    if len(found) != 10:
        raise ValueError(f"expected exactly ten published 2.0-ft rows; got {len(found)}")
    return found


def attest(name: str, body: str) -> None:
    _, n = SOURCES[name]
    observed = parse_comment(body, n)
    if observed != EXPECTED[name]:
        absent = sorted(set(EXPECTED[name]) - set(observed))
        extra = sorted(set(observed) - set(EXPECTED[name]))
        changed = sorted(k for k in observed.keys() & EXPECTED[name].keys()
                         if observed[k] != EXPECTED[name][k])
        raise ValueError(f"source attestation FAILED: {name}; absent={absent}; "
                         f"extra={extra}; changed={changed}")


def fetch_comment(comment_id: int) -> str:
    url = f"https://api.github.com/repos/accel-sim/accel-sim-framework/issues/comments/{comment_id}"
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "vektor-v309-source-attestation",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        obj = json.load(response)
    if obj.get("id") != comment_id or not isinstance(obj.get("body"), str):
        raise ValueError("wrong comment id or missing body")
    return obj["body"]


def ratio(n: int, d: int) -> str:
    return str(Fraction(n, d))


def evaluate() -> dict:
    if len(CYCLES) != 10 or set(EXPECTED["qv100"]) != set(EXPECTED["rtx2060"]):
        raise AssertionError("published workload-key conservation failure")
    summary = {}
    rows = []
    for name, data in EXPECTED.items():
        nonzero = 0
        max_range = Fraction(0)
        for k, vals in data.items():
            if len(vals) != SOURCES[name][1] or any(v <= 0 for v in vals):
                raise AssertionError("invalid frozen cycle table")
            r = Fraction(max(vals) - min(vals), min(vals))
            nonzero += (r > 0)
            max_range = max(max_range, r)
        summary[name] = {
            "workloads": len(data),
            "repeats_per_workload": SOURCES[name][1],
            "workloads_with_nonzero_cycle_range": nonzero,
            "maximum_within_workload_relative_range": str(max_range),
            "maximum_within_workload_relative_range_percent": float(max_range * 100),
        }
    for key in sorted(CYCLES):
        q, r1, r2 = CYCLES[key]
        rows.append({
            "workload": key, "qv100_four_repeats": list(EXPECTED["qv100"][key]),
            "rtx2060_two_repeats": [r1, r2],
            "rtx2060_within_repeat_max_over_min": ratio(max(r1, r2), min(r1, r2)),
            "descriptive_different_config_first_run_ratio": ratio(r1, q),
        })
    if summary["qv100"]["workloads_with_nonzero_cycle_range"] != 0:
        raise AssertionError("frozen repeatable-regime prediction failed")
    if summary["rtx2060"]["workloads_with_nonzero_cycle_range"] < 8:
        raise AssertionError("frozen nonrepeatable-regime prediction failed")
    return {
        "status": "PASS", "evidence_tier": "published_third_party_simulator_cycle_repeatability_NOT_hardware",
        "source_issue": ISSUE,
        "comment_ids": {k: v[0] for k, v in SOURCES.items()},
        "summary": summary, "rows": rows,
        "source_attestation": "NOT_RUN_OFFLINE",
        "v309_archive_digest_matched": False,
        "hardware_counter_calibrated": False,
        "physical_speedup_inference_permitted": False,
        "limitations": [
            "Different GPU configurations and likely simulator/trace versions; cross-config ratios are not causal",
            "No proof either source used V309's authenticated Tesla V100 trace archive",
            "Reported simulator cycles are not hardware-measured cycles",
            "Ten published workloads are a convenience sample, not prospective holdout",
            "Zero observed variance in four repeats does not prove general determinism",
            "No new architecture mechanism, RTL area/timing or GPU speedup",
        ],
    }


def selftest() -> dict:
    for name, expected in EXPECTED.items():
        text = "\n".join("|" + "|".join([k, *(str(x) for x in vals)]) + "|"
                         for k, vals in expected.items())
        attest(name, text)
        first = next(iter(expected))
        changed = text.replace(str(expected[first][0]), str(expected[first][0] + 1), 1)
        try:
            attest(name, changed)
        except ValueError:
            pass
        else:
            raise AssertionError("source value mutation was accepted")
        try:
            attest(name, text.splitlines()[0] + "\n" + text)
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate source row was accepted")
    result = evaluate()
    assert result["summary"]["qv100"]["workloads_with_nonzero_cycle_range"] == 0
    assert result["summary"]["rtx2060"]["workloads_with_nonzero_cycle_range"] == 9
    return {"status": "PASS", "independent_parser_cases": 2,
            "changed_value_refusals": 2, "duplicate_row_refusals": 2,
            "qv100_nonzero": 0, "rtx2060_nonzero": 9}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--attest-public-source", action="store_true")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    if args.selftest:
        result = selftest()
    else:
        result = evaluate()
        if args.attest_public_source:
            for name, (comment_id, _) in SOURCES.items():
                attest(name, fetch_comment(comment_id))
            result["source_attestation"] = "PASS_EXACT_TWO_PUBLIC_COMMENT_TABLES"
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output == "-":
        print(rendered, end="")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rendered)


if __name__ == "__main__":
    main()
