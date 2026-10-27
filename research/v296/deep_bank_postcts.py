#!/usr/bin/env python3
"""Prospective D4/D8 matched dynamic two-port RF extracted-RC transfer.

Derives only a depth parameter and the shared RTL top from the already
frozen symmetric hold25 physical runner. No physical Tcl or baseline changes.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fixed_word_hold25
import audit_tile_slice

ROOT = Path("research/v296")
OUT = Path("build/v296/tile_slice")
OLD = "v296_tile_slice_fixed_word"
NEW = "v296_tile_slice_deep_bank"
SOURCE = "run_fixed_word_hold25_postcts.sh"
TARGET = "run_deep_bank_hold25_postcts.sh"
MANIFEST = "deep_bank_hold25_manifest.json"
PREREG = "research/v296/DEEP_BANK_D4_D8_ROUTED_PREREG_20261027.md"
VARIANTS = ("pairwise", "serial_onehot")


def sha(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def derive(runner):
    if runner.count(OLD) != 5 or NEW in runner:
        raise ValueError("Mixed or unexpected fixed-word RTL references")
    for anchor in (
        'variant="$V296_TILE_VARIANT"\n',
        "serial_onehot) param=0; extra=1",
        'V296_CONTROL_EXTRA="$extra"',
        'V296_TOP="v296_tile_slice_fixed_word"',
        '"$root/cts45_hold25_tile.tcl"',
        "V296_FIXED_WORD_POSTCTS_EXTRACTED_COMPLETE",
    ):
        if runner.count(anchor) != 1:
            raise ValueError("Missing/ambiguous frozen physical anchor: " + anchor)
    out = runner.replace(OLD, NEW)
    anchor = 'variant="$V296_TILE_VARIANT"\n'
    out = out.replace(anchor, anchor +
        ': "$V296_DEEP_WORD_BITS"\n'
        'bits="$V296_DEEP_WORD_BITS"\n'
        'case "$bits" in 2|3) ;; *) echo INVALID_DEEP_BANK_BITS; exit 2 ;; esac\n')
    old_h = "hierarchy -top v296_tile_slice_deep_bank -chparam PAIRWISE $param;"
    if out.count(old_h) != 1:
        raise ValueError("Unmatched Yosys parameter anchor")
    out = out.replace(old_h,
        "hierarchy -top v296_tile_slice_deep_bank -chparam PAIRWISE $param -chparam WORD_BITS $bits;")
    out = out.replace("V296_FIXED_WORD_POSTCTS_EXTRACTED_COMPLETE",
                      "V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE")
    if OLD in out or out.count(NEW) != 5 or out.count("-chparam WORD_BITS $bits") != 1:
        raise ValueError("Unsafe mixed RTL/depth implementation")
    return out


def build(bits):
    if bits not in (2, 3):
        raise ValueError("Only prospectively frozen D4/D8 are eligible")
    fixed_word_hold25.build()
    source = (OUT / SOURCE).read_text()
    result = derive(source)
    (OUT / TARGET).write_text(result)
    tcl = (OUT / "cts45_hold25_tile.tcl").read_text()
    for required in (
        "clock_tree_synthesis", "detailed_route -output_drc",
        "extract_parasitics -ext_model_file",
        "repair_timing -hold -slack_margin 0.025",
        "repair_timing -setup -slack_margin 0.250",
        "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0",
        'if {$env(V296_CONTROL_EXTRA) eq "1"}',
    ):
        if required not in tcl:
            raise ValueError("Frozen physical requirement missing: " + required)
    m = {
        "preregistration": PREREG,
        "architecture": "V296_PAIRWISE_BANK_ADMISSION_ONLY",
        "word_bits": bits,
        "depth": 1 << bits,
        "banks": 16, "read_ports_per_bank": 2, "global_write_ports": 1,
        "strongest_serial_fifth_stage": True,
        "symmetric_hold_margin_ns": 0.025,
        "clock_ns": 3.5, "rc_multiplier": 2.0,
        "place_density": 0.45,
        "source_runner_sha256": sha(source),
        "derived_runner_sha256": sha(result),
        "frozen_hold25_tcl_sha256": sha(tcl),
        "dynamic_rtl_sha256": sha((ROOT / (NEW + ".sv")).read_bytes()),
        "holdouts": "SEALED",
        "evidence_tier": "ROUTED_EXTRACTED_RC_PENDING",
        "gpu_speedup_claim": False,
    }
    (OUT / MANIFEST).write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    print("V296_DYNAMIC_DEEP_BANK_HOLD25_FROZEN depth=" + str(1 << bits))


def audit(bits):
    root = OUT
    m = json.loads((root / MANIFEST).read_text())
    if (m["word_bits"] != bits or m["depth"] != 1 << bits
            or m["preregistration"] != PREREG
            or m["architecture"] != "V296_PAIRWISE_BANK_ADMISSION_ONLY"
            or m["banks"] != 16 or m["read_ports_per_bank"] != 2
            or m["global_write_ports"] != 1
            or m["clock_ns"] != 3.5 or m["rc_multiplier"] != 2.0
            or m["place_density"] != 0.45
            or m["symmetric_hold_margin_ns"] != 0.025
            or m["strongest_serial_fifth_stage"] is not True
            or m["holdouts"] != "SEALED"):
        raise ValueError("Manifest protocol mismatch")
    for name, key in (
        (SOURCE, "source_runner_sha256"),
        (TARGET, "derived_runner_sha256"),
        ("cts45_hold25_tile.tcl", "frozen_hold25_tcl_sha256"),
    ):
        if sha((root / name).read_bytes()) != m[key]:
            raise ValueError("Modified physical source: " + name)
    if (root / TARGET).read_text() != derive((root / SOURCE).read_text()):
        raise ValueError("Derived physical runner differs from frozen source")
    if sha((ROOT / (NEW + ".sv")).read_bytes()) != m["dynamic_rtl_sha256"]:
        raise ValueError("Dynamic RTL changed")
    rows = {}
    for variant, extra in (("pairwise", "0"), ("serial_onehot", "1")):
        try:
            log = (root / (variant + ".high.log")).read_text(errors="replace")
            if log.splitlines().count("V296_HOLD25_MARGIN_NS 0.025") != 1:
                raise ValueError("Hold repair not executed")
            if log.splitlines().count("V296_CTS45_EXTRA_REPAIR " + extra) != 1:
                raise ValueError("Wrong fifth-stage serial repair")
            marker = (root / (variant + ".deep_bank.exit.txt")).read_text()
            if "EXIT_CODE=0" not in marker:
                raise ValueError("Physical execution failed or timed out")
            hashes = (root / (variant + ".inputs.sha256")).read_text()
            if m["dynamic_rtl_sha256"] + "  " + str(ROOT / (NEW + ".sv")) not in hashes:
                raise ValueError("Wrong dynamic RTL in physical execution")
            if m["frozen_hold25_tcl_sha256"] + "  " + str(root / "cts45_hold25_tile.tcl") not in hashes:
                raise ValueError("Wrong physical Tcl in physical execution")
            rows[variant] = audit_tile_slice.case(root, variant)
        except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    decision, comparison = audit_tile_slice.decision(rows)
    output = {
        "decision": decision, "comparison": comparison, "rows": rows,
        "depth": 1 << bits,
        "evidence_tier": "ROUTED_EXTRACTED_RC_IF_COMPLETE",
        "both_feasible_required": True,
        "same_clock_admission_gain": 0,
        "production_gpu_speedup": "NOT_ESTABLISHED",
        "holdouts": "SEALED",
    }
    path = root / ("aggregate.deep_bank_bits%d.json" % bits)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"depth": 1 << bits, "decision": decision,
                      "comparison": comparison, "rows": rows}, indent=2))
    if decision != "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)


def self_test():
    fake = (
        "sha256sum research/v296/v296_tile_slice_fixed_word.sv\n"
        'src="research/v296/v296_tile_slice_fixed_word.sv"\n'
        "hierarchy -top v296_tile_slice_fixed_word -chparam PAIRWISE $param;\n"
        "synth -top v296_tile_slice_fixed_word -flatten\n"
        'V296_TOP="v296_tile_slice_fixed_word"\n'
        'variant="$V296_TILE_VARIANT"\n'
        "serial_onehot) param=0; extra=1\n"
        'V296_CONTROL_EXTRA="$extra"\n'
        '"$root/cts45_hold25_tile.tcl"\n'
        "V296_FIXED_WORD_POSTCTS_EXTRACTED_COMPLETE\n"
    )
    result = derive(fake)
    assert result.count(NEW) == 5 and OLD not in result
    assert result.count("-chparam WORD_BITS $bits") == 1
    for bad in (fake.replace("extra=1", "extra=0"),
                fake.replace('"$root/cts45_hold25_tile.tcl"', ""),
                fake + "synth -top v296_tile_slice_fixed_word",
                fake.replace("V296_FIXED_WORD_POSTCTS_EXTRACTED_COMPLETE", "")):
        try:
            derive(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe physical transformation accepted")
    print("V296_DEEP_BANK_POSTCTS_DERIVATION_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    p.add_argument("--audit", action="store_true")
    p.add_argument("--word-bits", type=int, default=2)
    args = p.parse_args()
    if args.self_test:
        self_test()
    if args.build:
        build(args.word_bits)
    if args.audit:
        audit(args.word_bits)
    if not (args.self_test or args.build or args.audit):
        p.error("Choose --self-test, --build or --audit")


if __name__ == "__main__":
    main()
