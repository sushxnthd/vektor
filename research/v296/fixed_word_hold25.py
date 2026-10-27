#!/usr/bin/env python3
"""Symmetric V296 post-CTS hold-margin intervention; same RTL and frozen signoff."""
import argparse
import hashlib
import json
from pathlib import Path
import fixed_word_postcts_flow
import audit_tile_slice

ROOT = Path("build/v296/tile_slice")
BASE_TCL = "cts45_tile.tcl"
NEW_TCL = "cts45_hold25_tile.tcl"
BASE_RUN = "run_fixed_word_postcts.sh"
NEW_RUN = "run_fixed_word_hold25_postcts.sh"
MANIFEST = "fixed_word_hold25_manifest.json"
HOLD_MARGIN = 0.025

def digest(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()

def derive(tcl, runner):
    anchor = "repair_timing -hold\n"
    if tcl.count(anchor) != 1 or "V296_HOLD25_MARGIN_NS" in tcl:
        raise ValueError("Original hold repair anchor missing or duplicated")
    for required in ("repair_timing -setup -slack_margin 0.250",
                     "clock_tree_synthesis", "detailed_route -output_drc",
                     "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0",
                     'if {$env(V296_CONTROL_EXTRA) eq "1"}'):
        if required not in tcl:
            raise ValueError("Frozen physical constraint absent: " + required)
    new_tcl = tcl.replace(anchor,
        'puts "V296_HOLD25_MARGIN_NS 0.025"\n'
        "repair_timing -hold -slack_margin 0.025\n")
    old_call = '"$root/cts45_tile.tcl"'
    if runner.count(old_call) != 1 or "cts45_hold25_tile.tcl" in runner:
        raise ValueError("Original physical runner anchor missing or duplicated")
    for required in ("serial_onehot) param=0; extra=1",
                     'V296_CONTROL_EXTRA="$extra"',
                     'V296_TOP="v296_tile_slice_fixed_word"'):
        if required not in runner:
            raise ValueError("Strong matched control or RTL top missing: " + required)
    new_runner = runner.replace(old_call, '"$root/cts45_hold25_tile.tcl"')
    return new_tcl, new_runner

def build():
    fixed_word_postcts_flow.build()
    old_tcl = (ROOT / BASE_TCL).read_text()
    old_run = (ROOT / BASE_RUN).read_text()
    new_tcl, new_run = derive(old_tcl, old_run)
    (ROOT / NEW_TCL).write_text(new_tcl)
    (ROOT / NEW_RUN).write_text(new_run)
    manifest = {
        "evidence_tier": "PROSPECTIVE_FULL_ROUTE_NOT_SIGNOFF",
        "preregistration": "research/v296/FIXED_WORD_HOLD25_PREREG_20261027.md",
        "original_extracted_replay_run": 40490815519,
        "original_physical_run": 40469489684,
        "sole_architecture_mechanism": "V296_PAIRWISE_BANK_ADMISSION",
        "rtl_top": "v296_tile_slice_fixed_word",
        "symmetric_hold_repair": True,
        "serial_extra_fifth_stage": True,
        "hold_slack_margin_ns": HOLD_MARGIN,
        "clock_ns": 3.5, "rc_multiplier": 2.0, "placement_density": 0.45,
        "source_tcl_sha256": digest(old_tcl),
        "derived_tcl_sha256": digest(new_tcl),
        "source_runner_sha256": digest(old_run),
        "derived_runner_sha256": digest(new_run),
        "source_rtl_sha256": digest(Path("research/v296/v296_tile_slice_fixed_word.sv").read_bytes()),
        "workload_holdouts": "SEALED", "gpu_speedup_claim": False
    }
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("V296_HOLD25_SYMMETRIC_PHYSICAL_TRIAL_GENERATED")

def audit(root):
    m = json.loads((root / MANIFEST).read_text())
    if (m["hold_slack_margin_ns"] != HOLD_MARGIN or
        m["clock_ns"] != 3.5 or m["rc_multiplier"] != 2.0 or
        m["placement_density"] != 0.45 or
        not m["symmetric_hold_repair"] or not m["serial_extra_fifth_stage"] or
        m["workload_holdouts"] != "SEALED"):
        raise ValueError("Frozen hold trial provenance mismatch")
    for name, key in ((BASE_TCL, "source_tcl_sha256"),
                      (NEW_TCL, "derived_tcl_sha256"),
                      (BASE_RUN, "source_runner_sha256"),
                      (NEW_RUN, "derived_runner_sha256")):
        if digest((root / name).read_bytes()) != m[key]:
            raise ValueError("Modified generated source: " + name)
    expected_tcl, expected_run = derive((root / BASE_TCL).read_text(),
                                       (root / BASE_RUN).read_text())
    if (root / NEW_TCL).read_text() != expected_tcl or (root / NEW_RUN).read_text() != expected_run:
        raise ValueError("Non-symmetric or unexpected physical modification")
    rows = {}
    for variant, extra in (("pairwise", "0"), ("serial_onehot", "1")):
        log = (root / (variant + ".high.log")).read_text(errors="replace")
        if log.splitlines().count("V296_HOLD25_MARGIN_NS 0.025") != 1:
            raise ValueError("Missing or duplicate executed hold-margin marker")
        if log.splitlines().count("V296_CTS45_EXTRA_REPAIR " + extra) != 1:
            raise ValueError("Missing strongest matched-control marker")
        if "EXIT_CODE=0" not in (root / (variant + ".fixed_word_postcts.exit.txt")).read_text():
            raise ValueError("Physical tool did not complete: " + variant)
        inputs = (root / (variant + ".inputs.sha256")).read_text()
        if m["source_rtl_sha256"] + "  research/v296/v296_tile_slice_fixed_word.sv" not in inputs:
            raise ValueError("RTL source changed: " + variant)
        if m["derived_tcl_sha256"] + "  " + str(root / NEW_TCL) not in inputs:
            raise ValueError("Hold25 Tcl not pinned in run inputs: " + variant)
        rows[variant] = audit_tile_slice.case(root, variant)
    verdict, comparison = audit_tile_slice.decision(rows)
    result = {"decision": verdict, "rows": rows, "comparison": comparison,
              "evidence_tier": "MATCHED_POSTCTS_ROUTED_EXTRACTED_RC",
              "source_rtl_sha256": m["source_rtl_sha256"],
              "hold_margin_ns": HOLD_MARGIN, "holdouts": "SEALED",
              "physical_signoff": verdict == "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU",
              "production_gpu_advantage": False}
    (root / "aggregate.hold25.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"decision": verdict,
                      "pairwise_final": rows["pairwise"]["final"],
                      "serial_final": rows["serial_onehot"]["final"],
                      "comparison": comparison}, indent=2))
    if verdict != "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)

