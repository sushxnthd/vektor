#!/usr/bin/env python3
"""V296 one-shot symmetric upstream physical repair, frozen before evaluation.

Only the shared post-CTS repair window changes. The same generated Tcl is used
by V296 and the optimized serial control. Negative/censored outcomes are data.
"""
import argparse
import hashlib
import json
from pathlib import Path

import tile_slice_flow
import audit_tile_slice

ROOT = Path("research/v296")
OUT = Path("build/v296/tile_slice")
PREREG = "research/v296/V296_SYMMETRIC_UPSTREAM_REPAIR_PREREG_20261028.md"
TCL = "cts45_upstream_repair.tcl"
RUNNER = "run_upstream_repair.sh"
MANIFEST = "upstream_repair_manifest.json"
ANCHOR = ("repair_timing -hold\ndetailed_placement\n"
          "estimate_parasitics -placement\n"
          "v296_repair_metrics cts45_postcts_repaired")
INTERVENTION = (
    "repair_timing -hold\n"
    'puts "V296_UPSTREAM_REPAIR_BEGIN"\n'
    "set_max_fanout 8 [current_design]\n"
    "detailed_placement\n"
    "estimate_parasitics -placement\n"
    "repair_design -cap_margin 40 -slew_margin 40\n"
    "repair_timing -setup -slack_margin 2.200\n"
    "repair_timing -hold -slack_margin 0.050\n"
    'puts "V296_UPSTREAM_REPAIR_END"\n'
    "detailed_placement\n"
    "estimate_parasitics -placement\n"
    "v296_repair_metrics cts45_postcts_repaired"
)
RUNNER_ANCHOR = '"$root/cts45_tile.tcl"'
RUNNER_REPLACEMENT = '"$root/cts45_upstream_repair.tcl"'
VARIANTS = ("pairwise", "serial_onehot")


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def replace_exact(source, old, new):
    if source.count(old) != 1 or new in source:
        raise ValueError("Missing, duplicated or already-transformed frozen anchor")
    return source.replace(old, new)


def derive():
    _, generated = tile_slice_flow.generate()
    original_tcl = generated["cts45_tile.tcl"]
    for frozen in (
        "clock_tree_synthesis", "detailed_route -output_drc",
        "extract_parasitics -ext_model_file", "set_propagated_clock",
        "repair_timing -setup -slack_margin 0.250",
        "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0",
        'if {$env(V296_CONTROL_EXTRA) eq "1"}',
        "V296_CTS45_FIFTH_DONE",
    ):
        if frozen not in original_tcl:
            raise ValueError("Lost original physical constraint: " + frozen)
    new_tcl = replace_exact(original_tcl, ANCHOR, INTERVENTION)
    original_runner = (ROOT / "run_tile_slice_cts.sh").read_text()
    for frozen in (
        'serial_onehot) param=0; extra=1',
        'V296_CONTROL_EXTRA="$extra"',
        'V296_PLACE_DENSITY=0.45',
        'python3 research/v296/audit_tile_slice.py --single "$root" "$variant"',
    ):
        if frozen not in original_runner:
            raise ValueError("Lost original contestant protocol: " + frozen)
    new_runner = replace_exact(original_runner, RUNNER_ANCHOR, RUNNER_REPLACEMENT)
    return original_tcl, new_tcl, original_runner, new_runner


