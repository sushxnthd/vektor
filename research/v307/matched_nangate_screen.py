#!/usr/bin/env python3
"""Reproducible matched Nangate45 cell-area/load screen, NOT placed STA.

One registered RTL selector, three identical interfaces, three frozen policies.
No GPU IPC or silicon frequency claim. Re-run: python3 research/v307/matched_nangate_screen.py
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "research/v307/nangate_screen"
OUT.mkdir(parents=True, exist_ok=True)
REV = "eda8e552974d47a12616294dddf4012d892548d3"
URL = ("https://raw.githubusercontent.com/The-OpenROAD-Project/"
       "OpenROAD-flow-scripts/" + REV +
       "/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib")
LIB = OUT / "NangateOpenCellLibrary_typical.lib"
RTL = ROOT / "research/v307/v307_issue_select.sv"
# First screen includes strongest same-information control, then two load sensitivities.
CASES = [(m, 10) for m in (0, 1, 2)] + [(m, load) for load in (2, 30) for m in (0, 1)]
TIMEOUT = 720
# Declared BEFORE the new mapped physical results are inspected:
# No performance gain versus FUTURE-TIE in opened W1 pilot (-0.388%).
# To justify further implementation, pressure must save >=10% mapped area
# versus FUTURE-TIE at nominal load, with <=20% overhead versus MAX-NOW,
# and it must not lose the nominal cell-area advantage at either load corner.
# This is a screening convention, not a foundry signoff criterion.

def run(args, timeout=TIMEOUT):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=timeout, check=False)

def mapped_area(log):
    hits = re.findall(r"Chip area for module[^\n]*?:\s*([0-9]+(?:\.[0-9]+)?)", log)
    if not hits:
        hits = re.findall(r"Chip area[^\n]*?:\s*([0-9]+(?:\.[0-9]+)?)", log)
    return float(hits[-1]) if hits else None

def main():
    if not LIB.exists():
        urllib.request.urlretrieve(URL, LIB)
    libhash = hashlib.sha256(LIB.read_bytes()).hexdigest()
    rtlhash = hashlib.sha256(RTL.read_bytes()).hexdigest()
    results = {}
    for mode, load in CASES:
        key = f"mode{mode}_load{load}ff"
        constr = OUT / f"{key}.constr"
        constr.write_text(f"set_driving_cell BUF_X1\nset_load {load}\n")
        logpath = OUT / f"{key}.log"
        # Same synthesis, liberty, registered IO and optimization script for all modes.
        # ABC -D is a mapping target in ps, NOT measured worst-path delay.
        script = (
            f"read_liberty -lib -ignore_miss_func -ignore_miss_dir {LIB}; "
            f"read_verilog -sv {RTL}; "
            f"hierarchy -top v307_issue_select -chparam MODE {mode}; "
            "synth -top v307_issue_select -flatten; "
            f"dfflibmap -liberty {LIB}; "
            f"abc -liberty {LIB} -constr {constr} -D 10000; "
            "clean; check -assert; "
            f"stat -liberty {LIB}"
        )
        try:
            p = run(["yosys", "-Q", "-T", "-p", script])
            logpath.write_text(p.stdout)
            area = mapped_area(p.stdout) if p.returncode == 0 else None
            results[key] = {"mode": mode, "load_ff": load, "exit": p.returncode,
                            "mapped_area_um2": area, "log": logpath.name,
                            "structural_check_pass": p.returncode == 0 and
                            "0 problems" in p.stdout}
        except subprocess.TimeoutExpired:
            results[key] = {"mode": mode, "load_ff": load, "error": "timeout",
                            "mapped_area_um2": None, "structural_check_pass": False}
        print(key, results[key], flush=True)
    def area(mode, load):
        return results[f"mode{mode}_load{load}ff"]["mapped_area_um2"]
    complete = all(v.get("mapped_area_um2") is not None and
                   v.get("structural_check_pass") for v in results.values())
    gate = None
    if complete:
        nominal = area(1, 10) <= .90 * area(2, 10) and area(1, 10) <= 1.20 * area(0, 10)
        # Fail closed. Nominal gate can already falsify the candidate. This
        # initial sweep intentionally does not map MODE=2 at the load corners;
        # therefore a hypothetical nominal pass cannot claim a full pass.
        corner_keys = [f"mode2_load{load}ff" for load in (2, 30)]
        corners_available = all(k in results for k in corner_keys)
        corners = (all(area(1, load) < area(2, load) for load in (2, 30))
                   if corners_available else None)
        gate = bool(nominal and corners is True)
    report = {"evidence_tier": "mapped Nangate45 cell area and ABC load sensitivity; no STA/route/power",
              "library_revision": REV, "library_sha256": libhash,
              "rtl_sha256": rtlhash, "abc_delay_target_ps_not_measured": 10000,
              "screen_frozen_before_mapping": ">=10% nominal area saving vs FUTURE-TIE, <=20% nominal area overhead vs MAX-NOW, smaller than FUTURE-TIE at 2/30fF",
              "all_cases_complete": complete, "physical_area_screen_survives": gate,
              "corner_vs_future_tie_available": (corners_available if complete else False),
              "cases": results}
    (OUT / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"complete": complete, "area_gate_survives": gate,
                      "nominal_um2": {str(m): area(m, 10) for m in (0, 1, 2)}},
                     indent=2), flush=True)
    return 0 if complete else 1

if __name__ == "__main__":
    sys.exit(main())
