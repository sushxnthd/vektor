#!/usr/bin/env python3
"""Derive matched fixed-word pre-CTS trial without changing frozen physical Tcl."""
import argparse
import hashlib
import json
from pathlib import Path
import bank_decode_pre_cts

OUT = Path("build/v296/tile_slice")
OLD = "v296_tile_slice_bank_decode"
NEW = "v296_tile_slice_fixed_word"

def derive_runner(src):
    if src.count(OLD) < 4 or NEW in src:
        raise ValueError("Missing or contaminated decoded runner")
    out = src.replace(OLD, NEW)
    for anchor in ("research/v296/" + NEW + ".sv",
                   "hierarchy -top " + NEW,
                   'V296_TOP="' + NEW + '"',
                   "cts45_fourth_diag.tcl",
                   "V296_FOURTH_CONE_NO_SIGNOFF"):
        if anchor not in out:
            raise ValueError("Missing physical invariant " + anchor)
    if OLD in out:
        raise ValueError("Mixed physical top modules")
    return out

def build():
    bank_decode_pre_cts.build()
    src = (OUT / "run_bank_decode_fourth.sh").read_text()
    dst = derive_runner(src)
    (OUT / "run_fixed_word_fourth.sh").write_text(dst)
    (OUT / "fixed_word_manifest.json").write_text(json.dumps({
        "preregistration": "research/v296/FIXED_WORD_TWO_PORT_RF_CONE_PREREG_20261027.md",
        "evidence_tier": "PRECTS_ESTIMATED_ONLY_NOT_SIGNOFF",
        "both_contestants_same_two_port_rf": True,
        "serial_fifth_stage_excluded": True,
        "source_runner_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "fixed_runner_sha256": hashlib.sha256(dst.encode()).hexdigest(),
        "unchanged_fourth_tcl_sha256": hashlib.sha256(
            (OUT / "cts45_fourth_diag.tcl").read_bytes()).hexdigest()
    }, indent=2) + "\n")
    print("V296_FIXED_WORD_MATCHED_PRECTS_GENERATED")

def self_test():
    src = (
        "sha256sum research/v296/v296_tile_slice_bank_decode.sv\n"
        "src=research/v296/v296_tile_slice_bank_decode.sv\n"
        "hierarchy -top v296_tile_slice_bank_decode\n"
        'V296_TOP="v296_tile_slice_bank_decode"\n'
        "openroad cts45_fourth_diag.tcl\n"
        "echo V296_FOURTH_CONE_NO_SIGNOFF\n"
    )
    x = derive_runner(src)
    assert OLD not in x and x.count(NEW) == 4
    for bad in (src.replace("cts45_fourth_diag.tcl", ""), x,
                src.replace("hierarchy -top v296_tile_slice_bank_decode", "")):
        try:
            derive_runner(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe generator input accepted")
    print("V296_FIXED_WORD_GENERATOR_SELFTEST_PASS")

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
        p.error("Choose a test or build")
