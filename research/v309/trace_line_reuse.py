#!/usr/bin/env python3
"""V309: source-conditional V100 LDG line identity; NOT GPU cache/DRAM traffic.

Historical producer M=A&P is unverified. Ambiguous rows are EXCLUDED, never
treated as zero-demand. Each trace file is a separate address identity domain.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import io
import json
from pathlib import PurePosixPath
import tarfile

from legacy_predicate_mask_provenance import address_tail, MAX64
from v100_sass_profile import EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name

LINE_BYTES = 128

def certified_addresses(record):
    mask, op, width, fmt, data = record
    if mask <= 0 or width <= 0:
        raise ValueError("invalid active memory record")
    visible = [lane for lane in range(32) if mask & (1 << lane)]
    k = len(visible)
    if fmt == 0:
        n = len(data)
        if not k <= n <= 32:
            raise ValueError("source-incompatible format0 token count")
        tokens = [int(t, 0) for t in data]
        if any(x < 0 or x > MAX64 for x in tokens):
            raise ValueError("format0 token outside uint64")
        if n == k:
            addresses = tokens
        elif n == 32:
            addresses = [tokens[lane] for lane in visible]
        else:
            return None, "excluded_format0_hidden_lanes"
    elif fmt == 1:
        if len(data) != 2:
            raise ValueError("format1 needs base and stride")
        base, stride = (int(t, 0) for t in data)
        if base < 0 or base > MAX64:
            raise ValueError("format1 base outside uint64")
        if mask & 1:
            addresses = [base + lane * stride for lane in visible]
        elif stride == 0:
            addresses = [base] * k
        else:
            return None, "excluded_format1_shifted_start"
    else:
        raise ValueError("unsupported memory address format")
    if len(addresses) != k or any(a < 0 or a > MAX64 or a + width - 1 > MAX64 for a in addresses):
        raise ValueError("visible memory address outside uint64")
    return tuple(addresses), "certified_format" + str(fmt)

def instruction_lines(addresses, width, line_bytes=LINE_BYTES):
    if width <= 0 or line_bytes <= 0 or not addresses:
        raise ValueError("invalid line footprint request")
    if any(a < 0 or a > MAX64 or a + width - 1 > MAX64 for a in addresses):
        raise ValueError("line footprint uint64 overflow")
    return frozenset(line for a in addresses
                     for line in range(a // line_bytes, (a + width - 1) // line_bytes + 1))

def summarize_file(records):
    c = Counter()
    unique = set()
    for rec in records:
        c["global_proxy"] += 1
        mask, op, width, fmt, data = rec
        if op.split(".", 1)[0] != "LDG":
            continue
        c["ldg_rows"] += 1
        addrs, status = certified_addresses(rec)
        c[status] += 1
        if addrs is None:
            continue
        lines = instruction_lines(addrs, width)
        if not lines:
            raise AssertionError("certified load has empty footprint")
        c["certified_rows"] += 1
        c["line_references"] += len(lines)
        unique.update(lines)
    c["unique_lines"] = len(unique)
    c["duplicate_line_references"] = c["line_references"] - len(unique)
    if c["duplicate_line_references"] < 0:
        raise AssertionError("negative line reuse")
    if c["certified_rows"] + c["excluded_format0_hidden_lanes"] + c["excluded_format1_shifted_start"] != c["ldg_rows"]:
        raise AssertionError("LDG row classification not conserved")
    return c

def fraction_string(num, den):
    return str(Fraction(num, den)) if den else None

def scan(path):
    with open(path, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive size or SHA-256 mismatch")
    apps = defaultdict(Counter)
    file_rows = []
    nfiles = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():
                raise ValueError("device archive member")
            if not member.isfile() or not member.name.endswith(".traceg"):
                continue
            if member.size < 0 or member.size > 2 * 1024**3:
                raise ValueError("oversized trace member")
            parts = PurePosixPath(member.name).parts
            if len(parts) < 5:
                raise ValueError("unknown trace path")
            nfiles += 1
            fp = tar.extractfile(member)
            if fp is None:
                raise ValueError("unreadable trace member")
            def records():
                for lineno, raw in enumerate(fp, 1):
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line or not line[0].isdigit():
                        continue
                    try:
                        rec = address_tail(line)
                        if rec is not None:
                            yield rec
                    except (ValueError, IndexError) as exc:
                        raise ValueError(f"{member.name}:{lineno}: {exc}") from exc
            try:
                c = summarize_file(records())
            except (ValueError, IndexError, AssertionError) as exc:
                raise ValueError(f"{member.name}: {exc}") from exc
            apps[parts[2]].update(c)
            file_rows.append({"application": parts[2], "trace": member.name,
                              "ldg_rows": c["ldg_rows"], "certified_rows": c["certified_rows"],
                              "line_references": c["line_references"],
                              "unique_lines": c["unique_lines"],
                              "reuse_fraction": fraction_string(c["duplicate_line_references"], c["line_references"])})
    g = Counter()
    for c in apps.values():
        g.update(c)
    if nfiles != 210 or g["global_proxy"] != 240465:
        raise AssertionError(f"frozen corpus conservation failed: files={nfiles}, global={g['global_proxy']}")
    if sum(c["ldg_rows"] for c in apps.values()) != g["ldg_rows"]:
        raise AssertionError("application sum mismatch")
    if any(c["certified_rows"] > c["ldg_rows"] for c in apps.values()):
        raise AssertionError("impossible coverage")
    return {
        "status": "PASS", "evidence_tier": "source_conditional_LDG_subset_line_identity_NOT_GPU_cache_or_DRAM",
        "archive_sha256": EXPECTED_SHA, "producer_identity_verified": False,
        "trace_files": nfiles, "hypothetical_line_bytes": LINE_BYTES,
        "global": {**dict(g), "coverage_fraction": fraction_string(g["certified_rows"], g["ldg_rows"]),
                   "reuse_fraction": fraction_string(g["duplicate_line_references"], g["line_references"])},
        "applications": {app: {**dict(c), "coverage_fraction": fraction_string(c["certified_rows"], c["ldg_rows"]),
                               "reuse_fraction": fraction_string(c["duplicate_line_references"], c["line_references"])}
                         for app, c in sorted(apps.items())},
        "files_without_certified_LDG": sum(row["certified_rows"] == 0 for row in file_rows),
        "files": sorted(file_rows, key=lambda row: row["trace"]),
        "limits": [
            "historical producer source hypothesis is unverified",
            "certified subset omits ambiguous LDG rows; no full-workload reuse fraction inferred",
            "trace files treated as independent address identity domains",
            "trace order is not GPU memory-system scheduling order",
            "128-byte line is a sensitivity assumption, not an authenticated hardware mapping",
            "line identity is not measured L1/L2/DRAM traffic, cache hit rate, stalls or speedup",
            "no new hardware mechanism, physical RTL validation or prospective holdout",
        ],
    }

def selftest():
    # Independent byte-level oracle.
    cases = 0
    for width in (1, 4, 8, 16):
        for offset in (0, 31, 127):
            for base in (0, 128, 1024):
                addresses = (base + offset, base + offset + 7)
                expected = {b // LINE_BYTES for a in addresses for b in range(a, a + width)}
                assert instruction_lines(addresses, width) == expected
                cases += 1
    # Frozen synthetic high-reuse and no-reuse regimes.
    for family in ("hot_reuse", "cold_stream"):
        refs = [set(range(4)) if family == "hot_reuse"
                else set(range(i * 4, i * 4 + 4)) for i in range(64)]
        r = sum(map(len, refs))
        u = len(set().union(*refs))
        assert (r, u, r - u) == ((256, 4, 252) if family == "hot_reuse" else (256, 256, 0))
        assert Fraction(r - u, r) == (Fraction(63, 64) if family == "hot_reuse" else 0)
    def row(mask, fmt, data, op="LDG.E", width=4):
        return (mask, op, width, fmt, data)
    assert certified_addresses(row(0b11, 0, ["0x1000", "0x1080"]))[0] == (0x1000, 0x1080)
    assert certified_addresses(row(0b10, 0, ["0x1000", "0x1080"]))[0] is None
    assert certified_addresses(row(0b10, 0, ["0x1000"] * 32))[0] == (0x1000,)
    assert certified_addresses(row(0b11, 1, ["0x1000", "4"]))[0] == (0x1000, 0x1004)
    assert certified_addresses(row(0b10, 1, ["0x1000", "4"]))[0] is None
    assert certified_addresses(row(0b10, 1, ["0x1000", "0"]))[0] == (0x1000,)
    assert summarize_file([row(1, 0, ["0x1000"]), row(1, 0, ["0x1000"])])["duplicate_line_references"] == 1
    assert sum(summarize_file([row(1, 0, ["0x1000"])])["unique_lines"] for _ in range(2)) == 2
    invalids = [row(0b11, 0, ["0x1000"]), row(1, 0, ["-1"]),
                row(1, 0, ["0xffffffffffffffff"], width=8),
                row(1, 1, ["0xffffffffffffffff", "0"], width=8),
                row(1, 2, ["0x1000"])]
    for bad in invalids:
        try:
            certified_addresses(bad)
        except ValueError:
            continue
        raise AssertionError("malformed address record accepted")
    return {"status": "PASS", "independent_byte_oracle_cases": cases,
            "frozen_synthetic_regimes": 2, "invalid_address_refusals": len(invalids),
            "file_domain_separation": "PASS", "source_ambiguity_refusal": "PASS"}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), indent=2, sort_keys=True))
    if args.archive:
        print(json.dumps(scan(args.archive), indent=2, sort_keys=True))
    elif not args.selftest:
        p.error("archive required")
