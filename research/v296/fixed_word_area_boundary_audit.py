#!/usr/bin/env python3
"""SHA-pinned independent area/packing sensitivity for V296 fixed-word RF proxy.
Only mapped/pre-CTS evidence; no extracted timing, tile performance, or GPU claim.
GitHub Actions 40457696916: mapped 12714054823, pairwise preCTS 12716756605.
"""
import argparse
from decimal import Decimal, getcontext
import hashlib
import json
import re
import zipfile

getcontext().prec = 40
MAPPED_SHA = "bb75e7eb91e13599d9fcc230caaef51b0c1c43d579128ac3100d2f78b02f7522"
PRECTS_SHA = "cebe917377f0a3195a43e9bdb3917a0b8036e198ed8444250d7fca019c10f349"
NAMES = ("decoded_pairwise", "decoded_serial", "fixed_pairwise", "fixed_serial")

def verify(path, expected):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    if h.hexdigest() != expected:
        raise ValueError("ZIP SHA256 mismatch: " + path)

def mapped(path):
    verify(path, MAPPED_SHA)
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in NAMES:
            s = z.read(name + ".log").decode()
            area = re.findall(r"Chip area for module '\\[^']+':\s*([0-9.]+)", s)
            depth = re.findall(r"Longest topological path in .*?\(length=(\d+)\):", s)
            counts = []
            for cell in ("DFFR_X1", "DFF_X1"):
                hits = re.findall(r"^\s+" + cell + r"\s+(\d+)\s*$", s, re.M)
                if not hits:
                    raise ValueError("missing mapped flop: " + name + "/" + cell)
                counts.append(int(hits[-1]))
            if len(area) != 1 or len(depth) != 1 or sum(counts) != 388:
                raise ValueError("incomplete or inconsistent mapped log: " + name)
            out[name] = {"area": Decimal(area[0]), "depth": int(depth[0])}
        other = json.loads(z.read("independent_audit.json"))
        for name in NAMES:
            if out[name]["area"] != Decimal(str(other["areas"][name]["area_um2"])):
                raise ValueError("upstream mapped-area mismatch: " + name)
    return out

def prects(path):
    verify(path, PRECTS_SHA)
    with zipfile.ZipFile(path) as z:
        s = z.read("pairwise.high.log").decode()
        manifest = json.loads(z.read("fourth_diag_manifest.json"))
        if manifest["extracted_rc"] or manifest["postcts"] or manifest["routed"]:
            raise ValueError("unexpected evidence tier")
        metrics = re.findall(r"V296_METRIC stage=cts45_fourth_repaired area_um2=([0-9.]+) slew=(\d+) cap=(\d+)", s)
        setup = re.findall(r"V296_FOURTH_CONE_WORST_SETUP_BEGIN\s*worst slack\s+([+-]?[0-9.]+)", s)
        hold = re.findall(r"V296_FOURTH_CONE_WORST_HOLD_BEGIN\s*worst slack\s+([+-]?[0-9.]+)", s)
        if len(metrics) != 1 or len(setup) != 1 or len(hold) != 1:
            raise ValueError("incomplete or duplicate preCTS checkpoint")
        a, slew, cap = metrics[0]
        return {"area": Decimal(a), "setup": Decimal(setup[0]), "hold": Decimal(hold[0]),
                "slew": int(slew), "cap": int(cap)}

def analyze(m, p):
    a, b = m["fixed_pairwise"]["area"], m["fixed_serial"]["area"]
    da, db = m["decoded_pairwise"]["area"], m["decoded_serial"]["area"]
    rows = []
    for n in (12, 14, 15, 16, 17, 18, 20, 24, 32):
        # (n+1) * a * (1+h) <= n*b: identical independent tiles,
        # budget exactly n serial tiles; h is candidate-only overhead.
        h = Decimal(n)*b/(Decimal(n+1)*a)-1
        rows.append({"serial_tiles": n, "candidate_tiles": n+1,
                     "max_candidate_only_overhead_pct": str(100*h),
                     "zero_overhead_possible": h >= 0})
    return {
        "decision": "MAPPED_AREA_SENSITIVITY_ONLY_NOT_GPU_WIN",
        "run_id": 40457696916,
        "fixed_pairwise_area_um2": str(a),
        "fixed_serial_area_um2": str(b),
        "fixed_pairwise_area_saving_pct": str(100*(1-a/b)),
        "decoded_pairwise_area_saving_pct": str(100*(1-da/db)),
        "relative_saving_change_percentage_points": str(100*(da/db-a/b)),
        "fixed_vs_decoded_pairwise_change_pct": str(100*(a/da-1)),
        "fixed_vs_decoded_serial_change_pct": str(100*(b/db-1)),
        "prects_pairwise_area_um2": str(p["area"]),
        "prects_pairwise_area_inflation_pct": str(100*(p["area"]/a-1)),
        "prects_pairwise_setup_ns": str(p["setup"]),
        "prects_pairwise_hold_ns": str(p["hold"]),
        "prects_pairwise_cap": p["cap"],
        "prects_pairwise_slew": p["slew"],
        "mapped_topological_depth": {k: m[k]["depth"] for k in NAMES},
        "conditional_packing": rows,
        "limitations": [
            "two-word flop RF proxy only; not production SRAM",
            "fourth-stage preCTS; serial fifth-stage repair excluded",
            "no extracted-RC, postCTS, power, bandwidth or GPU throughput evidence",
            "packing arithmetic excludes shared tile overhead, routing, clock and power"
        ]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapped-zip")
    parser.add_argument("--pairwise-prects-zip")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.self_test:
        fake = {name: {"area": Decimal(90 if name.endswith("pairwise") else 100), "depth": 1}
                for name in NAMES}
        fake["decoded_pairwise"]["area"] = Decimal(95)
        out = analyze(fake, {"area": Decimal(90), "setup": Decimal("0.1"),
                             "hold": Decimal(0), "cap": 0, "slew": 0})
        assert out["fixed_pairwise_area_saving_pct"] == "10.0"
        assert out["conditional_packing"][0]["zero_overhead_possible"]
        print("V296_FIXED_WORD_AREA_BOUNDARY_SELFTEST_PASS")
        return
    if not args.mapped_zip or not args.pairwise_prects_zip:
        parser.error("both artifact ZIPs required")
    output = json.dumps(analyze(mapped(args.mapped_zip), prects(args.pairwise_prects_zip)), indent=2) + "\n"
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    print(output)

if __name__ == "__main__":
    main()
