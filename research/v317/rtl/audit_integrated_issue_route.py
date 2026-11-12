#!/usr/bin/env python3
"""Read-only independent audit of the V317 integrated issue-control OpenROAD ZIP.

Usage: python research/v317/rtl/audit_integrated_issue_route.py artifact.zip
Only Python standard library is required. Not a silicon signoff.
"""
import argparse
import json
import math
import re
import zipfile

SOURCE_SHA = "20c5165651d0a941d3c60f918e4255961b8a2a90"
IMAGE_DIGEST = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"


def audit(path):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())

        def read(name):
            if name not in names:
                raise AssertionError("missing artifact file: " + name)
            return archive.read(name).decode("utf-8", "replace")

        assert read("source_sha.txt").strip() == SOURCE_SHA
        assert IMAGE_DIGEST in read("pinned_image.txt")
        assert IMAGE_DIGEST in read("container_digests.json")
        assert "PASS V317 integrated issue-control equivalence cycles=4096 accepted=13153" in read("rtl_simulation.log")
        results = {}
        for variant in ("source", "pairwise"):
            top = "vektor_v317_issue_integrated_top_" + variant
            prefix = "integrated_" + variant + "/"
            logdir = prefix + "logs/nangate45/" + top + "/base/"
            rptdir = prefix + "reports/nangate45/" + top + "/base/"
            assert "exit_code=0" in read(prefix + "status.txt")
            metrics = json.loads(read(logdir + "6_report.json"))
            route = read(logdir + "5_2_route.log")
            finish = read(rptdir + "6_finish.rpt")
            extraction = read(logdir + "6_report.log")
            assert "RCX-0045" in extraction, "no parasitic extraction evidence"
            drc = [int(v) for v in re.findall(r"Number of violations\s*=\s*(\d+)", route)]
            assert drc and drc[-1] == 0, "final detailed route not DRC-clean"
            assert re.search(r"Found 0 net violations", route)
            assert re.search(r"Found 0 pin violations", route)
            wires = [int(v) for v in re.findall(r"Total wire length\s*=\s*(\d+)\s*um", route)]
            assert wires, "no routed wire-length evidence"

            def metric(key):
                if key not in metrics:
                    raise AssertionError("missing metric " + variant + ": " + key)
                return metrics[key]

            for key in ("max_slew", "max_cap", "max_fanout"):
                assert metric("finish__timing__drv__" + key) == 0
            assert metric("finish__timing__drv__hold_violation_count") == 0
            assert metric("finish__timing__hold__ws") >= 0
            assert "finish report_checks -path_delay max reg to reg" in finish
            assert metric("finish__design__instance__area__macros") == 0
            match = re.search(r"Extract (\d+) nets", extraction)
            assert match, "missing extracted-net count"
            results[variant] = {
                "area_um2": metric("finish__design__instance__area__stdcell"),
                "fmax_hz": metric("finish__timing__fmax"),
                "setup_slack_ns": metric("finish__timing__setup__ws"),
                "hold_slack_ns": metric("finish__timing__hold__ws"),
                "setup_violations": metric("finish__timing__drv__setup_violation_count"),
                "power_proxy_mw": 1000 * metric("finish__power__total"),
                "wire_um": wires[-1],
                "final_drc": drc[-1],
                "extracted_nets": int(match.group(1)),
            }
        source, pairwise = results["source"], results["pairwise"]
        assert source["area_um2"] > pairwise["area_um2"], "frozen area prediction failed"
        assert source["setup_violations"] > 0 and source["setup_slack_ns"] < 0
        assert pairwise["setup_violations"] == 0 and pairwise["setup_slack_ns"] >= 0
        assert source["wire_um"] > pairwise["wire_um"]
        derived = {
            "area_reduction_pct": 100 * (1 - pairwise["area_um2"] / source["area_um2"]),
            "wire_reduction_pct": 100 * (1 - pairwise["wire_um"] / source["wire_um"]),
            "power_proxy_reduction_pct": 100 * (1 - pairwise["power_proxy_mw"] / source["power_proxy_mw"]),
            "fmax_gain_pct": 100 * (pairwise["fmax_hz"] / source["fmax_hz"] - 1),
            "period_source_ns": 1e9 / source["fmax_hz"],
            "period_pairwise_ns": 1e9 / pairwise["fmax_hz"],
            "setup_slack_delta_ps": 1000 * (pairwise["setup_slack_ns"] - source["setup_slack_ns"]),
            "pairwise_adverse_slack_budget_ps": 1000 * pairwise["setup_slack_ns"],
            "source_setup_repair_needed_ps": -1000 * source["setup_slack_ns"],
        }
        assert math.isclose(derived["setup_slack_delta_ps"], 79.0193, abs_tol=0.01)
        return {
            "provenance": {"source_sha": SOURCE_SHA, "image_digest": IMAGE_DIGEST},
            "results": results,
            "derived": derived,
            "limitations": "one corner, no SRAM macros, default-activity power, no workload IPC",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_zip")
    args = parser.parse_args()
    print(json.dumps(audit(args.artifact_zip), indent=2, sort_keys=True))
