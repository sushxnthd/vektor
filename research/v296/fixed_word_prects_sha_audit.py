#!/usr/bin/env python3
"""Fail-closed SHA-pinned V296 fixed-word pre-CTS paired physical audit."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

RUN = 40457696916
SHA = {
    "pairwise": "cebe917377f0a3195a43e9bdb3917a0b8036e198ed8444250d7fca019c10f349",
    "serial_onehot": "6455f4b21faf1919c2b38b5d9887bb4942f98b061ec9ec6901628adaaa53b3c3",
}
STAGE = "cts45_fourth_routed"
GUARD = .050


def exactly(pattern, text, label):
    values = re.findall(pattern, text, re.S)
    if len(values) != 1:
        raise ValueError(f"{label}: expected one occurrence, found {len(values)}")
    return values[0]


def one(path, variant):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SHA[variant]:
        raise ValueError(f"{variant}: artifact ZIP SHA-256 mismatch")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or any(
            n.startswith("/") or ".." in Path(n).parts for n in names
        ):
            raise ValueError("Unsafe ZIP entry")
        def read(name):
            return z.read(name).decode("utf-8")
        fixed = json.loads(read("fixed_word_manifest.json"))
        fourth = json.loads(read("fourth_diag_manifest.json"))
        decoded = json.loads(read("bank_decode_manifest.json"))
        tile = json.loads(read("tile_manifest.json"))
        if not (fixed["both_contestants_same_two_port_rf"]
                and fixed["serial_fifth_stage_excluded"]
                and fourth["clock_ns"] == 3.5
                and fourth["shared_fourth_stage"]
                and fourth["serial_fifth_control_repair_excluded"]
                and not any(fourth[k] for k in ("postcts", "routed", "extracted_rc"))
                and decoded["both_contestants_same_retiming"]
                and decoded["serial_fifth_stage_excluded"]
                and tile["same_tcl_for_both"]
                and tile["die_um"] == 260 and tile["core_um"] == 240):
            raise ValueError("Unmatched or non-preCTS provenance")
        for name, expected in {
            "cts45_fourth_diag.tcl": fixed["unchanged_fourth_tcl_sha256"],
            "run_fixed_word_fourth.sh": fixed["fixed_runner_sha256"],
            "run_bank_decode_fourth.sh": fixed["source_runner_sha256"],
        }.items():
            if hashlib.sha256(z.read(name)).hexdigest() != expected:
                raise ValueError("Embedded Tcl/runner SHA mismatch: " + name)
        if not (fourth["generated_tcl_sha256"]
                == decoded["unchanged_fourth_tcl_sha256"]
                == fixed["unchanged_fourth_tcl_sha256"]):
            raise ValueError("Physical Tcl mismatch")
        log = read(f"{variant}.high.log")
        if (log.count("V296_FOURTH_CONE_DONE") != 1 or
                log.count("V296_FOURTH_CONE_TIER PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS") != 1):
            raise ValueError("Missing/duplicated preCTS marker")
        a, slew, cap = exactly(
            r"V296_METRIC stage=" + STAGE +
            r" area_um2=([0-9.]+) slew=(\d+) cap=(\d+)",
            log, "final metric")
        def slack(kind):
            return float(exactly(
                r"V296_FOURTH_CONE_WORST_" + kind +
                r"_BEGIN\s+worst slack\s+(-?[0-9.]+)\s+V296_FOURTH_CONE_WORST_" +
                kind + r"_END", log, kind + " slack"))
        setup, hold = slack("SETUP"), slack("HOLD")
        area = float(a)
        if not (0 < area <= 30000 and int(slew) == int(cap) == 0 and hold >= 0):
            raise ValueError("PreCTS electrical/area gate failed")
        path_text = exactly(
            r"V296_FOURTH_CONE_SETUP_PATH_BEGIN\s+(.*?)\s+V296_FOURTH_CONE_SETUP_PATH_END",
            log, "setup path")
        start = exactly(r"Startpoint:\s+(\S+)", path_text, "start")
        end = exactly(r"Endpoint:\s+(\S+)", path_text, "end")
        common = [fixed, fourth, decoded, tile,
                  read(f"{variant}.inputs.sha256"),
                  read(f"{variant}.openroad.version")]
        return dict(variant=variant, artifact_sha256=digest,
                    area_um2=area, setup_slack_ns=setup, hold_slack_ns=hold,
                    cap_violations=int(cap), slew_violations=int(slew),
                    setup_guard_pass=setup >= GUARD,
                    worst_setup_startpoint=start, worst_setup_endpoint=end,
                    common_provenance=common)


def audit(pairwise, serial):
    p, s = one(pairwise, "pairwise"), one(serial, "serial_onehot")
    if p["common_provenance"] != s["common_provenance"]:
        raise ValueError("Different input hashes, tool versions or physical constraints")
    pa, sa = p["area_um2"], s["area_um2"]
    return dict(
        source_run=RUN,
        evidence_tier="MATCHED_PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS_NOT_SIGNOFF",
        candidate={k: v for k, v in p.items() if k != "common_provenance"},
        serial={k: v for k, v in s.items() if k != "common_provenance"},
        candidate_area_saving_fraction=1 - pa / sa,
        setup_slack_advantage_ns=p["setup_slack_ns"] - s["setup_slack_ns"],
        candidate_setup_margin_above_guard_ps=1000 * (p["setup_slack_ns"] - GUARD),
        maximum_net_postcts_extraction_setup_penalty_to_preserve_guard_ps=1000 * (p["setup_slack_ns"] - GUARD),
        serial_setup_shortfall_to_guard_ps=1000 * max(0, GUARD - s["setup_slack_ns"]),
        conditional_18_candidate_per_16_serial_area_overhead_budget_fraction=16 * sa / (18 * pa) - 1,
        conditional_19_candidate_per_16_serial_area_overhead_budget_fraction=16 * sa / (19 * pa) - 1,
        strongest_serial_fifth_stage_included=False,
        extracted_rc_timing_pass=False, routed_drc_pass=False, gpu_throughput_claim=False,
        decision=("CANDIDATE_PRECTS_GUARD_PASS_ROUTE_TRIAL_JUSTIFIED_NOT_SIGNOFF"
                  if p["setup_guard_pass"] else "FIXED_WORD_REPAIR_REJECT_PRECTS_GUARD_FAIL"))


def self_test():
    import tempfile
    assert abs(16 * 100 / (18 * 80) - 1 - 1 / 9) < 1e-12
    with tempfile.TemporaryDirectory() as temp:
        bad = Path(temp) / "bad.zip"
        bad.write_bytes(b"not a GitHub artifact")
        for variant in SHA:
            try:
                one(bad, variant)
            except ValueError:
                pass
            else:
                raise AssertionError("Corrupt ZIP accepted")
    print("V296_FIXED_WORD_PRECTS_SHA_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairwise", type=Path)
    ap.add_argument("--serial", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.pairwise or args.serial:
        if not (args.pairwise and args.serial):
            ap.error("Both original ZIPs required")
        result = audit(args.pairwise, args.serial)
        if args.output:
            args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print(json.dumps(result, sort_keys=True, indent=2))
        print("V296_FIXED_WORD_PRECTS_SHA_AUDIT_PASS")
    elif not args.self_test:
        ap.error("Supply --self-test or both ZIPs")