def build():
    tile_slice_flow.build()
    orig_tcl, new_tcl, orig_runner, new_runner = derive()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / TCL).write_text(new_tcl)
    (OUT / RUNNER).write_text(new_runner)
    manifest = {
        "preregistration": PREREG,
        "original_tcl_sha256": sha(orig_tcl),
        "derived_tcl_sha256": sha(new_tcl),
        "original_runner_sha256": sha(orig_runner),
        "derived_runner_sha256": sha(new_runner),
        "original_rtl_sha256": sha((ROOT / "v296_tile_slice.sv").read_bytes()),
        "clock_ns": 3.5, "rc_multiplier": 2.0, "density": 0.45,
        "setup_guard_ns": 0.250, "hold_guard_ns": 0.0,
        "area_limit_um2": 30000, "fanout_limit": 8,
        "additional_setup_margin_ns": 2.200,
        "additional_hold_margin_ns": 0.050,
        "candidate": "V296", "control": "V295_SERIAL_FIFTH_STAGE",
        "same_tcl_both": True, "holdouts": "SEALED",
        "gpu_performance_claim": False,
    }
    (OUT / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("V296_UPSTREAM_REPAIR_FROZEN")


def check_provenance():
    m = json.loads((OUT / MANIFEST).read_text())
    orig_tcl, new_tcl, orig_runner, new_runner = derive()
    expected = {
        "original_tcl_sha256": sha(orig_tcl),
        "derived_tcl_sha256": sha(new_tcl),
        "original_runner_sha256": sha(orig_runner),
        "derived_runner_sha256": sha(new_runner),
        "original_rtl_sha256": sha((ROOT / "v296_tile_slice.sv").read_bytes()),
    }
    for key, value in expected.items():
        if m.get(key) != value:
            raise ValueError("SHA mismatch: " + key)
    for filename, content in ((TCL, new_tcl), (RUNNER, new_runner)):
        if (OUT / filename).read_text() != content:
            raise ValueError("Generated physical source changed: " + filename)
    for key, value in (("clock_ns", 3.5), ("rc_multiplier", 2.0),
                       ("density", 0.45), ("setup_guard_ns", 0.250),
                       ("area_limit_um2", 30000), ("same_tcl_both", True),
                       ("holdouts", "SEALED")):
        if m.get(key) != value:
            raise ValueError("Frozen protocol mismatch: " + key)
    return m


def audit():
    # Reconstruct the generator inputs locally, but do not overwrite original
    # physical contestant artifacts. They are read as immutable evidence.
    build()
    m = check_provenance()
    rows = {}
    for variant, extra in (("pairwise", "0"), ("serial_onehot", "1")):
        try:
            exit_path = OUT / (variant + ".upstream_repair.exit.txt")
            if exit_path.read_text().strip() != "EXIT_CODE=0":
                raise ValueError("Tool failed, timed out or was interrupted")
            log = (OUT / (variant + ".high.log")).read_text(errors="replace")
            lines = log.splitlines()
            for marker in ("V296_UPSTREAM_REPAIR_BEGIN", "V296_UPSTREAM_REPAIR_END",
                           "V296_CTS45_EXTRA_REPAIR " + extra):
                if lines.count(marker) != 1:
                    raise ValueError("Missing/duplicate executed policy: " + marker)
            if not (lines.index("V296_UPSTREAM_REPAIR_BEGIN") <
                    lines.index("V296_UPSTREAM_REPAIR_END") <
                    lines.index("V296_CTS45_DETAIL_BEGIN")):
                raise ValueError("Repair was not upstream of detailed routing")
            if variant == "serial_onehot" and lines.count("V296_CTS45_FIFTH_DONE") != 1:
                raise ValueError("Strongest serial fifth-stage repair omitted")
            inputs = (OUT / (variant + ".inputs.sha256")).read_text()
            if m["derived_tcl_sha256"] + "  " + str(OUT / TCL) not in inputs:
                raise ValueError("Actual physical Tcl not SHA-pinned")
            rows[variant] = audit_tile_slice.case(OUT, variant)
        except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    verdict, comparison = audit_tile_slice.decision(rows)
    result = {
        "decision": verdict, "comparison": comparison, "rows": rows,
        "intervention": "symmetric_upstream_physical_repair",
        "evidence_tier": "EXTRACTED_RC_IF_BOTH_COMPLETE",
        "prediction": "NO_MATCHED_FEASIBLE_PARETO",
        "matched_gpu_throughput_gain": "NOT_ESTABLISHED",
        "same_clock_admission_ratio_if_feasible": 1.0,
        "holdouts": "SEALED", "signoff": False,
    }
    (OUT / "aggregate.upstream_repair.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if verdict != "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)


def self_test():
    orig_tcl, new_tcl, orig_runner, new_runner = derive()
    assert new_tcl.count("V296_UPSTREAM_REPAIR_BEGIN") == 1
    assert new_tcl.count("V296_UPSTREAM_REPAIR_END") == 1
    assert new_tcl.count("repair_timing -setup -slack_margin 2.200") == 1
    assert new_tcl.count("repair_timing -hold -slack_margin 0.050") == 1
    assert new_tcl.count("V296_CTS45_FIFTH_DONE") == 1
    assert orig_tcl.count("V296_CTS45_FIFTH_DONE") == 1
    assert RUNNER_ANCHOR in orig_runner and RUNNER_REPLACEMENT in new_runner
    for broken in (orig_tcl.replace(ANCHOR, ""),
                   orig_tcl.replace(ANCHOR, ANCHOR + "\n" + ANCHOR)):
        try:
            replace_exact(broken, ANCHOR, INTERVENTION)
        except ValueError:
            pass
        else:
            raise AssertionError("Mutated original Tcl accepted")
    for broken in (orig_runner.replace(RUNNER_ANCHOR, ""),
                   orig_runner.replace(RUNNER_ANCHOR, RUNNER_ANCHOR * 2)):
        try:
            replace_exact(broken, RUNNER_ANCHOR, RUNNER_REPLACEMENT)
        except ValueError:
            pass
        else:
            raise AssertionError("Mutated original runner accepted")
    print("V296_UPSTREAM_REPAIR_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    p.add_argument("--audit", action="store_true")
    a = p.parse_args()
    if a.self_test: self_test()
    if a.build: build()
    if a.audit: audit()
    if not (a.self_test or a.build or a.audit):
        p.error("Specify --self-test, --build or --audit")
