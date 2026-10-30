#!/usr/bin/env python3
"""Independent V309 SASS memory-sector redecoder. Does not import primary code."""
from __future__ import annotations
import argparse
from collections import defaultdict
import copy
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath

SHA = "aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1"
CAP = 67108864
NAMES = ("active_memory", "global_proxy", "other_memory", "active_lanes",
         "requested_unique_bytes", "sectors32", "sectors64", "lines128",
         "perfect_pack_floor32", "packing_slack_rows", "format0",
         "format1", "format2", "trace_files")
STEMS = {"LDG", "STG", "ATOM", "RED"}


def zero():
    return {k: 0 for k in NAMES}


def independent_row(line):
    t = line.split()
    if len(t) < 10:
        raise ValueError("short")
    mask = int(t[5], 16)
    if not 0 <= mask <= 0xffffffff:
        raise ValueError("mask")
    nd = int(t[6])
    if not 0 <= nd <= 16 or any(not r.startswith("R") for r in t[7:7+nd]):
        raise ValueError("dest")
    i = 7 + nd
    op = t[i]
    ns = int(t[i+1])
    if not 0 <= ns <= 16 or any(not r.startswith("R") for r in t[i+2:i+2+ns]):
        raise ValueError("source")
    i += ns + 2
    width = int(t[i])
    if width < 0:
        raise ValueError("width")
    if not width or not mask:
        return mask, op, width, None
    data = t[i+1:]
    fmt = int(data[0])
    lanes = [j for j in range(32) if mask & (1 << j)]
    payload = data[1:]
    if fmt == 0:
        if len(payload) != len(lanes):
            raise ValueError("list length")
        addrs = [int(x, 0) for x in payload]
    elif fmt == 1:
        if len(payload) != 2 or lanes[-1] - lanes[0] + 1 != len(lanes):
            raise ValueError("stride length")
        b, s = int(payload[0], 0), int(payload[1], 0)
        addrs = [b + j*s for j in range(len(lanes))]
    elif fmt == 2:
        if len(payload) != len(lanes):
            raise ValueError("delta length")
        addrs = [int(payload[0], 0)]
        for x in payload[1:]:
            addrs += [addrs[-1] + int(x, 0)]
    else:
        raise ValueError("unknown format")
    if any(a < 0 or a + width > 2**64 for a in addrs):
        raise ValueError("range")
    return mask, op, width, (fmt, addrs)


