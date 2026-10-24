#!/usr/bin/env python3
"""Independently join OpenSTA max-slew pin violations to immutable SPEF nets."""
import collections
import hashlib
import json
from pathlib import Path
import re
import sys


def resolve(token, names):
    if token.startswith("*"):
        ref, sep, pin = token.partition(":")
        base = names.get(ref[1:], ref)
        return base + ("/" + pin if sep else "")
    return token


def parse_spef(text):
    if not re.search(r"(?m)^\*C_UNIT\s+1\s+PF\s*$", text):
        raise ValueError("Unexpected SPEF capacitance units")
    names = dict(re.findall(r"(?m)^\*(\d+)\s+(\S+)\s*$", text.split("*D_NET", 1)[0]))
    pin_net = {}
    net_info = {}
    pat = r"(?ms)^\*D_NET\s+(\S+)\s+([\d.eE+\-]+)\s*\n(.*?)^\*END\s*$"
    for m in re.finditer(pat, text):
        net = resolve(m.group(1), names)
        cap = float(m.group(2))
        body = m.group(3)
        if "*CONN" not in body or "*CAP" not in body:
            raise ValueError("Malformed SPEF net block")
        conn = body.split("*CONN", 1)[1].split("*CAP", 1)[0]
        fanout, drivers = 0, []
        for line in conn.splitlines():
            hit = re.match(r"^\*(I|P)\s+(\S+)\s+([IOB])\b(.*)$", line)
            if not hit:
                continue
            kind, raw_pin, direction, suffix = hit.groups()
            pin = resolve(raw_pin, names)
            if pin in pin_net and pin_net[pin] != net:
                raise ValueError("Pin belongs to multiple SPEF nets: " + pin)
            pin_net[pin] = net
            if kind == "I" and direction == "I":
                fanout += 1
            if kind == "I" and direction == "O":
                cell = re.search(r"\*D\s+(\S+)", suffix)
                drivers.append({"pin": pin, "cell": cell.group(1) if cell else "UNKNOWN"})
        net_info[net] = {"declared_total_cap_pf": cap, "cell_input_connections": fanout,
                         "cell_output_drivers": drivers}
    if not net_info:
        raise ValueError("No SPEF nets")
    return pin_net, net_info


def parse_violators(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"^(\S+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s+\(VIOLATED\)", line)
        if m:
            pin, limit, slew, slack = m.groups()
            limit, slew, slack = float(limit), float(slew), float(slack)
            if slack >= 0 or abs((slew - limit) + slack) > 0.00001:
                raise ValueError("Inconsistent violating-pin transition: " + pin)
            rows.append({"pin": pin, "limit_ns": limit, "slew_ns": slew,
                         "excess_ns": -slack})
    if not rows:
        raise ValueError("No explicit violating-pin rows")
    if len(set(x["pin"] for x in rows)) != len(rows):
        raise ValueError("Duplicate pin rows")
    return rows


def analyze(slew_text, spef_text):
    pins, nets = parse_spef(spef_text)
    violations = parse_violators(slew_text)
    if len(violations) != 33:
        raise ValueError("Expected 33 frozen high-RC violations; found " + str(len(violations)))
    unmapped = [v["pin"] for v in violations if v["pin"] not in pins]
    if unmapped:
        raise ValueError("SPEF lacks violating pins: " + repr(unmapped))
    by_net = collections.defaultdict(list)
    for v in violations:
        by_net[pins[v["pin"]]].append(v)
    groups = []
    for net, rows in sorted(by_net.items(), key=lambda kv: -len(kv[1])):
        worst = max(rows, key=lambda x: x["excess_ns"])
        groups.append({"net": net, "violating_pin_count": len(rows),
                       "worst_pin": worst["pin"], "worst_excess_ns": worst["excess_ns"],
                       **nets[net], "pins": rows})
    return {"decision": "SLEW_PIN_TO_SPEF_MAP_PASS",
            "total_violating_pins": len(violations),
            "distinct_violating_nets": len(groups), "groups": groups,
            "limitations": "Post-hoc attribution, not a prospective repair or slew closure."}


def self_test():
    spef = ("*SPEF \"ieee 1481-1999\"\n*C_UNIT 1 PF\n*NAME_MAP\n*1 netA\n"
            "*2 _123_\n*D_NET *1 0.12\n*CONN\n*I *2:A I\n"
            "*I *2:ZN O *D INV_X32\n*CAP\n1 *2:A 0.12\n*END\n")
    p, n = parse_spef(spef)
    assert p["_123_/A"] == "netA" and n["netA"]["cell_input_connections"] == 1
    v = parse_violators("_123_/A 0.250000 0.281187 -0.031187 (VIOLATED)\n")
    assert len(v) == 1 and abs(v[0]["excess_ns"] - 0.031187) < 1e-9
    for bad in ("_123_/A 0.25 0.28 +0.03 (VIOLATED)",
                "_123_/A 0.25 0.28 -0.01 (VIOLATED)"):
        try:
            parse_violators(bad)
        except ValueError:
            continue
        raise AssertionError("Malformed violation accepted")
    print("V296_SLEW_SPEF_JOIN_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 4:
        raise SystemExit("Usage: map_slew_to_spef.py VIOLATOR_REPORT SPEF OUTPUT_JSON")
    report, spef, dest = (Path(x) for x in sys.argv[1:])
    try:
        result = analyze(report.read_text(), spef.read_text())
        result["provenance"] = {
            "slew_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            "spef_sha256": hashlib.sha256(spef.read_bytes()).hexdigest()}
    except (ValueError, OSError, UnicodeError) as exc:
        result = {"decision": "SLEW_PIN_TO_SPEF_MAP_FAIL", "error": str(exc)}
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "groups"}, indent=2))
    if result["decision"] != "SLEW_PIN_TO_SPEF_MAP_PASS":
        raise SystemExit(3)
