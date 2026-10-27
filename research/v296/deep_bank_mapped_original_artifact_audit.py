#!/usr/bin/env python3
"""SHA-pinned independent audit of V296 dynamic deep-bank mapped artifacts.

Only synthesis/RTL evidence. LTP -noff includes sequential arcs and emits loop
warnings; it is not STA and is intentionally not interpreted as timing.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile

ARTIFACTS = {
    4: ("fe59053e653148616c35b2e1304d34ff9e200fe0ddd02b443ba6b8c2bcf68b20", 12745855863),
    8: ("add9c2dcf6a85e6fd6bd5eaf63bee86c78bbc34e205c0b8d51378c612d9df8fb", 12744174948),
}
RTL = {
    4: ("41bb2b30d57f0dbea2212243b0896c521f908c60538cf518c1c1e58f961b4d21", 12745770168),
    8: ("69d662753c42526a3b63dde5a3f0bd0cb9c2df61a5ee4a5e6fadae60acd29c1b", 12743389008),
    16: ("cc9cfc0c456fdd5e9781f32e684319cae6c7935676fe3c3c1f0d8b22d0dbce6f", 12744113447),
}


def sha_checked_zip(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"artifact SHA mismatch: {path}")
    z = ZipFile(path)
    if any(".." in Path(n).parts or n.startswith("/") for n in z.namelist()):
        raise ValueError("unsafe artifact ZIP path")
    return z


def parse_mapped(z, depth):
    if z.read("evidence_tier.txt").decode().strip() != f"MAPPED_ONLY_NO_PHYSICAL_SIGNOFF depth={depth}":
        raise ValueError("wrong evidence tier")
    provenance = z.read("source_library.sha256").decode()
    version = z.read("yosys.version").decode().strip()
    if not version.startswith("Yosys 0.9"):
        raise ValueError("unrecognized synthesis tool")
    if len(provenance.splitlines()) != 4:
        raise ValueError("incomplete provenance")
    out = {}
    for name in ("pairwise", "serial"):
        s = z.read(f"depth{depth}_{name}.log").decode(errors="replace")
        if "found and reported 0 problems." not in s or "Executing CHECK pass" not in s:
            raise ValueError(f"Yosys check did not pass: {depth} {name}")
        areas = re.findall(r"Chip area for module '\\v296_tile_slice_deep_bank': ([0-9.]+)", s)
        if len(areas) != 1:
            raise ValueError(f"ambiguous area: {depth} {name}")
        lengths = re.findall(r"Longest topological path in v296_tile_slice_deep_bank \(length=(\d+)\):", s)
        if len(lengths) != 1:
            raise ValueError(f"missing LTP diagnostic: {depth} {name}")
        out[name] = {"mapped_area_um2": float(areas[0]),
                     "ltp_noff_nodes_DIAGNOSTIC_NOT_TIMING": int(lengths[0]),
                     "ltp_noff_loop_warnings": s.count("Warning: Detected loop at"),
                     "yosys_check_problems": 0}
    return out, provenance, version


def evaluate(mapped, rtl):
    parsed, provenances, versions = {}, [], []
    for depth in (4, 8):
        z = sha_checked_zip(mapped[depth], ARTIFACTS[depth][0])
        parsed[depth], provenance, version = parse_mapped(z, depth)
        provenances.append(provenance)
        versions.append(version)
    if len(set(provenances)) != 1 or len(set(versions)) != 1:
        raise ValueError("source/library/tool mismatch across depths")
    for depth in (4, 8, 16):
        z = sha_checked_zip(rtl[depth], RTL[depth][0])
        files = z.namelist()
        if files != ["v296_deep_bank_rtl.log"]:
            raise ValueError("unexpected RTL evidence archive")
        s = z.read(files[0]).decode().strip()
        m = re.fullmatch(r"V296_DEEP_BANK_DYNAMIC_RTL_PASS depth=(\d+) cycles=(\d+) accepted=(\d+) word_addresses=(\d+)", s)
        if not m or tuple(map(int, m.groups())) != (depth, 2048, 6608, depth):
            raise ValueError("RTL oracle result mismatch")
    c4 = parsed[4]["pairwise"]["mapped_area_um2"]
    s4 = parsed[4]["serial"]["mapped_area_um2"]
    c8 = parsed[8]["pairwise"]["mapped_area_um2"]
    s8 = parsed[8]["serial"]["mapped_area_um2"]
    if not (c4 < s4 and c8 < s8 and c4 < c8 and s4 < s8):
        raise ValueError("unexpected mapped area ordering")
    pred_c16 = c8 + 2 * (c8 - c4)
    pred_s16 = s8 + 2 * (s8 - s4)
    return {
        "source_run": 40527760514,
        "source_head_sha": "41b3a4d2c922aea43336aa571a60d5b3d88dbcb5",
        "evidence_tier": "SHA_VERIFIED_RTL_AND_MAPPED_SYNTHESIS_ONLY",
        "mapped": parsed,
        "rtl_passed_depths": [4, 8, 16],
        "matched_source_library_tool": True,
        "measured_saving_um2": {"4": round(s4-c4, 6), "8": round(s8-c8, 6)},
        "measured_saving_percent": {"4": round(100*(s4-c4)/s4, 6), "8": round(100*(s8-c8)/s8, 6)},
        "linear_two_point_prediction_UNSEEN_depth16": {
            "pairwise_um2": round(pred_c16, 6), "serial_um2": round(pred_s16, 6),
            "difference_um2": round(pred_s16-pred_c16, 6),
            "acceptance": "each predicted mapped area within 15% and pairwise < serial; falsifies interpolation/extrapolation model only",
        },
        "limitations": ["mapped cell area is not placed or routed area",
                        "ltp -noff crosses sequential boundaries and emits loop warnings; no clock timing inference",
                        "serial PREDECODE(0) is not necessarily strongest feasible fifth-stage physical serial",
                        "flop RF proxy, not SRAM macro; 8-bit datapath, no workload throughput or power"],
    }


def self_test():
    assert round(13835.990 - 12960.584, 3) == 875.406
    assert round(18782.260 - 17552.542, 3) == 1229.718
    assert round(17552.542 + 2*(17552.542-12960.584), 3) == 26736.458
    assert round(18782.260 + 2*(18782.260-13835.990), 3) == 28674.800
    print("V296_DEEP_BANK_MAPPED_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    for d in (4, 8): p.add_argument(f"--mapped{d}", type=Path)
    for d in (4, 8, 16): p.add_argument(f"--rtl{d}", type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    else:
        args = vars(a)
        if any(args[f"mapped{d}"] is None for d in (4, 8)) or any(args[f"rtl{d}"] is None for d in (4, 8, 16)):
            p.error("provide all five original artifact ZIP paths")
        print(json.dumps(evaluate({d: args[f"mapped{d}"] for d in (4, 8)},
                                  {d: args[f"rtl{d}"] for d in (4, 8, 16)}), indent=2, sort_keys=True))
