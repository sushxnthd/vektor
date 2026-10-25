#!/usr/bin/env python3
"""Fail-closed generation of a matched V296 RF-slice physical experiment.

The frozen controller CTS protocol is copied, not modified. Only the floorplan
anchor and two source paths are changed; both contestants consume the SAME Tcl.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path("research/v296")
OUT = Path("build/v296/tile_slice")
ORIGINAL = (
    "cap_margin_repair.tcl", "cap_margin_third.tcl", "cts45_setup250.tcl")
OLD_FLOOR = ("initialize_floorplan -die_area {0 0 140 140} "
             "-core_area {10 10 130 130} -site FreePDK45_38x28_10R_NP_162NW_34O")
NEW_FLOOR = ("initialize_floorplan -die_area {0 0 260 260} "
             "-core_area {10 10 250 250} -site FreePDK45_38x28_10R_NP_162NW_34O")


def replace_once(source, before, after):
    if source.count(before) != 1:
        raise ValueError("Frozen source anchor changed or ambiguous: " + before)
    return source.replace(before, after)


def generate():
    src = {name: (ROOT / name).read_text() for name in ORIGINAL}
    tile_repair = replace_once(
        src["cap_margin_repair.tcl"], OLD_FLOOR,
        NEW_FLOOR + '\nputs "V296_TILE_SLICE_FLOORPLAN die260_core240"')
    tile_third = replace_once(
        src["cap_margin_third.tcl"],
        "source research/v296/cap_margin_repair.tcl",
        f"source {OUT}/cap_margin_repair_tile.tcl")
    tile_cts = replace_once(
        src["cts45_setup250.tcl"],
        "source research/v296/cap_margin_third.tcl",
        f"source {OUT}/cap_margin_third_tile.tcl")
    generated = {
        "cap_margin_repair_tile.tcl": tile_repair,
        "cap_margin_third_tile.tcl": tile_third,
        "cts45_tile.tcl": tile_cts,
    }
    if "repair_timing -setup -slack_margin 0.250" not in tile_cts:
        raise ValueError("Lost frozen setup250 policy")
    if "set_max_fanout 16 [current_design]" not in tile_cts:
        raise ValueError("Lost frozen fanout policy")
    if "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0" not in tile_cts:
        raise ValueError("Lost frozen extracted RC policy")
    if "global_placement -density $env(V296_PLACE_DENSITY)" not in tile_repair:
        raise ValueError("Lost matched density policy")
    return src, generated


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def build():
    src, generated = generate()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in generated.items():
        (OUT / name).write_text(data)
    manifest = {
        "preregistration": "research/v296/TILE_SLICE_PHYSICAL_PREREG_20261025.md",
        "die_um": 260, "core_um": 240, "same_tcl_for_both": True,
        "source_sha256": {name: sha(data) for name, data in src.items()},
        "generated_sha256": {name: sha(data) for name, data in generated.items()},
    }
    (OUT / "tile_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("V296_TILE_SLICE_GENERATED_SAME_CONSTRAINTS")


def self_test():
    src, gen = generate()
    assert OLD_FLOOR not in gen["cap_margin_repair_tile.tcl"]
    assert gen["cap_margin_repair_tile.tcl"].count(NEW_FLOOR) == 1
    assert gen["cap_margin_repair_tile.tcl"].count("V296_TILE_SLICE_FLOORPLAN") == 1
    for original in ORIGINAL:
        assert src[original]
    for source, before in (
        ("x", OLD_FLOOR), (OLD_FLOOR + OLD_FLOOR, OLD_FLOOR)):
        try:
            replace_once(source, before, NEW_FLOOR)
        except ValueError:
            pass
        else:
            raise AssertionError("Fail-open source replacement")
    print("V296_TILE_SLICE_GENERATOR_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.build:
        build()
    if not (a.self_test or a.build):
        p.error("Specify --self-test and/or --build")
