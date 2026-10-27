#!/usr/bin/env python3
"""Derive symmetric fixed-word post-CTS experiment without altering physical Tcl."""
import argparse
import hashlib
import json
from pathlib import Path
import bank_decode_postcts_flow

OUT = Path("build/v296/tile_slice")
ROOT = Path("research/v296")
OLD = "v296_tile_slice_bank_decode"
NEW = "v296_tile_slice_fixed_word"
SRC = "run_bank_decode_postcts.sh"
DST = "run_fixed_word_postcts.sh"
MANIFEST = "fixed_word_postcts_manifest.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def derive(text):
    # Two source references, hierarchy, synth, V296_TOP.
    if text.count(OLD) != 5 or NEW in text:
        raise ValueError("Unexpected decoded source/top count or mixed RTL")
    for anchor in (
        "serial_onehot) param=0; extra=1",
        'V296_CONTROL_EXTRA="$extra"',
        "python3 research/v296/audit_tile_slice.py --single",
        "V296_DECODED_POSTCTS_EXTRACTED_COMPLETE",
        "V296_PLACE_DENSITY=0.45",
    ):
        if text.count(anchor) != 1:
            raise ValueError("Missing or ambiguous strong-control/physical anchor: " + anchor)
    out = text.replace(OLD, NEW).replace(
        "V296_DECODED_POSTCTS_EXTRACTED_COMPLETE",
        "V296_FIXED_WORD_POSTCTS_EXTRACTED_COMPLETE")
    if OLD in out or out.count(NEW) != 5:
        raise ValueError("Mixed top after transformation")
    return out


def build():
    bank_decode_postcts_flow.build()
    src = (OUT / SRC).read_text()
    transformed = derive(src)
    physical = (OUT / "cts45_tile.tcl").read_bytes()
    for anchor in (
        "clock_tree_synthesis", "detailed_route -output_drc",
        "extract_parasitics -ext_model_file",
        "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0",
        'if {$env(V296_CONTROL_EXTRA) eq "1"}',
        "repair_timing -setup -slack_margin 0.250",
    ):
        if anchor not in physical.decode():
            raise ValueError("Frozen CTS/serial repair absent: " + anchor)
    (OUT / DST).write_text(transformed)
    manifest = {
        "preregistration": "research/v296/FIXED_WORD_POSTCTS_STRONG_CONTROL_PREREG_20261027.md",
        "evidence_tier": "POSTCTS_DETAILED_ROUTE_EXTRACTED_RC_PENDING",
        "source_run": 40457696916,
        "rtl_top": NEW,
        "same_rtl_for_both": True,
        "strongest_serial_fifth_stage_required": True,
        "candidate_extra_repair": 0,
        "serial_extra_repair": 1,
        "clock_ns": 3.5,
        "rc_multiplier": 2.0,
        "placement_density": 0.45,
        "source_runner_sha256": sha(src.encode()),
        "derived_runner_sha256": sha(transformed.encode()),
        "unchanged_physical_tcl_sha256": sha(physical),
        "source_rtl_sha256": sha((ROOT / (NEW + ".sv")).read_bytes()),
        "holdouts": "SEALED",
        "gpu_performance_claim": False,
    }
    (OUT / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    print("V296_FIXED_WORD_POSTCTS_STRONG_CONTROL_GENERATED")


def self_test():
    t = (
        "sha256sum research/v296/v296_tile_slice_bank_decode.sv\n"
        "src=research/v296/v296_tile_slice_bank_decode.sv\n"
        "hierarchy -top v296_tile_slice_bank_decode\n"
        "synth -top v296_tile_slice_bank_decode\n"
        'V296_TOP="v296_tile_slice_bank_decode"\n'
        "serial_onehot) param=0; extra=1\n"
        'V296_CONTROL_EXTRA="$extra"\n'
        "python3 research/v296/audit_tile_slice.py --single\n"
        "V296_DECODED_POSTCTS_EXTRACTED_COMPLETE\n"
        "V296_PLACE_DENSITY=0.45\n"
    )
    out = derive(t)
    assert out.count(NEW) == 5 and OLD not in out
    for broken in (t.replace("extra=1", "extra=0"),
                   t.replace("V296_PLACE_DENSITY=0.45", ""),
                   t + OLD,
                   t.replace("V296_DECODED_POSTCTS_EXTRACTED_COMPLETE", "")):
        try:
            derive(broken)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe post-CTS input accepted")
    print("V296_FIXED_WORD_POSTCTS_GENERATOR_SELFTEST_PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--build", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.build:
        build()
    if not (args.self_test or args.build):
        ap.error("Choose --self-test or --build")
