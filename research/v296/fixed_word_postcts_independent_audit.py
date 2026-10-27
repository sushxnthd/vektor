#!/usr/bin/env python3
"""Fail-closed independent fixed-word extracted-RC provenance and signoff checker."""
import argparse
import hashlib
import json
from pathlib import Path
import audit_tile_slice

ROOT = Path("research/v296")
TOP = "v296_tile_slice_fixed_word"
VARIANTS = ("pairwise", "serial_onehot")
MANIFEST = "fixed_word_postcts_manifest.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(root, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown physical contestant")
    m = json.loads((root / MANIFEST).read_text())
    if not (m["rtl_top"] == TOP and m["same_rtl_for_both"]
            and m["strongest_serial_fifth_stage_required"]
            and m["candidate_extra_repair"] == 0 and m["serial_extra_repair"] == 1
            and m["clock_ns"] == 3.5 and m["rc_multiplier"] == 2.0
            and m["placement_density"] == 0.45
            and m["holdouts"] == "SEALED"):
        raise ValueError("Changed source/physical/serial control protocol")
    for filename, field in (
        ("run_fixed_word_postcts.sh", "derived_runner_sha256"),
        ("run_bank_decode_postcts.sh", "source_runner_sha256"),
        ("cts45_tile.tcl", "unchanged_physical_tcl_sha256"),
    ):
        if digest(root / filename) != m[field]:
            raise ValueError("Modified runner/Tcl: " + filename)
    if digest(ROOT / (TOP + ".sv")) != m["source_rtl_sha256"]:
        raise ValueError("RTL changed after frozen experiment")
    source = "research/v296/" + TOP + ".sv"
    inputs = (root / f"{variant}.inputs.sha256").read_text().splitlines()
    matches = [line.split()[0] for line in inputs if line.endswith("  " + source)]
    if matches != [m["source_rtl_sha256"]]:
        raise ValueError("Missing or mismatched RTL synthesis hash")
    if any(line.endswith("  research/v296/v296_tile_slice_bank_decode.sv")
           for line in inputs):
        raise ValueError("Decoded RTL leaked into fixed-word physical run")
    log = (root / f"{variant}.high.log").read_text(errors="replace")
    extra = "1" if variant == "serial_onehot" else "0"
    for marker in (
        "V296_CTS45_EXTRA_REPAIR " + extra,
        "V296_CTS45_CLOCKS_PROPAGATED 1",
        "V296_CTS45_RC_MULTIPLIER 2.0",
    ):
        if marker not in log:
            raise ValueError("Missing physical/strong-control evidence: " + marker)
    return m


def one(root, variant):
    verify(root, variant)
    row = audit_tile_slice.case(root, variant)
    return dict(variant=variant, complete=bool(row.get("complete")),
                feasible=bool(row.get("feasible")), physical=row,
                source_provenance="PASS")


def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = one(root, variant)
        except (ValueError, OSError, KeyError, IndexError, TypeError) as error:
            rows[variant] = dict(variant=variant, complete=False,
                                 feasible=False, error=str(error))
    if not all(rows[v].get("complete") for v in VARIANTS):
        verdict = "INCOMPLETE_OR_CENSORED_NO_CLAIM"
    elif not rows["pairwise"]["feasible"]:
        verdict = "FIXED_WORD_CANDIDATE_PHYSICAL_GATE_FAIL"
    elif not rows["serial_onehot"]["feasible"]:
        verdict = "STRONG_SERIAL_INFEASIBLE_NO_MATCHED_PARETO_CLAIM"
    else:
        p = rows["pairwise"]["physical"]["final"]
        s = rows["serial_onehot"]["physical"]["final"]
        area_saving = (s["area_um2"] - p["area_um2"]) / s["area_um2"]
        setup_lead = p["setup_ns"] - s["setup_ns"]
        verdict = ("BOTH_FEASIBLE_PARETO_SUPPORTED_NOT_GPU"
                   if area_saving >= .01 and setup_lead >= .050
                   else "MATCHED_PARETO_NOT_SUPPORTED")
    out = dict(verdict=verdict, rows=rows, source="FIXED_WORD_POSTCTS_STRONG_CONTROL",
               holdouts="SEALED", physical_gpu=False,
               measured_gpu_speedup=False, measured_power=False,
               realistic_deep_bank=False)
    root.mkdir(parents=True, exist_ok=True)
    (root / "aggregate.fixed_word_postcts.json").write_text(
        json.dumps(out, indent=2) + "\n")
    print(json.dumps({"verdict": verdict, "contestants": {
        v: {k: rows[v].get(k) for k in ("complete", "feasible", "error")}
        for v in VARIANTS}}, indent=2))
    if verdict != "BOTH_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)


def self_test():
    assert digest(ROOT / "fixed_word_postcts_independent_audit.py")
    assert set(VARIANTS) == {"pairwise", "serial_onehot"}
    try:
        verify(Path("/no/such/physical/artifact"), "unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid contestant accepted")
    print("V296_FIXED_WORD_POSTCTS_INDEPENDENT_SELFTEST_PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--single", nargs=2)
    ap.add_argument("--aggregate", type=Path)
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.single:
        print(json.dumps(one(Path(args.single[0]), args.single[1]), indent=2))
    if args.aggregate:
        aggregate(args.aggregate)
    if not (args.self_test or args.single or args.aggregate):
        ap.error("Choose --self-test, --single or --aggregate")