def independent_add(acc, row):
    mask, op, width, record = row
    if not mask or not width:
        return
    acc["active_memory"] += 1
    if op.split(".")[0] not in STEMS:
        acc["other_memory"] += 1
        return
    fmt, addrs = record
    acc["global_proxy"] += 1
    acc["active_lanes"] += mask.bit_count()
    acc["format"+str(fmt)] += 1
    spans = sorted((a, a+width) for a in addrs)
    merged = []
    for a, b in spans:
        if not merged or a > merged[-1][1]:
            merged.append([a, b])
        else:
            merged[-1][1] = max(merged[-1][1], b)
    distinct = sum(b-a for a,b in merged)
    acc["requested_unique_bytes"] += distinct
    for gran, name in ((32, "sectors32"), (64, "sectors64"), (128, "lines128")):
        occupied = set()
        for a,b in spans:
            occupied.update(range(a//gran, (b-1)//gran + 1))
        acc[name] += len(occupied)
        if gran == 32:
            floor = (distinct+31)//32
            acc["perfect_pack_floor32"] += floor
            acc["packing_slack_rows"] += len(occupied) > floor


def check(report, independent):
    if report.get("archive_sha256") != SHA:
        raise ValueError("SHA mismatch")
    if report.get("fixed_address_ideal_coalescer_improvement_sectors") != 0:
        raise ValueError("invalid ideal coalescer control")
    if report.get("prospective_holdout") != "NONE; all Rodinia families previously inspected":
        raise ValueError("false prospective claim")
    for field in ("global", "applications"):
        r = report.get(field, {})
        e = independent[field]
        if set(r) != set(e):
            raise ValueError("application or global key mismatch")
        for app in e if field == "applications" else (None,):
            observed = r[app] if app is not None else r
            expected = e[app] if app is not None else e
            for k in NAMES:
                if observed.get(k) != expected[k]:
                    raise ValueError(f"independent mismatch {field}/{app}/{k}")
            if expected["global_proxy"]:
                util = expected["requested_unique_bytes"]/(32*expected["sectors32"])
                slack = expected["packing_slack_rows"]/expected["global_proxy"]
                if observed.get("sector_utilization") != util or observed.get("packing_slack_share") != slack:
                    raise ValueError("fraction mismatch")
                if observed.get("layout_only_sector_slack") != expected["sectors32"]-expected["perfect_pack_floor32"]:
                    raise ValueError("slack mismatch")
    return {"audit": "PASS", "global_proxy": independent["global"]["global_proxy"],
            "sectors32": independent["global"]["sectors32"],
            "layout_slack": independent["global"]["sectors32"]-independent["global"]["perfect_pack_floor32"]}


def recompute(path):
    with open(path, "rb") as f:
        blob = f.read(CAP+1)
    if len(blob) > CAP or hashlib.sha256(blob).hexdigest() != SHA:
        raise ValueError("archive digest or size")
    apps = defaultdict(zero)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar:
            if m.name.startswith("/") or ".." in m.name.split("/") or m.isdev():
                raise ValueError("unsafe archive")
            if not m.isfile() or not m.name.endswith(".traceg"):
                continue
            if m.size > 2*1024**3:
                raise ValueError("oversized trace")
            parts = PurePosixPath(m.name).parts
            if len(parts) < 5:
                raise ValueError("path")
            a = apps[parts[2]]
            a["trace_files"] += 1
            f = tar.extractfile(m)
            if f is None:
                raise ValueError("unreadable")
            for line_no, raw in enumerate(f, 1):
                s = raw.decode("utf-8", errors="replace").strip()
                if s and s[0].isdigit():
                    try:
                        independent_add(a, independent_row(s))
                    except (ValueError, IndexError) as exc:
                        raise ValueError(f"{m.name}:{line_no}: {exc}") from exc
    g = zero()
    for a in apps.values():
        for k in NAMES:
            g[k] += a[k]
    if g["active_memory"] != 484259 or g["trace_files"] != 210:
        raise ValueError("memory conservation")
    return {"global": g, "applications": dict(sorted(apps.items()))}


def selftest():
    a = zero()
    for s in (
        "0 0 0 0 0010 ffffffff 0 LDG.E 1 R1 4 1 0x1000 4",
        "0 0 0 0 0010 00000005 0 STG.E 1 R1 4 2 0x1000 64",
        "0 0 0 0 0010 00000003 0 ATOM.E 1 R1 4 0 0x1000 0x1000",
    ):
        independent_add(a, independent_row(s))
    assert a["global_proxy"] == 3 and a["sectors32"] == 7
    expected = {"global": a, "applications": {"fixture": a}}
    summary = {"sector_utilization": a["requested_unique_bytes"]/(32*a["sectors32"]),
               "packing_slack_share": a["packing_slack_rows"]/a["global_proxy"],
               "layout_only_sector_slack": a["sectors32"]-a["perfect_pack_floor32"]}
    report = {"archive_sha256": SHA, "global": {**a, **summary},
              "applications": {"fixture": {**a, **summary}},
              "fixed_address_ideal_coalescer_improvement_sectors": 0,
              "prospective_holdout": "NONE; all Rodinia families previously inspected"}
    check(report, expected)
    mutants = []
    for key in NAMES:
        x = copy.deepcopy(report)
        x["global"][key] += 1
        mutants.append(x)
    for key, val in (("archive_sha256", "bad"),
                     ("fixed_address_ideal_coalescer_improvement_sectors", 1),
                     ("prospective_holdout", "unseen")):
        x = copy.deepcopy(report)
        x[key] = val
        mutants.append(x)
    for x in mutants:
        try:
            check(x, expected)
        except ValueError:
            pass
        else:
            raise AssertionError("mutant accepted")
    return {"selftest": "PASS", "mutants_rejected": len(mutants)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("report", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), sort_keys=True))
    if args.archive and args.report:
        with open(args.report) as f:
            report = json.load(f)
        print(json.dumps(check(report, recompute(args.archive)), sort_keys=True, indent=2))
    elif not args.selftest:
        p.error("archive and report required")
