#!/usr/bin/env python3
"""SHA-locked read-only extracted STA paths for completed V296 deep-bank artifacts.

D8 pairwise and D4 serial are different depths: NEVER infer matched Pareto.
No routing, resizing, RC rescaling, or holdout access is performed.
"""
import argparse
import hashlib
import json
import re
from decimal import Decimal as D
from pathlib import Path
from zipfile import ZipFile

CASES = {
    "D8_pairwise": dict(variant="pairwise", bits=3, artifact=12769775926,
        sha="92a84c3923eb62cd506241bcb1d8da06cfcfbd6a13328c8e050b14f301086f4b",
        setup="-0.684592", hold="0.010986", area="28984.15729646331", cap=1),
    "D4_serial_onehot": dict(variant="serial_onehot", bits=2, artifact=12769708334,
        sha="edeb136bc054eddf7434119115df198e7d4403c9bd01c0a726df7fb30519755b",
        setup="-1.316510", hold="0.002572", area="23265.68981914079", cap=6),
}
TOL = D("0.001")
GUARD = D("0.050")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def original(path, case):
    c = CASES[case]
    if sha(path.read_bytes()) != c["sha"]:
        raise ValueError("Immutable original artifact ZIP digest mismatch")
    v = c["variant"]
    with ZipFile(path) as z:
        m = json.loads(z.read("deep_bank_hold25_manifest.json"))
        expected = dict(word_bits=c["bits"], depth=1 << c["bits"], banks=16,
                        read_ports_per_bank=2, global_write_ports=1,
                        clock_ns=3.5, rc_multiplier=2.0, holdouts="SEALED",
                        strongest_serial_fifth_stage=True)
        if any(m.get(k) != x for k, x in expected.items()):
            raise ValueError("Resource/clock/RC mismatch")
        tcl = z.read("cts45_hold25_tile.tcl")
        if sha(tcl) != m["frozen_hold25_tcl_sha256"]:
            raise ValueError("Physical Tcl hash mismatch")
        for token in ("read_spef", "detailed_route -output_drc",
                      "repair_timing -setup -slack_margin 0.250",
                      "repair_timing -hold -slack_margin 0.025",
                      "adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0"):
            if tcl.decode().count(token) != 1:
                raise ValueError("Changed physical Tcl: " + token)
        for suffix in (".high.cts45.def", ".high.cts45.spef"):
            if len(z.read(v + suffix)) < 100000:
                raise ValueError("Missing routed DEF/SPEF")
        if z.read(v + ".high.cts45.drc.rpt").strip():
            raise ValueError("Nonzero original route DRC")
        if z.read(v + ".deep_bank.exit.txt").decode().strip() != "EXIT_CODE=0":
            raise ValueError("Original route incomplete")
        log = z.read(v + ".high.log").decode(errors="replace")
        for marker in ("V296_CTS45_DONE", "V296_CTS45_DRC_COUNT 0",
                       "V296_CTS45_IS_ROUTED 1", "V296_CTS45_RC_MULTIPLIER 2.0"):
            if log.count(marker) != 1:
                raise ValueError("Original route marker absent/ambiguous: " + marker)
        a = json.loads(z.read(v + ".tile.audit.json"))
        f = a["final"]
        if not a["complete"] or a["feasible"] or a["variant"] != v:
            raise ValueError("Incorrect original physical verdict")
        for k in ("setup", "hold", "area"):
            field = {"setup": "setup_ns", "hold": "hold_ns", "area": "area_um2"}[k]
            if abs(D(str(f[field])) - D(c[k])) > D("0.000001"):
                raise ValueError("Original numerical physical mismatch: " + k)
        if f["cap"] != c["cap"] or f["slew"] != 0:
            raise ValueError("Original electrical mismatch")
    return dict(source_run=40557136436, artifact_id=c["artifact"],
                zip_sha256=c["sha"], depth=1 << c["bits"], variant=v,
                setup_ns=c["setup"], hold_ns=c["hold"], area_um2=c["area"],
                cap_violations=c["cap"], physical_gate="FAIL",
                matched_architecture_comparison=False)


def generate():
    import v296_postroute_sta_replay as base
    tcl = base.TCL
    if tcl.count("read_spef $spef") != 1:
        raise ValueError("Read-only extracted SPEF replay anchor changed")
    for token in ("report_checks -path_delay max", "report_checks -path_delay min"):
        if tcl.count(token) != 1:
            raise ValueError("Named critical-path report missing")
    for line in tcl.splitlines():
        if line.strip().startswith("#"):
            continue
        if any(x in line for x in ("repair_timing ", "repair_design ",
               "detailed_route ", "global_route ", "clock_tree_synthesis ",
               "adjust_rc -res_factor")):
            raise ValueError("Physical mutation in read-only replay")
    return tcl


def section(log, label):
    begin, end = ("V296_REPLAY_" + label + "_" + x for x in ("BEGIN", "END"))
    if log.splitlines().count(begin) != 1 or log.splitlines().count(end) != 1:
        raise ValueError("Missing/duplicated extracted report " + label)
    return log.split(begin, 1)[1].split(end, 1)[0]


def worst(block):
    m = re.findall(r"^worst slack\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s*$", block, re.M)
    if len(m) != 1:
        raise ValueError("Ambiguous extracted worst slack")
    x = D(m[0])
    if not x.is_finite():
        raise ValueError("Nonfinite extracted slack")
    return x


