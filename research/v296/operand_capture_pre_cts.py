#!/usr/bin/env python3
"""Fail-closed derivation of a symmetric operand-capture pre-CTS experiment.

Reuses the immutable V296 fourth-stage timing Tcl. Only the *module source*
and top are changed in both contestants' synthesized netlists. Does not
weaken timing/RC/floorplan or silently use the original unpipelined netlist.
"""
import argparse
import hashlib
import json
from pathlib import Path
import fourth_cone_flow

OUT = Path("build/v296/tile_slice")
ORIGINAL = "v296_tile_slice_return_tree"
REPAIRED = "v296_tile_slice_operand_capture"

def derive_runner(runner):
    if runner.count(ORIGINAL) < 4:
        raise ValueError("Missing original module/source anchors")
    if REPAIRED in runner:
        raise ValueError("Already retimed; refuse repeated transformation")
    out = runner.replace(ORIGINAL, REPAIRED)
    for needle in (
        "research/v296/v296_tile_slice_operand_capture.sv",
        "hierarchy -top v296_tile_slice_operand_capture",
        'V296_TOP="v296_tile_slice_operand_capture"',
        "cts45_fourth_diag.tcl",
        "V296_FOURTH_CONE_NO_SIGNOFF",
    ):
        if needle not in out:
            raise ValueError("Required retiming/physical anchor absent: " + needle)
    if ORIGINAL in out:
        raise ValueError("Mixed source variants")
    return out

def build():
    fourth_cone_flow.build()
    src = (OUT/"run_fourth_diag.sh").read_text()
    dst = derive_runner(src)
    (OUT/"run_operand_capture_fourth.sh").write_text(dst)
    (OUT/"operand_capture_manifest.json").write_text(json.dumps({
        "preregistration": "research/v296/OPERAND_CAPTURE_PIPELINE_PREREG_20261026.md",
        "evidence_tier": "PRECTS_ESTIMATED_ONLY_NOT_SIGNOFF",
        "retimed_top": REPAIRED,
        "both_contestants_same_retiming": True,
        "serial_fifth_stage_excluded": True,
        "source_runner_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "retimed_runner_sha256": hashlib.sha256(dst.encode()).hexdigest(),
        "unchanged_fourth_tcl_sha256": hashlib.sha256(
            (OUT/"cts45_fourth_diag.tcl").read_bytes()).hexdigest()
    }, indent=2)+"\n")
    print("V296_OPERAND_CAPTURE_MATCHED_PRECTS_GENERATED")

def self_test():
    fake = (
        "sha256sum research/v296/v296_tile_slice_return_tree.sv\n"
        "src=research/v296/v296_tile_slice_return_tree.sv\n"
        "hierarchy -top v296_tile_slice_return_tree\n"
        "V296_TOP=\"v296_tile_slice_return_tree\"\n"
        "openroad cts45_fourth_diag.tcl\n"
        "echo V296_FOURTH_CONE_NO_SIGNOFF\n"
    )
    x=derive_runner(fake)
    assert ORIGINAL not in x and x.count(REPAIRED) == 4
    for bad in (fake.replace("hierarchy -top v296_tile_slice_return_tree",""),
                fake.replace("cts45_fourth_diag.tcl",""),
                x):
        try: derive_runner(bad)
        except ValueError: pass
        else: raise AssertionError("Accepted unsafe runner")
    print("V296_OPERAND_CAPTURE_GENERATOR_SELFTEST_PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--build",action="store_true")
    a=p.parse_args()
    if a.self_test: self_test()
    if a.build: build()
    if not (a.self_test or a.build): p.error("Select a test or build")
