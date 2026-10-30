#!/usr/bin/env python3
"""V309: authenticated SASS address topology, NOT measured memory transactions.
A fixed-address ideal coalescer is the equal-resource lower-bound control.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath

from v100_sass_profile import EXPECTED_SHA, parse_row
from v100_trace_inventory import MAX_ARCHIVE, validate_name

FIELDS = ("active_memory", "global_proxy", "other_memory", "active_lanes",
          "requested_unique_bytes", "sectors32", "sectors64", "lines128",
          "perfect_pack_floor32", "packing_slack_rows", "format0",
          "format1", "format2", "trace_files")
GLOBAL_STEMS = frozenset(("LDG", "STG", "ATOM", "RED"))
MAX_ADDR = (1 << 64) - 1


def fresh():
    return {k: 0 for k in FIELDS}


def parse_address_record(line):
    """Decode only documented old-format 0/1/2 memory addresses.
    No extra tokens are accepted: unsupported trace versions fail closed.
    """
    mask, opcode, _, width = parse_row(line)
    if not mask or width == 0:
        return mask, opcode, width, ()
    t = line.split()
    nd = int(t[6])
    op_i = 7 + nd
    ns = int(t[op_i + 1])
    tail = t[op_i + 3 + ns:]
    if len(tail) < 2:
        raise ValueError("missing address compression and payload")
    fmt = int(tail[0])
    data = tail[1:]
    lanes = [i for i in range(32) if (mask >> i) & 1]
    n = len(lanes)
    if fmt == 0:
        if len(data) == 32:
            addrs = [int(data[i], 0) for i in lanes]
        elif len(data) == n:
            addrs = [int(x, 0) for x in data]
        else:
            raise ValueError("format0 address count mismatch")
    elif fmt == 1:
        if len(data) != 2 or lanes != list(range(lanes[0], lanes[-1] + 1)):
            raise ValueError("format1 needs contiguous active lanes and base/stride")
        base, stride = int(data[0], 0), int(data[1], 0)
        addrs = [base + i * stride for i in range(n)]
    elif fmt == 2:
        if len(data) != n:
            raise ValueError("format2 needs base and n-1 deltas")
        base = int(data[0], 0)
        addrs = [base]
        for delta in data[1:]:
            addrs.append(addrs[-1] + int(delta, 0))
    else:
        raise ValueError("unsupported address format: " + str(fmt))
    if any(a < 0 or a > MAX_ADDR or a + width - 1 > MAX_ADDR for a in addrs):
        raise ValueError("address or interval outside 64-bit space")
    return mask, opcode, width, (fmt, tuple(addrs))


def union_bytes(addresses, width):
    intervals = sorted((a, a + width) for a in addresses)
    total = 0
    lo = hi = None
    for a, b in intervals:
        if lo is None:
            lo, hi = a, b
        elif a > hi:
            total += hi - lo
            lo, hi = a, b
        else:
            hi = max(hi, b)
    if lo is not None:
        total += hi - lo
    return total


def touched(addresses, width, sector):
    return len({i for a in addresses for i in range(a // sector,
                (a + width - 1) // sector + 1)})


def account(acc, row):
    mask, opcode, width, record = row
    if not mask or not width:
        return
    acc["active_memory"] += 1
    if opcode.split(".", 1)[0] not in GLOBAL_STEMS:
        acc["other_memory"] += 1
        return
    fmt, addrs = record
    n = mask.bit_count()
    assert len(addrs) == n
    acc["global_proxy"] += 1
    acc["active_lanes"] += n
    acc["format" + str(fmt)] += 1
    unique = union_bytes(addrs, width)
    s32 = touched(addrs, width, 32)
    acc["requested_unique_bytes"] += unique
    acc["sectors32"] += s32
    acc["sectors64"] += touched(addrs, width, 64)
    acc["lines128"] += touched(addrs, width, 128)
    floor = (unique + 31) // 32
    if floor > s32:
        raise AssertionError("sector floor exceeded observed footprint")
    acc["perfect_pack_floor32"] += floor
    acc["packing_slack_rows"] += (s32 > floor)


def summarize(acc):
    if not acc["global_proxy"]:
        return {"sector_utilization": None, "packing_slack_share": None}
    return {
        "sector_utilization": acc["requested_unique_bytes"] / (32 * acc["sectors32"]),
        "packing_slack_share": acc["packing_slack_rows"] / acc["global_proxy"],
        "layout_only_sector_slack": acc["sectors32"] - acc["perfect_pack_floor32"],
    }


def profile(path):
    with open(path, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive size or frozen SHA-256 mismatch")
    apps = defaultdict(fresh)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():
                raise ValueError("device archive member")
            if not member.isfile() or not member.name.endswith(".traceg"):
                continue
            if member.size > 2 * 1024**3:
                raise ValueError("oversized trace member")
            parts = PurePosixPath(member.name).parts
            if len(parts) < 5:
                raise ValueError("unknown trace path")
            acc = apps[parts[2]]
            acc["trace_files"] += 1
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError("unreadable trace")
            for line_no, raw in enumerate(stream, 1):
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or not line[0].isdigit():
                    continue
                try:
                    account(acc, parse_address_record(line))
                except (ValueError, IndexError, AssertionError) as exc:
                    raise ValueError(f"{member.name}:{line_no}: {exc}; raw={line[:360]!r}") from exc
    overall = fresh()
    for acc in apps.values():
        for k in FIELDS:
            overall[k] += acc[k]
    if overall["trace_files"] != 210 or overall["active_memory"] != 484259:
        raise ValueError("full corpus memory-row conservation failed")
    if not overall["global_proxy"]:
        raise ValueError("no global-proxy memory operations")
    return {
        "evidence_tier": "authentic_V100_SASS_address_topology_NOT_transactions_or_stalls",
        "archive_sha256": EXPECTED_SHA,
        "global": {**overall, **summarize(overall)},
        "applications": {k: {**v, **summarize(v)} for k, v in sorted(apps.items())},
        "fixed_address_ideal_coalescer_improvement_sectors": 0,
        "prospective_holdout": "NONE; all Rodinia families previously inspected",
        "limits": [
            "global-proxy opcode stems are a classification, not a cache-path proof",
            "32/64/128-byte granularities are sensitivity assumptions",
            "perfect packing requires changing memory addresses or layout",
            "no measured sectors, counters, bandwidth, timing, occupancy, or RTX5090 claims",
        ],
    }


def selftest():
    a = fresh()
    base = "0 0 0 0 0010 "
    full = base + "ffffffff 0 LDG.E 1 R1 4 1 0x1000 4"
    row = parse_address_record(full)
    assert len(row[3][1]) == 32 and row[3][1][-1] == 0x107c
    account(a, row)
    assert a["sectors32"] == 4 and a["perfect_pack_floor32"] == 4
    sparse = base + "00000005 0 STG.E 1 R1 4 2 0x1000 64"
    account(a, parse_address_record(sparse))
    assert a["sectors32"] == 6 and a["packing_slack_rows"] == 1
    repeated = base + "00000003 0 ATOM.E 1 R1 4 0 0x1000 0x1000"
    account(a, parse_address_record(repeated))
    assert a["requested_unique_bytes"] == 128 + 8 + 4
    assert a["sectors32"] == 7
    assert a["perfect_pack_floor32"] == 6
    account(a, parse_address_record(base + "00000003 0 LDS 1 R1 4 0 0x1000 0x1004"))
    # Legacy tracer format-0 may include inactive lane slots.
    full_slots = ["0x1000"] + ["0xdead"] * 31
    slot_row = parse_address_record(base + "00000001 0 LDG 1 R1 4 0 " + " ".join(full_slots))
    assert slot_row[3][1] == (0x1000,)
    account(a, slot_row)
    assert a["other_memory"] == 1 and a["global_proxy"] == 4
    mutants = [
        base + "00000003 0 LDG 1 R1 4 0 0x1000",
        base + "00000005 0 LDG 1 R1 4 1 0x1000 4",
        base + "00000003 0 LDG 1 R1 4 2 0x1000",
        base + "00000003 0 LDG 1 R1 4 3 0x1000 4",
        base + "00000003 0 LDG 1 R1 4 0 0xffffffffffffffff 0x1000",
        base + "00000003 0 LDG 1 R1 4 2 0x1000 -5000",
    ]
    for bad in mutants:
        try:
            parse_address_record(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted corrupt address record: " + bad)
    # Independent byte-enumeration oracle for small synthetic intervals.
    for width in (1, 2, 4, 8, 16):
        for stride in (0, 1, 3, 17, 32, 63):
            addresses = [0x1003 + stride * i for i in range(4)]
            byteset = {b for addr in addresses for b in range(addr, addr + width)}
            assert union_bytes(addresses, width) == len(byteset)
            for gran in (32, 64, 128):
                assert touched(addresses, width, gran) == len({b // gran for b in byteset})
    return {"selftest": "PASS", "negative_mutants": len(mutants),
            "independent_byte_oracle_cases": 5 * 6 * 3,
            "fixture_global_proxy": a["global_proxy"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), sort_keys=True))
    if args.archive:
        print(json.dumps(profile(args.archive), sort_keys=True, indent=2))
    elif not args.selftest:
        p.error("archive required")
