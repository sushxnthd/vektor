#!/usr/bin/env python3
"""SHA-locked, independent physical locality audit for the original V296
post-CTS detailed-route artifact. SPEF total cap is NOT STA pin cap.
Not signoff, not a GPU tile performance claim.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED_SHA256 = "057d4fe6d4bf67164857c54c9635c302e163da6b486f59515b7b8151578d8388"
RUN_ID = 40309580865
ARTIFACT_ID = 12648648864
DRIVERS = ("_12573_", "_10310_", "_09621_")
SETUP_GUARD_NS = 0.050

def insist(ok, message):
    if not ok:
        raise ValueError(message)

def verify_sha(blob):
    digest = hashlib.sha256(blob).hexdigest()
    insist(digest == EXPECTED_SHA256, "Artifact SHA-256 mismatch: " + digest)
    return digest

def one(pattern, source, flags=0):
    matches = list(re.finditer(pattern, source, flags))
    insist(len(matches) == 1, "Expected one match: " + pattern)
    return matches[0]

def audit(path):
    digest = verify_sha(Path(path).read_bytes())
    with zipfile.ZipFile(path) as z:
        names = ("pairwise.high.log", "pairwise.high.cts45.spef",
                 "pairwise.high.cts45.def", "pairwise.tile.audit.json")
        insist(all(n in z.namelist() for n in names), "Missing physical evidence")
        log, spef, deff, row_text = (z.read(n).decode("utf-8") for n in names)
    insist("V296_CTS45_DRC_COUNT 0" in log and
           "V296_CTS45_IS_ROUTED 1" in log and
           "V296_CTS45_DONE" in log, "Route not complete")
    row = json.loads(row_text)
    insist(row.get("variant") == "pairwise" and row.get("complete") is True,
           "Wrong contestant")
    f = row["final"]
    insist(f["cap"] == 3 and f["slew"] == 0, "Electrical mismatch")
    insist(abs(f["setup_ns"] + 1.047895) < 1e-8 and
           abs(f["hold_ns"] + .036622) < 1e-8, "STA mismatch")
    insist(f["setup_ns"] < SETUP_GUARD_NS and f["hold_ns"] < 0,
           "Unexpected closure")
    report = one(r"V296_CTS45_CAP_VIOLATORS_BEGIN\s*(.*?)\s*V296_CTS45_CAP_VIOLATORS_END",
                 log, re.S).group(1)
    lines = re.findall(r"^(_\d+_)/ZN\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+) \(VIOLATED\)$",
                       report, re.M)
    insist(len(lines) == 3 and set(x[0] for x in lines) == set(DRIVERS),
           "Changed cap violations")
    units = int(one(r"^UNITS DISTANCE MICRONS (\d+) ;$", deff, re.M).group(1))
    insist(units > 0, "Invalid DEF units")
    placements = {}
    for inst, master, x, y in re.findall(
            r"^\s*-\s+(\S+)\s+(\S+)\s+[^\n]*?\+ PLACED \( (\d+) (\d+) \)",
            deff, re.M):
        placements[inst] = (master, int(x) / units, int(y) / units)
    insist(len(placements) > 1000, "DEF parsing failed")
    head = spef[:spef.index("*D_NET")]
    name_map = {int(i): n for i, n in re.findall(r"^\*(\d+) (\S+)$", head, re.M)}
    inverse = {n: i for i, n in name_map.items()}
    insist(len(inverse) == len(name_map), "Ambiguous SPEF names")
    relevant = {}
    for m in re.finditer(r"^\*D_NET (\*\d+|\S+) ([\d.eE+-]+)\s*\n(.*?)(?=^\*END)",
                         spef, re.M | re.S):
        conn = one(r"\*CONN\s*\n(.*?)(?=^\*CAP)", m.group(3), re.M | re.S).group(1)
        pins = re.findall(r"^\*I \*(\d+):(\S+) ([IO]) \*D (\S+)$", conn, re.M)
        for driver in DRIVERS:
            if any(i == str(inverse[driver]) and p == "ZN" and d == "O"
                   for i, p, d, cell in pins):
                insist(driver not in relevant, "Duplicate driver net")
                sinks = [(name_map[int(i)], p, cell) for i, p, d, cell in pins if d == "I"]
                relevant[driver] = (m.group(1), float(m.group(2)), sinks, len(pins))
    insist(set(relevant) == set(DRIVERS), "Missing SPEF drivers")
    result_rows = []
    for driver, limit, cap, slack in lines:
        limit, cap, slack = map(float, (limit, cap, slack))
        insist(abs(cap - limit + slack) < 1e-4, "Cap slack mismatch")
        net, netcap, sinks, count = relevant[driver]
        insist(len(sinks) == 1 and count == 2,
               "Not a point-to-point net; reject locality inference")
        sink, pin, sink_master = sinks[0]
        insist(driver in placements and sink in placements, "Missing DEF placement")
        a, ax, ay = placements[driver]
        b, bx, by = placements[sink]
        insist(b == sink_master, "DEF/SPEF sink mismatch")
        result_rows.append({
            "driver": driver, "driver_master": a, "sink": sink,
            "sink_pin": pin, "sink_master": b, "spef_net": net,
            "sta_cap_limit_ff": limit, "sta_cap_ff": cap,
            "sta_excess_ff": cap - limit,
            "excess_percent_of_limit": 100 * (cap - limit) / limit,
            "spef_total_cap_ff": 1000 * netcap,
            "spef_pin_count": count,
            "def_origin_manhattan_um": abs(ax - bx) + abs(ay - by),
            "geometry_note": "cell origin separation, NOT actual routed wirelength"
        })
    return {
        "run_id": RUN_ID, "artifact_id": ARTIFACT_ID,
        "zip_sha256": digest,
        "evidence_tier": "post-CTS detailed-route OpenRCX; not signoff",
        "variant": "pairwise", "setup_slack_ns": f["setup_ns"],
        "hold_slack_ns": f["hold_ns"],
        "setup_repair_to_plus50ps_ns": SETUP_GUARD_NS - f["setup_ns"],
        "hold_repair_to_zero_ns": -f["hold_ns"],
        "drc_count": 0, "slew_violations": f["slew"],
        "cap_violations": f["cap"], "cap_violators": result_rows,
        "physical_gate": "FAIL",
        "interpretation": "All three cap violators are point-to-point; physical wire/locality may contribute but causality is unproven.",
        "measured_gpu_speedup": False, "equal_consumed_area": False
    }

def self_test():
    assert abs((13.085626 - 11.482200) - 1.603426) < 1e-9
    try:
        verify_sha(b"corrupt")
    except ValueError:
        pass
    else:
        raise AssertionError("Corrupt artifact accepted")
    print("V296_CAP_LOCALITY_SELFTEST_PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--zip", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.zip:
        result = json.dumps(audit(a.zip), indent=2) + "\n"
        if a.output:
            a.output.write_text(result)
        print(result)
    if not (a.self_test or a.zip):
        p.error("Specify --self-test or --zip")
