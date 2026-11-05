#!/usr/bin/env python3
"""V309: source-conditional full-corpus 32B sector-count envelopes, not GPU stalls.

Historical producer hypothesis: printed M = A & P, format-0 address tokens
are in ascending unmasked-A lane order. A and P are absent from the archive.
Exact enumeration is capped; the fallback is a *conservative* bound.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from itertools import combinations
from math import comb
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath

from legacy_predicate_mask_provenance import (
    address_tail, format1_sector_envelope, MAX64, PRODUCER_COMMIT
)
from v100_sass_profile import EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name

MAX_CHOICES_PER_ROW = 4096
MAX_TOTAL_CHOICES = 2_000_000


def sectors(addr, width):
    if addr < 0 or addr > MAX64 or width <= 0:
        raise ValueError("invalid uint64 address token or width")
    if addr + width - 1 > MAX64:
        return None  # unknown width-extended footprint; do not invent wrap semantics
    return frozenset(range(addr // 32, (addr + width - 1) // 32 + 1))


def possible_ranks(mask, n, lane, lanes=32):
    """Exact possible rank indices for a mandatory visible lane.

    For h=n-popcount(M) hidden lanes, h_before may range from
    max(0,h-optional_after) to min(h,optional_before).
    """
    k = mask.bit_count()
    if not mask & (1 << lane) or not (k <= n <= lanes):
        raise ValueError("source-incompatible rank query")
    before = (mask & ((1 << lane) - 1)).bit_count()
    after = k - before - 1
    h = n - k
    optional_before = lane - before
    optional_after = lanes - lane - 1 - after
    lo = before + max(0, h - optional_after)
    hi = before + min(h, optional_before)
    if lo > hi or hi >= n:
        raise AssertionError("impossible source-compatible rank")
    return range(lo, hi + 1)


def format0_envelope(mask, width, tokens, budget, lanes=32):
    """Return (lower, upper, sharp, enumerated_A, method).

    A is any superset of M with popcount(A)=len(tokens). Only printed-mask
    lanes contribute to sectors. For unenumerated rows, bounds contain truth.
    """
    k = mask.bit_count()
    n = len(tokens)
    if mask <= 0 or mask >= 1 << lanes or not (k <= n <= lanes):
        raise ValueError("format0 source-incompatible address cardinality")
    ss = [sectors(int(t, 0), width) for t in tokens]
    visible = [i for i in range(lanes) if mask & (1 << i)]
    h = n - k
    # The historical tracer may serialize garbage/sentinel addresses for
    # predicated-off lanes. Reject no row solely for such a hidden token.
    # If an overflowing token could be visible, conservatively bound rather
    # than interpreting 64-bit address wrap as an actual memory transaction.
    if any(ss[j] is None for lane in visible
           for j in possible_ranks(mask, n, lane, lanes)):
        return 1, k * ((width + 30) // 32 + 1), False, 0, "overflow_unknown"
    if h == 0 or n == lanes:
        a = mask if h == 0 else (1 << lanes) - 1
        touched = set()
        for lane in visible:
            touched.update(ss[(a & ((1 << lane) - 1)).bit_count()])
        count = len(touched)
        return count, count, True, 0, "unique_A"

    if k == 1:
        ranks = possible_ranks(mask, n, visible[0], lanes)
        counts = [len(ss[j]) for j in ranks]
        return min(counts), max(counts), True, 0, "one_visible_exact"

    choices = comb(lanes - k, h)
    if choices <= MAX_CHOICES_PER_ROW and choices <= budget:
        optional = [i for i in range(lanes) if not (mask & (1 << i))]
        lower = 10**9
        upper = 0
        used = 0
        for extra in combinations(optional, h):
            a = mask
            for lane in extra:
                a |= 1 << lane
            touched = set()
            for lane in visible:
                touched.update(ss[(a & ((1 << lane) - 1)).bit_count()])
            count = len(touched)
            lower = min(lower, count)
            upper = max(upper, count)
            used += 1
        if used != choices:
            raise AssertionError("incomplete exact enumeration")
        return lower, upper, True, used, "enumerated_exact"

    # Certified conservative bounds. Each visible lane's possible token
    # positions are exact, but their simultaneous assignments are coupled.
    guaranteed = set()
    possible = set()
    max_sum = 0
    min_single = 1
    for lane in visible:
        candidate = [ss[j] for j in possible_ranks(mask, n, lane, lanes)]
        intersection = set(candidate[0])
        union = set()
        for item in candidate:
            intersection.intersection_update(item)
            union.update(item)
        guaranteed.update(intersection)
        possible.update(union)
        max_sum += max(map(len, candidate))
        min_single = max(min_single, min(map(len, candidate)))
    lower = max(1, len(guaranteed), min_single)
    upper = min(len(possible), max_sum)
    if lower > upper:
        raise AssertionError("inconsistent conservative bounds")
    return lower, upper, False, 0, "conservative"


def selftest():
    # Independently enumerate A and its visible-address subsequence on 6 lanes.
    # This oracle does not call possible_ranks or the primary enumerator.
    checks = 0
    for mask in range(1, 1 << 6):
        k = mask.bit_count()
        visible = [i for i in range(6) if mask & (1 << i)]
        for n in range(k, 7):
            for pattern in range(3):
                tokens = [
                    hex((0x1000 + 32 * i) if pattern == 0 else
                        (0x101f + 32 * i) if pattern == 1 else
                        (0x1000 + 4 * (i % 3)))
                    for i in range(n)
                ]
                actual = []
                for a in range(1 << 6):
                    if a & mask != mask or a.bit_count() != n:
                        continue
                    active = [i for i in range(6) if a & (1 << i)]
                    touched = set()
                    for lane in visible:
                        j = active.index(lane)
                        addr = int(tokens[j], 0)
                        touched.update(range(addr // 32, (addr + 3) // 32 + 1))
                    actual.append(len(touched))
                lo, hi, sharp, _, _ = format0_envelope(mask, 4, tokens, 999999, lanes=6)
                assert actual and lo <= min(actual) <= max(actual) <= hi
                assert sharp and (lo, hi) == (min(actual), max(actual))
                checks += 1
    # Adversarial hidden-lane ambiguity: visible lane 1 can read either token.
    lo, hi, sharp, _, _ = format0_envelope(0b10, 4, ["0x101f", "0x1040"], 0, lanes=3)
    assert (lo, hi, sharp) == (1, 2, True)
    # Force the conservative path and compare it against exhaustive oracle.
    fallback_checks = 0
    for mask in range(1, 1 << 6):
        k = mask.bit_count()
        if k < 2:
            continue
        for n in range(k + 1, 6):
            tokens = [hex(0x101f + 32 * i) for i in range(n)]
            lo, hi, sharp, _, method = format0_envelope(mask, 4, tokens, 0, lanes=6)
            assert not sharp and method == "conservative"
            actual = []
            visible = [i for i in range(6) if mask & (1 << i)]
            for a in range(1 << 6):
                if a & mask != mask or a.bit_count() != n:
                    continue
                active = [i for i in range(6) if a & (1 << i)]
                touched = set()
                for lane in visible:
                    j = active.index(lane)
                    addr = int(tokens[j], 0)
                    touched.update(range(addr // 32, (addr + 3) // 32 + 1))
                actual.append(len(touched))
            assert actual and lo <= min(actual) and hi >= max(actual)
            fallback_checks += 1
    for invalid in [(0b11, 4, ["0x1000"]), (0b1, 4, ["-1"])]:
        try:
            format0_envelope(*invalid, budget=0)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed source record accepted")
    assert format0_envelope(0b10, 4, ["0xffffffffffffffff", "0x1000"], 0, lanes=3)[4] == "overflow_unknown"
    assert format0_envelope(0b10, 4, ["0xffffffffffffffff", "0x1000", "0x1020"], 0, lanes=3)[4] == "unique_A"
    return {"selftest": "PASS", "independent_exhaustive_cases": checks,
            "forced_conservative_oracle_cases": fallback_checks,
            "adversarial_hidden_lane_counterexample": "PASS",
            "malformed_records_rejected": 2, "overflow_unknown_fixture": "PASS"}


def scan(path):
    with open(path, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive size or SHA-256 mismatch")
    apps = defaultdict(Counter)
    remaining = MAX_TOTAL_CHOICES
    files = 0
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
            files += 1
            acc = apps[parts[2]]
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError("unreadable trace member")
            for line_no, raw in enumerate(stream, 1):
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or not line[0].isdigit():
                    continue
                try:
                    row = address_tail(line)
                    if row is None:
                        continue
                    mask, op, width, fmt, data = row
                    acc["global_proxy"] += 1
                    if fmt == 0:
                        acc["format0_rows"] += 1
                        k = mask.bit_count()
                        n = len(data)
                        if n < k or n > 32:
                            raise ValueError("source-incompatible format0 row")
                        lo, hi, sharp, used, method = format0_envelope(mask, width, data, remaining)
                        remaining -= used
                        acc["format0_sector_lower32"] += lo
                        acc["format0_sector_upper32"] += hi
                        acc["format0_enumerated_masks"] += used
                        acc["format0_" + method] += 1
                        if n > k:
                            acc["format0_predicate_hidden"] += 1
                            acc["format0_hidden_exact_sector32" if lo == hi else
                                "format0_hidden_ambiguous_sector32"] += 1
                            if not sharp:
                                acc["format0_hidden_fallback"] += 1
                        else:
                            acc["format0_old_exact"] += 1
                    elif fmt == 1:
                        acc["format1_rows"] += 1
                        base, stride = (int(x, 0) for x in data)
                        lo, hi, _ = format1_sector_envelope(mask, width, base, stride)
                        acc["format1_sector_lower32"] += lo
                        acc["format1_sector_upper32"] += hi
                        acc["format1_ambiguous32" if lo != hi else "format1_exact32"] += 1
                    else:
                        raise ValueError("unexpected format2; no source-conditional decoder")
                    acc["sector_lower32"] += lo
                    acc["sector_upper32"] += hi
                except (ValueError, IndexError, AssertionError) as exc:
                    raise ValueError(f"{member.name}:{line_no}: {exc}") from exc
    g = Counter()
    for a in apps.values():
        g.update(a)
    if files != 210 or g["global_proxy"] != 240465:
        raise ValueError("frozen corpus conservation failed")
    if g["format0_rows"] != 106728 or g["format1_rows"] != 133737:
        raise ValueError("format-count conservation failed")
    if g["format0_predicate_hidden"] != 22504 or g["format1_ambiguous32"] != 371:
        raise ValueError("previous source-conditional audit mismatch")
    if g["format1_sector_lower32"] != 1194830 or g["format1_sector_upper32"] != 1195201:
        raise ValueError("previous format1 sector envelope mismatch")
    if g["format0_old_exact"] != 84224:
        raise ValueError("previous exact format0 count mismatch")
    return {
        "evidence_tier": "source_conditional_32B_sector_bounds_NOT_measured_transactions",
        "producer_hypothesis_commit": PRODUCER_COMMIT,
        "producer_identity_verified": False,
        "archive_sha256": EXPECTED_SHA,
        "trace_files": files,
        "global": dict(g),
        "applications": {k: dict(v) for k, v in sorted(apps.items())},
        "limits": [
            "All bounds are conditional on the 2020 tracer source model",
            "Some format0 intervals are conservative, not sharp",
            "Sector counts are not physical transactions, stalls or cycles",
            "Rodinia families were previously inspected; no prospective hardware holdout",
            "No hardware mechanism promoted; ideal fixed-address coalescer remains control",
            "No area/power/timing/RTX5090-equivalence result"
        ]
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), sort_keys=True))
    if args.archive:
        print(json.dumps(scan(args.archive), sort_keys=True, indent=2))
    elif not args.selftest:
        p.error("archive required")
