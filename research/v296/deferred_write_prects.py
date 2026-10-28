#!/usr/bin/env python3
"""Fail-closed, same-depth V296 deferred-write matched pre-CTS discriminator.

Derive the existing D4/D8 deep-bank physical runner and stop its unchanged
3.5 ns, 2x estimated-RC physical flow just before CTS. Keep the optimized
fifth-stage serial control. NOT post-CTS, routed, extracted-RC or signoff.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import deep_bank_postcts

OUT = Path("build/v296/tile_slice")
ROOT = Path("research/v296")
OLD = "v296_tile_slice_deep_bank"
NEW = "v296_tile_slice_deferred_write"
SOURCE = "run_deep_bank_hold25_postcts.sh"
TARGET = "run_deferred_prects.sh"
TCL_SOURCE = "cts45_hold25_tile.tcl"
TCL_TARGET = "cts45_deferred_prects.tcl"
MANIFEST = "deferred_prects_manifest.json"
STOP = 'puts "V296_CTS45_CTS_BEGIN"'
PREREG = "research/v296/DEFERRED_WRITE_MATCHED_PRECTS_PREREG_20261028.md"

DIAG = r'''
puts "V296_DEFERRED_PRECTS_TIER GLOBAL_ROUTE_ESTIMATED_RC_NOT_SIGNOFF"
puts "V296_DEFERRED_PRECTS_AREA_UM2 [expr {[rsz::design_area] * 1.0e12}]"
puts "V296_DEFERRED_PRECTS_CAP_COUNT [sta::max_capacitance_violation_count]"
puts "V296_DEFERRED_PRECTS_SLEW_COUNT [sta::max_slew_violation_count]"
puts "V296_DEFERRED_PRECTS_SETUP_BEGIN"
report_worst_slack -max -digits 6
puts "V296_DEFERRED_PRECTS_SETUP_END"
puts "V296_DEFERRED_PRECTS_PATHS_BEGIN"
report_checks -path_delay max -fields {slew capacitance fanout} -digits 6
puts "V296_DEFERRED_PRECTS_PATHS_END"
write_def "$env(V296_OUT).deferred_prects.def"
puts "V296_DEFERRED_PRECTS_DONE"
'''


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def derive_tcl(tcl):
    if tcl.count(STOP) != 1:
        raise ValueError("Missing/ambiguous frozen pre-CTS stop")
    prefix = tcl.split(STOP, 1)[0]
    required = (
        'if {$env(V296_CONTROL_EXTRA) eq "1"}',
        "V296_CTS45_FIFTH_DONE",
        "V296_CTS45_PRECTS_AREA_UM2",
        "V296_CTS45_EXTRA_REPAIR",
        "V296_CTS45_FOURTH_DONE",
        "V296_PLACE_DENSITY",
        "V296_RC_SCALE",
        "V296_DETAIL_RC_MULTIPLIER",
    )
    if any(a not in prefix for a in required):
        raise ValueError("Lost pre-CTS physical/fifth-stage anchors")
    if any(a in prefix for a in (
        "clock_tree_synthesis", "detailed_route -output_drc",
        "extract_parasitics -ext_model_file", "set_propagated_clock",
    )):
        raise ValueError("Pre-CTS prefix includes CTS/route/signoff")
    return prefix + DIAG


def derive_runner(runner):
    if runner.count(OLD) != 5 or NEW in runner:
        raise ValueError("Unexpected source/top count or mixed RTL")
    for anchor in (
        'serial_onehot) param=0; extra=1',
        'V296_CONTROL_EXTRA="$extra"',
        'V296_PLACE_DENSITY=0.45',
        '-chparam WORD_BITS $bits',
        '"$root/cts45_hold25_tile.tcl"',
        'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?',
        'V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE',
    ):
        if runner.count(anchor) != 1:
            raise ValueError("Missing/ambiguous symmetric physical anchor: " + anchor)
    result = runner.replace(OLD, NEW)
    result = result.replace(
        '"$root/cts45_hold25_tile.tcl"',
        '"$root/cts45_deferred_prects.tcl"')
    result = result.replace(
        'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?',
        'test -s "$root/$variant.high.deferred_prects.def" || audit_rc=$?')
    result = result.replace(
        "V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE",
        "V296_DEFERRED_PRECTS_ESTIMATED_COMPLETE")
    if OLD in result or result.count(NEW) != 5:
        raise ValueError("Unsafe mixed source/RTL")
    return result


def build(bits):
    if bits not in (2, 3):
        raise ValueError("Only frozen D4/D8 are supported")
    deep_bank_postcts.build(bits)
    original = (OUT / SOURCE).read_text()
    tcl = (OUT / TCL_SOURCE).read_text()
    runner = derive_runner(original)
    diag = derive_tcl(tcl)
    (OUT / TARGET).write_text(runner)
    (OUT / TCL_TARGET).write_text(diag)
    manifest = {
        "preregistration": PREREG, "bits": bits, "depth": 1 << bits,
        "architecture": "V296_PAIRWISE_ADMISSION_ONLY",
        "control": "V295_SERIAL_FIFTH_STAGE",
        "clock_ns": 3.5, "rc_multiplier": 2.0, "density": 0.45,
        "banks": 16, "ports_per_bank": 2, "global_write_ports": 1,
        "holdouts": "SEALED", "evidence": "PRECTS_ESTIMATED_RC_ONLY",
        "source_runner_sha256": sha(original),
        "derived_runner_sha256": sha(runner),
        "source_tcl_sha256": sha(tcl),
        "derived_tcl_sha256": sha(diag),
        "deferred_rtl_sha256": sha((ROOT / (NEW + ".sv")).read_bytes()),
    }
    (OUT / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("V296_DEFERRED_PRECTS_DERIVED depth=" + str(1 << bits))


def parse_log(log, variant):
    if log.count("V296_DEFERRED_PRECTS_DONE") != 1:
        raise ValueError("Missing or duplicate complete pre-CTS marker")
    extra = "0" if variant == "pairwise" else "1"
    if log.count("V296_CTS45_EXTRA_REPAIR " + extra) != 1:
        raise ValueError("Missing correct fifth-stage serial marker")
    if variant == "serial_onehot" and log.count("V296_CTS45_FIFTH_DONE") != 1:
        raise ValueError("Strong serial fifth stage absent")
    if variant == "pairwise" and "V296_CTS45_FIFTH_DONE" in log:
        raise ValueError("Unexpected candidate-only fifth stage")
    def number(key):
        hits = re.findall(r"^" + re.escape(key) + r"\s+([-+]?\d+(?:\.\d+)?)\s*$", log, re.M)
        if len(hits) != 1:
            raise ValueError("Missing or duplicate numeric metric " + key)
        return float(hits[0])
    area = number("V296_DEFERRED_PRECTS_AREA_UM2")
    cap = number("V296_DEFERRED_PRECTS_CAP_COUNT")
    slew = number("V296_DEFERRED_PRECTS_SLEW_COUNT")
    segment = log.split("V296_DEFERRED_PRECTS_SETUP_BEGIN", 1)
    if len(segment) != 2 or segment[1].count("V296_DEFERRED_PRECTS_SETUP_END") != 1:
        raise ValueError("Missing or ambiguous setup block")
    setup = segment[1].split("V296_DEFERRED_PRECTS_SETUP_END", 1)[0]
    hits = re.findall(r"worst slack\s+([-+]?\d+(?:\.\d+)?)", setup, re.I)
    if len(hits) != 1:
        raise ValueError("Missing worst setup slack")
    slack = float(hits[0])
    if not (0 < area < 100000 and -100 < slack < 100 and
            cap >= 0 and int(cap) == cap and slew >= 0 and int(slew) == slew):
        raise ValueError("Nonphysical metric")
    return {"area_um2": area, "setup_slack_ns": slack,
            "cap_violations": int(cap), "slew_violations": int(slew),
            "prects_plausible": slack >= .05 and area <= 30000 and cap == 0 and slew == 0}


def audit(bits):
    m = json.loads((OUT / MANIFEST).read_text())
    if (m["bits"] != bits or m["depth"] != 1 << bits or
        m["preregistration"] != PREREG or m["control"] != "V295_SERIAL_FIFTH_STAGE" or
        m["clock_ns"] != 3.5 or m["rc_multiplier"] != 2.0 or m["density"] != .45 or
        m["ports_per_bank"] != 2 or m["holdouts"] != "SEALED"):
        raise ValueError("Physical manifest mismatch")
    for name, key in ((SOURCE, "source_runner_sha256"), (TARGET, "derived_runner_sha256"),
                      (TCL_SOURCE, "source_tcl_sha256"), (TCL_TARGET, "derived_tcl_sha256")):
        if sha((OUT / name).read_bytes()) != m[key]:
            raise ValueError("Source/derived physical file hash mismatch " + name)
    if (derive_runner((OUT / SOURCE).read_text()) != (OUT / TARGET).read_text() or
        derive_tcl((OUT / TCL_SOURCE).read_text()) != (OUT / TCL_TARGET).read_text()):
        raise ValueError("Derived physical source differs from generator")
    if sha((ROOT / (NEW + ".sv")).read_bytes()) != m["deferred_rtl_sha256"]:
        raise ValueError("RTL provenance mismatch")
    rows = {}
    for variant in ("pairwise", "serial_onehot"):
        try:
            exit_marker = (OUT / (variant + ".deferred_prects.exit.txt")).read_text().strip()
            if exit_marker != "EXIT_CODE=0":
                raise ValueError("Physical runner failed or timed out: " + exit_marker)
            log = (OUT / (variant + ".high.log")).read_text()
            rows[variant] = parse_log(log, variant)
            source_hashes = (OUT / (variant + ".inputs.sha256")).read_text()
            if m["deferred_rtl_sha256"] + "  " + str(ROOT / (NEW + ".sv")) not in source_hashes:
                raise ValueError("RTL hash missing from original runner")
            if m["derived_tcl_sha256"] + "  " + str(OUT / TCL_TARGET) not in source_hashes:
                raise ValueError("Derived Tcl hash missing from original runner")
        except (ValueError, OSError) as exc:
            rows[variant] = {"prects_plausible": False, "error": str(exc)}
    matched = all(rows[v]["prects_plausible"] for v in rows)
    area_delta = (rows["serial_onehot"]["area_um2"] - rows["pairwise"]["area_um2"]
                  if matched else None)
    result = {"depth": 1 << bits, "rows": rows,
              "matched_prects_plausible": matched,
              "matched_area_saving_um2": area_delta,
              "verdict": ("PRECTS_PLAUSIBLE_NOT_SIGNOFF" if matched else
                          "PRECTS_INFEASIBLE_OR_CENSORED"),
              "tier": "PRECTS_GLOBAL_ROUTE_ESTIMATED_RC_NOT_SIGNOFF",
              "holdouts": "SEALED", "gpu_advantage": False}
    (OUT / ("deferred_prects_d%d_audit.json" % (1 << bits))).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not matched:
        raise SystemExit(3)


def self_test():
    base = ('V296_CTS45_FOURTH_DONE\n'
            'if {$env(V296_CONTROL_EXTRA) eq "1"} {\n'
            'puts "V296_CTS45_FIFTH_DONE"\n}\n'
            'puts "V296_CTS45_PRECTS_AREA_UM2 $pre_cts_area"\n'
            'puts "V296_CTS45_EXTRA_REPAIR $env(V296_CONTROL_EXTRA)"\n'
            'puts "$env(V296_PLACE_DENSITY) $env(V296_RC_SCALE) $env(V296_DETAIL_RC_MULTIPLIER)"\n'
            + STOP + '\nclock_tree_synthesis\n')
    assert "clock_tree_synthesis" not in derive_tcl(base)
    assert "-group_path_count" not in DIAG
    assert "report_checks -path_delay max -fields" in DIAG
    fake = ('sha256sum research/v296/v296_tile_slice_deep_bank.sv\n'
            'src=research/v296/v296_tile_slice_deep_bank.sv\n'
            'hierarchy -top v296_tile_slice_deep_bank -chparam WORD_BITS $bits\n'
            'synth -top v296_tile_slice_deep_bank\n'
            'V296_TOP="v296_tile_slice_deep_bank"\n'
            'serial_onehot) param=0; extra=1\n'
            'V296_CONTROL_EXTRA="$extra"\n'
            'V296_PLACE_DENSITY=0.45\n'
            '"$root/cts45_hold25_tile.tcl"\n'
            'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?\n'
            'V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE\n')
    transformed = derive_runner(fake)
    assert transformed.count(NEW) == 5 and OLD not in transformed
    for bad in (fake.replace("extra=1", "extra=0"),
                fake.replace("V296_PLACE_DENSITY=0.45", ""),
                fake + OLD):
        try:
            derive_runner(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe runner accepted")
    for bad in (base.replace(STOP, ""), base.replace("V296_CTS45_FIFTH_DONE", "")):
        try:
            derive_tcl(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe Tcl accepted")
    good = ("V296_CTS45_EXTRA_REPAIR 0\nV296_DEFERRED_PRECTS_DONE\n"
            "V296_DEFERRED_PRECTS_AREA_UM2 100\n"
            "V296_DEFERRED_PRECTS_CAP_COUNT 0\nV296_DEFERRED_PRECTS_SLEW_COUNT 0\n"
            "V296_DEFERRED_PRECTS_SETUP_BEGIN\nworst slack 0.100000\n"
            "V296_DEFERRED_PRECTS_SETUP_END\n")
    assert parse_log(good, "pairwise")["prects_plausible"]
    for bad in (good.replace("0.100000", "-0.100000"),
                good.replace("V296_DEFERRED_PRECTS_DONE", ""),
                good.replace("CAP_COUNT 0", "CAP_COUNT 2")):
        try:
            result = parse_log(bad, "pairwise")
            assert not result["prects_plausible"]
        except ValueError:
            pass
    print("V296_DEFERRED_PRECTS_DERIVATION_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    p.add_argument("--audit", action="store_true")
    p.add_argument("--word-bits", type=int, default=2)
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.build:
        build(a.word_bits)
    if a.audit:
        audit(a.word_bits)
    if not (a.self_test or a.build or a.audit):
        p.error("Select mode")


if __name__ == "__main__":
    main()
