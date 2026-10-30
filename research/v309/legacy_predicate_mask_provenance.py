#!/usr/bin/env python3
"""V309: falsify legacy SASS address identifiability under a dated producer snapshot.

This is a source-conditional provenance test, NOT a GPU performance result.
The 2020-03-09 tracer prints (active_mask & predicate_mask) but serializes
memory addresses using active_mask alone. It does NOT prove that this exact
commit produced the 2020-03-18 archive.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath

from v100_sass_profile import EXPECTED_SHA, parse_row
from v100_trace_inventory import MAX_ARCHIVE, validate_name

PRODUCER_COMMIT = "0e2fddcdef37fc59ad786553892b75567a5f2cdb"
GLOBAL = frozenset(("LDG", "STG", "ATOM", "RED"))
MAX64 = (1 << 64) - 1


def address_tail(line):
    t = line.split()
    mask, op, _, width = parse_row(line)
    if not mask or not width or op.split(".", 1)[0] not in GLOBAL:
        return None
    pos = 7 + int(t[6])
    pos += 2 + int(t[pos + 1])
    data = t[pos + 1:]
    if len(data) < 2:
        raise ValueError("missing memory compression payload")
    fmt = int(data[0])
    if fmt not in (0, 1, 2):
        raise ValueError("unsupported format")
    if fmt == 1 and len(data) != 3:
        raise ValueError("format1 must contain base and stride")
    if fmt == 0 and not data[1:]:
        raise ValueError("empty explicit address list")
    return mask, op, width, fmt, data[1:]


def sector_count(addrs, width, granularity=32):
    return len({s for a in addrs for s in range(a // granularity, (a + width - 1) // granularity + 1)})


def format1_sector_envelope(mask, width, base, stride, granularity=32):
    """All possible first-active-lane offsets consistent with printed M=A&P.

    A is assumed contiguous and begins at s <= first set bit of M.
    For every s, address(lane) = base + (lane-s)*stride. No assertion that
    any one s is the actual hidden A. Source-conditional envelope only.
    """
    lanes = [i for i in range(32) if mask & (1 << i)]
    if not lanes:
        raise ValueError("empty active mask")
    vals = []
    for first in range(lanes[0] + 1):
        # Historical format1 requires at least two original active lanes.
        if first == lanes[0] == 31:
            continue
        addrs = [base + (lane - first) * stride for lane in lanes]
        if any(a < 0 or a > MAX64 or a + width - 1 > MAX64 for a in addrs):
            continue
        vals.append(sector_count(addrs, width, granularity))
    if not vals:
        raise ValueError("no source-compatible candidate addresses")
    return min(vals), max(vals), len(vals)


def fresh():
    return Counter()


def account(acc, record):
    if record is None:
        return
    mask, op, width, fmt, data = record
    k = mask.bit_count()
    acc["global_proxy"] += 1
    acc["format_" + str(fmt)] += 1
    if fmt == 0:
        n = len(data)
        if n < k or n > 32:
            acc["format0_source_incompatible"] += 1
            return
        if any(int(x, 0) < 0 or int(x, 0) > MAX64 for x in data):
            raise ValueError("format0 address outside uint64")
        if n == k:
            acc["format0_exact_under_hypothesis"] += 1
            addrs = [int(x, 0) for x in data]
            if any(a + width - 1 > MAX64 for a in addrs):
                raise ValueError("format0 interval overflow")
            acc["format0_exact_sectors32"] += sector_count(addrs, width)
        else:
            acc["format0_predicate_hidden"] += 1
            acc["format0_hidden_address_tokens"] += n - k
        return
    if fmt == 1:
        base, stride = (int(x, 0) for x in data)
        if base < 0 or base > MAX64:
            raise ValueError("format1 base outside uint64")
        lo, hi, candidates = format1_sector_envelope(mask, width, base, stride)
        acc["format1_sector_lower32"] += lo
        acc["format1_sector_upper32"] += hi
        acc["format1_candidate_starts"] += candidates
        if lo == hi:
            acc["format1_sector_identifiable32"] += 1
        else:
            acc["format1_sector_ambiguous32"] += 1
            acc["format1_sector_uncertainty32"] += hi - lo
        if mask & 1:
            acc["format1_first_lane_zero"] += 1
        return
    acc["format2_unresolved_producer"] += 1


def scan(path):
    with open(path, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive SHA-256 or size mismatch")
    apps = defaultdict(fresh)
    nfiles = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():
                raise ValueError("unsafe archive member")
            if not member.isfile() or not member.name.endswith(".traceg"):
                continue
            if member.size > 2 * 1024**3:
                raise ValueError("oversized trace member")
            parts = PurePosixPath(member.name).parts
            if len(parts) < 5:
                raise ValueError("unexpected trace path")
            nfiles += 1
            app = apps[parts[2]]
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError("unreadable trace member")
            for line_no, raw in enumerate(stream, 1):
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or not line[0].isdigit():
                    continue
                try:
                    account(app, address_tail(line))
                except (ValueError, IndexError) as exc:
                    raise ValueError(f"{member.name}:{line_no}: {exc}") from exc
    g = Counter()
    for a in apps.values():
        g.update(a)
    if nfiles != 210 or g["global_proxy"] != 240465:
        raise ValueError("frozen corpus conservation failed")
    if g["format0_predicate_hidden"] == 0:
        raise ValueError("expected historical predicate-mask discrepancy not observed")
    return {
        "evidence_tier": "dated_source_conditional_trace_provenance_NOT_measured_GPU",
        "source_snapshot_commit": PRODUCER_COMMIT,
        "source_snapshot_is_proven_producer": False,
        "archive_sha256": EXPECTED_SHA,
        "trace_files": nfiles,
        "global": dict(g),
        "applications": {k: dict(v) for k, v in sorted(apps.items())},
        "limits": [
            "The producer commit is a hypothesis, not established archive provenance",
            "Original active_mask and predicate_mask are absent from serialized rows",
            "Format0 recovery only when payload count equals printed-mask popcount",
            "Format1 sector bounds assume contiguous original active_mask",
            "Format2 has no decoder certified against this historical source",
            "Prior 54.01% decoded address coverage may include conditionally shifted format1 addresses",
            "No hardware mechanism, measured counters, cycles, or RTX 5090 inference"
        ],
    }


def selftest():
    # 2020 source: printed M=A&P, but fmt0 writes addresses for A.
    m = 0b0001
    a = 0b1111
    assert (a & m) == m
    x = fresh()
    account(x, (m, "LDG.E", 4, 0, ["0x1000", "0x1020", "0x1040", "0x1060"]))
    assert x["format0_predicate_hidden"] == 1 and x["format0_hidden_address_tokens"] == 3
    account(x, (0b0011, "LDG.E", 4, 0, ["0x1000", "0x1020"]))
    assert x["format0_exact_under_hypothesis"] == 1 and x["format0_exact_sectors32"] == 2
    # M=lanes 2,3 may arise from A=0..3 or A=2..3; base shifts.
    lo, hi, n = format1_sector_envelope(0b1100, 4, 0x101c, 4)
    assert (lo, hi, n) == (1, 2, 3), (lo, hi, n)
    # If the first visible lane is zero, the base cannot shift earlier.
    assert format1_sector_envelope(0b0011, 4, 0x101c, 4) == (2, 2, 1)
    # Brute-force every allowed start, verifying min/max against byte sets.
    for mask in range(1, 256):
        for width in (1, 4, 8):
            for stride in (0, 4, 32):
                base = 0x1003
                lo, hi, _ = format1_sector_envelope(mask, width, base, stride)
                lanes = [i for i in range(8) if mask & (1 << i)]
                oracle = []
                for start in range(lanes[0] + 1):
                    addresses = [base + (lane - start) * stride for lane in lanes]
                    byte_set = {b for address in addresses for b in range(address, address + width)}
                    oracle.append(len({b // 32 for b in byte_set}))
                assert (lo, hi) == (min(oracle), max(oracle))
    return {"selftest": "PASS", "envelope_cases": 255 * 3 * 3,
            "source_conditional_format0_counterexample": "PASS",
            "source_conditional_format1_counterexample": "PASS"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), sort_keys=True))
    if args.archive:
        print(json.dumps(scan(args.archive), indent=2, sort_keys=True))
    elif not args.selftest:
        p.error("archive required")
