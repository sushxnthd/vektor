#!/usr/bin/env python3
"""Prospective V296 deferred-write D4/D8 *routed* extracted-RC discriminator.

Derive the frozen same-depth strong-control route, change only the common RTL
source/top and the completion marker. A completed workflow is NOT signoff.
"""
import argparse
import hashlib
import json
from pathlib import Path

import deep_bank_postcts
import audit_tile_slice

ROOT = Path("research/v296")
OUT = Path("build/v296/tile_slice")
OLD = "v296_tile_slice_deep_bank"
NEW = "v296_tile_slice_deferred_write"
SRC = "run_deep_bank_hold25_postcts.sh"
DST = "run_deferred_routed.sh"
TCL = "cts45_hold25_tile.tcl"
MANIFEST = "deferred_routed_manifest.json"
PREREG = "research/v296/DEFERRED_WRITE_MATCHED_ROUTED_PREREG_20261028.md"
VARIANTS = ("pairwise", "serial_onehot")


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def derive(runner, tcl):
    if runner.count(OLD) != 5 or NEW in runner:
        raise ValueError("Unexpected frozen RTL source/top references")
    for a in (
        'serial_onehot) param=0; extra=1',
        'V296_CONTROL_EXTRA="$extra"',
        'V296_PLACE_DENSITY=0.45',
        '-chparam WORD_BITS $bits',
        '"$root/cts45_hold25_tile.tcl"',
        'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?',
        'V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE',
    ):
        if runner.count(a) != 1:
            raise ValueError("Missing or ambiguous physical runner anchor " + a)
    for a in (
        "clock_tree_synthesis", "detailed_route -output_drc",
        "extract_parasitics -ext_model_file",
        "set_propagated_clock", "repair_timing -hold -slack_margin 0.025",
        "repair_timing -setup -slack_margin 0.250",
        "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0",
        'if {$env(V296_CONTROL_EXTRA) eq "1"}',
    ):
        if a not in tcl:
            raise ValueError("Missing frozen route/strong-control policy " + a)
    transformed = runner.replace(OLD, NEW).replace(
        "V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE",
        "V296_DEFERRED_ROUTED_EXTRACTED_COMPLETE")
    if OLD in transformed or transformed.count(NEW) != 5:
        raise ValueError("Mixed physical RTL source")
    return transformed


