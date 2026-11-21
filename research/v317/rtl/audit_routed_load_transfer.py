#!/usr/bin/env python3
"""Independent read-only audit of the V317 four-route OpenROAD artifact ZIP.

Consumes raw 6_report.json and 5_2_route.json, not a researcher summary.
The result is single-corner control-block evidence, not GPU performance.
"""
import argparse
import json
import math
import sys
import zipfile

CASES = ("source-10-fF", "pairwise-10-fF", "source-40-fF", "pairwise-40-fF")
EXPECTED_SHA = "01edebed092c65c264d42814a927614338b8ef9e"
EXPECTED_IMAGE = "openroad/orfs@sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def single_json(z, case, suffix):
    matches = [n for n in z.namelist()
               if n.startswith(case + "/logs/") and n.endswith("/" + suffix)]
    require(len(matches) == 1, f"{case}: expected one {suffix}, found {len(matches)}")
    return json.loads(z.read(matches[0]))


def metric(d, key, case):
    require(key in d, f"{case}: missing {key}")
    value = d[key]
    require(isinstance(value, (int, float)) and math.isfinite(value),
            f"{case}: invalid {key}")
    return value


def audit(path):
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, "ZIP integrity failure")
        require(z.read("source_sha.txt").decode().strip() == EXPECTED_SHA,
                "source SHA changed")
        require(z.read("pinned_image.txt").decode().strip() == EXPECTED_IMAGE,
                "container changed")
        rows = {}
        for case in CASES:
            variant, load_text = case.split("-")[:2]
            load = int(load_text)
            sdc = z.read(f"{case}/load.sdc").decode()
            require(f"set_load {load}.0 [get_ports {{grant*}}]" in sdc,
                    f"{case}: incorrect load")
            require("create_clock -name core_clk -period 2.000" in sdc,
                    f"{case}: clock mismatch")
            require("set_clock_uncertainty 0.100" in sdc,
                    f"{case}: uncertainty mismatch")
            require("exit_code=0" in z.read(f"{case}/status.txt").decode(),
                    f"{case}: failed route")
            r = single_json(z, case, "6_report.json")
            route = single_json(z, case, "5_2_route.json")
            area = metric(r, "finish__design__instance__area__stdcell", case)
            setup = metric(r, "finish__timing__setup__ws", case)
            hold = metric(r, "finish__timing__hold__ws", case)
            fmax = metric(r, "finish__timing__fmax", case)
            power = metric(r, "finish__power__total", case)
            wire = metric(route, "detailedroute__route__wirelength", case)
            drc = metric(route, "detailedroute__route__drc_errors", case)
            antenna = metric(route, "detailedroute__antenna__violating__nets", case)
            violations = {
                k: metric(r, k, case)
                for k in ("finish__timing__drv__max_slew",
                          "finish__timing__drv__max_cap",
                          "finish__timing__drv__max_fanout",
                          "finish__timing__drv__setup_violation_count",
                          "finish__timing__drv__hold_violation_count")
            }
            require(all(v == 0 for v in violations.values()),
                    f"{case}: electrical violation {violations}")
            require(drc == 0 and antenna == 0, f"{case}: DRC/antenna violation")
            require(setup >= 0 and hold >= 0, f"{case}: timing violation")
            require(area > 0 and fmax > 0 and power >= 0 and wire > 0,
                    f"{case}: invalid physical metric")
            require(metric(r, "finish__design__instance__count__class:sequential_cell", case) == 40,
                    f"{case}: wrapper changed")
            require(metric(r, "finish__design__die__area", case) == 3600,
                    f"{case}: die changed")
            rows[case] = {
                "area_um2": area, "setup_slack_ns": setup, "hold_slack_ns": hold,
                "minimum_period_ns": 1e9 / fmax, "fmax_hz": fmax,
                "wire_um": wire, "vectorless_power_proxy_W": power,
                "route_drc": drc, "antenna_nets": antenna,
                "electrical_violations": violations,
            }
        for variant, old_area, old_period in (("source", 1316, 1.56),
                                               ("pairwise", 583, 0.58)):
            x = rows[f"{variant}-10-fF"]
            require(abs(x["area_um2"] - old_area) / old_area < .1,
                    f"{variant}: replication area mismatch")
            require(abs(x["minimum_period_ns"] - old_period) / old_period < .1,
                    f"{variant}: replication period mismatch")
        comparisons = {}
        for load in (10, 40):
            source = rows[f"source-{load}-fF"]
            pair = rows[f"pairwise-{load}-fF"]
            require(pair["area_um2"] < source["area_um2"], f"{load} fF: area NO-GO")
            require(pair["minimum_period_ns"] < source["minimum_period_ns"],
                    f"{load} fF: timing NO-GO")
            comparisons[str(load)] = {
                "routed_cell_area_reduction_pct":
                    100 * (1 - pair["area_um2"] / source["area_um2"]),
                "wire_length_reduction_pct":
                    100 * (1 - pair["wire_um"] / source["wire_um"]),
                "isolated_period_ratio_source_over_pairwise":
                    source["minimum_period_ns"] / pair["minimum_period_ns"],
                "vectorless_power_proxy_reduction_pct":
                    100 * (1 - pair["vectorless_power_proxy_W"] /
                           source["vectorless_power_proxy_W"]),
                "intrinsic_grant_equivalent_service_gain": 1.0,
            }
        return {
            "evidence_tier": "single-corner routed 40-FF control block, NOT GPU tile",
            "source_sha": EXPECTED_SHA,
            "cases": rows,
            "comparisons": comparisons,
            "decision": "survives isolated load transfer; no intrinsic same-clock service gain",
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_zip")
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.artifact_zip), indent=2, sort_keys=True,
                         allow_nan=False))
    except (AssertionError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        print(f"AUDIT FAIL: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