def self_test():
    t = ("clock_tree_synthesis\ndetailed_route -output_drc\n"
         "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0\n"
         "repair_timing -setup -slack_margin 0.250\n"
         'if {$env(V296_CONTROL_EXTRA) eq "1"}\n'
         "repair_timing -hold\n")
    r = ('serial_onehot) param=0; extra=1\n'
         'V296_CONTROL_EXTRA="$extra"\n'
         'V296_TOP="v296_tile_slice_fixed_word"\n'
         'openroad -exit "$root/cts45_tile.tcl"\n')
    a,b = derive(t,r)
    assert a.count("repair_timing -hold -slack_margin 0.025") == 1
    assert b.count('"$root/cts45_hold25_tile.tcl"') == 1
    for bad_t,bad_r in ((t+t,r),(t,r.replace("extra=1","extra=0")),
                        (t.replace("repair_timing -hold\n",""),r),
                        (t,r.replace('"$root/cts45_tile.tcl"',""))):
        try: derive(bad_t,bad_r)
        except ValueError: pass
        else: raise AssertionError("Unsafe physical intervention accepted")
    print("V296_HOLD25_DERIVATION_SELFTEST_PASS")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    p.add_argument("--audit", type=Path)
    a=p.parse_args()
    if a.self_test: self_test()
    if a.build: build()
    if a.audit: audit(a.audit)
    if not (a.self_test or a.build or a.audit): p.error("Select mode")
if __name__ == "__main__":
    main()