def critical(block):
    import v296_postroute_sta_replay as base
    paths = base.paths(block)
    if len(paths) != 1:
        raise ValueError("Missing or multiple named worst paths")
    if "data arrival time" not in block or "data required time" not in block:
        raise ValueError("No extracted path delay table")
    rows = []
    for line in block.splitlines():
        fields = line.split()
        arrows = [i for i, f in enumerate(fields) if f in ("^", "v")]
        if len(arrows) != 1:
            continue
        i = arrows[0]
        if i < 2 or i + 2 >= len(fields):
            continue
        try:
            inc, arrival = D(fields[i-2]), D(fields[i-1])
        except Exception:
            continue
        if not inc.is_finite() or not arrival.is_finite():
            raise ValueError("Nonfinite path increment")
        pin, cell = fields[i+1], fields[i+2].strip("()")
        if "/" in pin and cell:
            rows.append(dict(pin=pin, cell=cell, increment_ns=float(inc),
                             arrival_ns=float(arrival)))
    if len(rows) < 4:
        raise ValueError("Incomplete per-pin path increments")
    p = paths[0]
    return dict(startpoint=p["start"], endpoint=p["end"],
                slack_ns=p["slack_ns"], path_pin_rows=len(rows),
                largest_reported_increments=sorted(
                    rows, key=lambda r: r["increment_ns"], reverse=True)[:12],
                start_is_primary_input="(input port" in block.splitlines()[1],
                warning="Reported increments include upstream net effects and may include clock path; not intrinsic cell delay")


def replay(log, case):
    c = CASES[case]
    if log.splitlines().count("V296_REPLAY_DONE") != 1:
        raise ValueError("Incomplete OpenSTA replay")
    if log.splitlines().count("V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION") != 1:
        raise ValueError("Incorrect evidence tier")
    s, h = worst(section(log, "SETUP_WORST")), worst(section(log, "HOLD_WORST"))
    if abs(s-D(c["setup"])) > TOL or abs(h-D(c["hold"])) > TOL:
        raise ValueError("Reconstructed extracted slack differs from original >1ps")
    sp, hp = critical(section(log, "SETUP_PATHS")), critical(section(log, "HOLD_PATHS"))
    if abs(D(str(sp["slack_ns"]))-s) > TOL or abs(D(str(hp["slack_ns"]))-h) > TOL:
        raise ValueError("Named critical path not original worst slack")
    return dict(verdict="EXTRACTED_PATHS_REPRODUCED_NOT_FEASIBLE",
                source_run=40557136436, artifact_id=c["artifact"],
                original_zip_sha256=c["sha"], depth=1 << c["bits"],
                variant=c["variant"], setup_ns=str(s), hold_ns=str(h),
                recovery_to_50ps_guard_ns=str(GUARD-s),
                setup_path=sp, hold_path=hp, matched_comparison=False,
                physical_gate="FAIL", repair_demonstrated=False,
                gpu_speedup=False, holdouts="SEALED")


def selftest():
    generate()
    def b(name, value):
        return "V296_REPLAY_" + name + "_BEGIN\n" + value + "\nV296_REPLAY_" + name + "_END\n"
    def path(slack, status):
        return ("Startpoint: wave_valid[8] (input port clocked by coreclk)\n"
                "Endpoint: _1_ (rising edge-triggered flip-flop clocked by coreclk)\n"
                "Path Type: max\n"
                + "".join("2 8.0 0.04 0.05 0.2 v c%d/Z (BUF_X1)\n" % i for i in range(4))
                + "data arrival time\ndata required time\n"
                + "slack (" + status + ") " + slack)
    sample = ("V296_REPLAY_EVIDENCE_TIER POSTROUTE_SPEF_DEF_RECONSTRUCTION\n"
              + b("SETUP_WORST", "worst slack -0.684592")
              + b("HOLD_WORST", "worst slack 0.010986")
              + b("SETUP_PATHS", path("-0.684592", "VIOLATED"))
              + b("HOLD_PATHS", path("0.010986", "MET")) + "V296_REPLAY_DONE\n")
    assert replay(sample, "D8_pairwise")["recovery_to_50ps_guard_ns"] == "0.734592"
    for bad in (sample.replace("V296_REPLAY_DONE", ""),
                sample.replace("worst slack -0.684592", "worst slack -0.584592"),
                sample.replace("Endpoint: _1_", "NotEndpoint: _1_"),
                sample.replace("c3/Z (BUF_X1)", "c3/Z")):
        try:
            replay(bad, "D8_pairwise")
        except (ValueError, IndexError):
            pass
        else:
            raise AssertionError("Corrupted extracted path accepted")
    print("V296_DEEP_BANK_EXTRACTED_PATH_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--generate", type=Path)
    p.add_argument("--verify-zip", type=Path)
    p.add_argument("--audit-log", type=Path)
    p.add_argument("--case", choices=tuple(CASES))
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.self_test:
        selftest()
    if a.generate:
        a.generate.parent.mkdir(parents=True, exist_ok=True)
        a.generate.write_text(generate())
    result = None
    if a.verify_zip:
        if not a.case:
            p.error("--case required")
        result = original(a.verify_zip, a.case)
    if a.audit_log:
        if not a.case:
            p.error("--case required")
        result = replay(a.audit_log.read_text(errors="replace"), a.case)
    if result is not None:
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if a.output:
            a.output.write_text(payload)
        print(payload)
    if not (a.self_test or a.generate or a.verify_zip or a.audit_log):
        p.error("Choose operation")


if __name__ == "__main__":
    main()