def build(bits):
    if bits not in (2, 3):
        raise ValueError("Only preregistered D4/D8 depths")
    deep_bank_postcts.build(bits)
    original = (OUT / SRC).read_text()
    tcl = (OUT / TCL).read_text()
    derived = derive(original, tcl)
    (OUT / DST).write_text(derived)
    manifest = {
        "preregistration": PREREG,
        "depth": 1 << bits, "bits": bits,
        "sole_mechanism": "V296_PAIRWISE_BANK_CONFLICT_ADMISSION",
        "control": "V295_OPTIMIZED_SERIAL_FIFTH_STAGE",
        "banks": 16, "read_ports_per_bank": 2, "global_write_ports": 1,
        "clock_ns": 3.5, "rc_multiplier": 2.0, "density": 0.45,
        "hold_margin_ns": 0.025, "setup_guard_ns": 0.050,
        "area_ceiling_um2": 30000, "min_area_saving": 0.01,
        "min_setup_lead_ns": 0.050,
        "source_runner_sha256": sha(original),
        "derived_runner_sha256": sha(derived),
        "unchanged_route_tcl_sha256": sha(tcl),
        "deferred_rtl_sha256": sha((ROOT / (NEW + ".sv")).read_bytes()),
        "holdouts": "SEALED",
        "evidence_tier": "ROUTED_EXTRACTED_RC_PENDING",
        "gpu_performance_claim": False,
    }
    (OUT / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("V296_DEFERRED_ROUTED_FROZEN depth=" + str(1 << bits))


def audit(bits):
    m = json.loads((OUT / MANIFEST).read_text())
    if (m["preregistration"] != PREREG or m["bits"] != bits
            or m["depth"] != 1 << bits or m["control"] != "V295_OPTIMIZED_SERIAL_FIFTH_STAGE"
            or m["clock_ns"] != 3.5 or m["rc_multiplier"] != 2.0
            or m["density"] != 0.45 or m["hold_margin_ns"] != 0.025
            or m["read_ports_per_bank"] != 2 or m["holdouts"] != "SEALED"):
        raise ValueError("Frozen routed protocol mismatch")
    for filename, field in ((SRC, "source_runner_sha256"),
                            (DST, "derived_runner_sha256"),
                            (TCL, "unchanged_route_tcl_sha256")):
        if sha((OUT / filename).read_bytes()) != m[field]:
            raise ValueError("Physical source/Tcl changed: " + filename)
    if (OUT / DST).read_text() != derive((OUT / SRC).read_text(),
                                        (OUT / TCL).read_text()):
        raise ValueError("Derived route is not a pure symmetric substitution")
    if sha((ROOT / (NEW + ".sv")).read_bytes()) != m["deferred_rtl_sha256"]:
        raise ValueError("Deferred RTL source changed")
    rows = {}
    for variant, extra in (("pairwise", "0"), ("serial_onehot", "1")):
        try:
            exitcode = (OUT / (variant + ".deferred_routed.exit.txt")).read_text().strip()
            if exitcode != "EXIT_CODE=0":
                raise ValueError("Incomplete/failed/timeout routed run: " + exitcode)
            log = (OUT / (variant + ".high.log")).read_text(errors="replace")
            if log.splitlines().count("V296_HOLD25_MARGIN_NS 0.025") != 1:
                raise ValueError("Hold25 repair marker absent/duplicate")
            if log.splitlines().count("V296_CTS45_EXTRA_REPAIR " + extra) != 1:
                raise ValueError("Serial fifth-stage control policy violated")
            if variant == "serial_onehot" and log.splitlines().count("V296_CTS45_FIFTH_DONE") != 1:
                raise ValueError("Strongest serial fifth stage missing")
            hashes = (OUT / (variant + ".inputs.sha256")).read_text()
            for field, path in (
                ("deferred_rtl_sha256", ROOT / (NEW + ".sv")),
                ("unchanged_route_tcl_sha256", OUT / TCL),
            ):
                if m[field] + "  " + str(path) not in hashes:
                    raise ValueError("Actual executed inputs not SHA-pinned: " + field)
            rows[variant] = audit_tile_slice.case(OUT, variant)
        except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
            rows[variant] = {"complete": False, "error": str(exc)}
    verdict, comparison = audit_tile_slice.decision(rows)
    result = {
        "depth": 1 << bits, "decision": verdict, "comparison": comparison,
        "rows": rows, "evidence_tier": "MATCHED_ROUTED_EXTRACTED_RC_IF_COMPLETE",
        "preregistered_prediction": "WIN" if bits == 2 else "NO_WIN",
        "prediction_correct": ((verdict == "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU")
                               == (bits == 2)),
        "holdouts": "SEALED", "gpu_throughput": "NOT_ESTABLISHED",
        "production_macro_signoff": False,
    }
    (OUT / ("aggregate.deferred_routed_bits%d.json" % bits)).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if verdict != "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)


def self_test():
    r = (
        "sha256sum research/v296/v296_tile_slice_deep_bank.sv\n"
        "src=research/v296/v296_tile_slice_deep_bank.sv\n"
        "hierarchy -top v296_tile_slice_deep_bank -chparam WORD_BITS $bits\n"
        "synth -top v296_tile_slice_deep_bank\n"
        'V296_TOP="v296_tile_slice_deep_bank"\n'
        'serial_onehot) param=0; extra=1\n'
        'V296_CONTROL_EXTRA="$extra"\n'
        'V296_PLACE_DENSITY=0.45\n'
        '"$root/cts45_hold25_tile.tcl"\n'
        'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?\n'
        'V296_DEEP_BANK_POSTCTS_EXTRACTED_COMPLETE\n')
    t = ("clock_tree_synthesis\ndetailed_route -output_drc\n"
         "extract_parasitics -ext_model_file\nset_propagated_clock\n"
         "repair_timing -hold -slack_margin 0.025\n"
         "repair_timing -setup -slack_margin 0.250\n"
         "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0\n"
         'if {$env(V296_CONTROL_EXTRA) eq "1"}\n')
    good = derive(r, t)
    assert good.count(NEW) == 5 and OLD not in good
    for a,b in ((r.replace("extra=1","extra=0"),t),
                (r,t.replace("detailed_route -output_drc","")),
                (r + OLD,t),
                (r,t.replace("repair_timing -hold -slack_margin 0.025",""))):
        try:
            derive(a,b)
        except ValueError:
            continue
        raise AssertionError("Unsafe physical variant accepted")
    print("V296_DEFERRED_ROUTED_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    p.add_argument("--audit", action="store_true")
    p.add_argument("--word-bits", type=int, default=2)
    a = p.parse_args()
    if a.self_test: self_test()
    if a.build: build(a.word_bits)
    if a.audit: audit(a.word_bits)
    if not (a.self_test or a.build or a.audit): p.error("Choose mode")
