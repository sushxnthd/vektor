#!/usr/bin/env python3
"""V309: legal per-stream-order interleaving sensitivity, NOT GPU cache simulation.

All address identities are conditional on an unverified historical tracer source.
No schedule is asserted to be physically feasible on the V100.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict, defaultdict, deque
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import PurePosixPath
import random
import tarfile

from legacy_predicate_mask_provenance import address_tail
from trace_line_reuse import certified_addresses, instruction_lines
from v100_sass_profile import EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name
from cache_capacity_replay import summarize as previous_summarize

CAPACITIES = (4, 16, 64, 256)
SCHEDULES = ("recorded", "serial", "round_robin")
MODES = ("skip", "flush")
EXPECTED = (210, 240465, 197197, 190219, 530930, 159345)


def stream_key(line):
    t = line.split()
    if len(t) < 4:
        raise ValueError("short CTA/warp prefix")
    try:
        k = tuple(int(x) for x in t[:4])
    except ValueError as exc:
        raise ValueError("noninteger CTA/warp prefix") from exc
    if len(k) != 4 or any(x < 0 for x in k):
        raise ValueError("negative or invalid CTA/warp key")
    return k


def schedule_events(events, streams, schedule):
    if schedule == "recorded":
        return iter(events)
    if schedule == "serial":
        return itertools.chain.from_iterable(streams.values())
    if schedule == "round_robin":
        queue = deque(iter(seq) for seq in streams.values())
        def generate():
            while queue:
                it = queue.popleft()
                try:
                    event = next(it)
                except StopIteration:
                    continue
                yield event
                queue.append(it)
        return generate()
    raise ValueError("unknown schedule")


def replay(events, capacities=CAPACITIES):
    if not capacities or any(type(c) is not int or c <= 0 for c in capacities):
        raise ValueError("invalid capacity")
    if len(set(capacities)) != len(capacities):
        raise ValueError("duplicate capacity")
    caches = {(mode, c): OrderedDict() for mode in MODES for c in capacities}
    misses = Counter()
    count = refs = unknown = 0
    unique = set()
    last = {}
    for key, index, lines in events:
        if len(key) != 4 or any(type(v) is not int or v < 0 for v in key):
            raise ValueError("invalid stream")
        if type(index) is not int or index != last.get(key, -1) + 1:
            raise AssertionError("per-stream instruction order changed")
        last[key] = index
        count += 1
        if lines is None:
            unknown += 1
            for c in capacities:
                caches[("flush", c)].clear()
            continue
        if not isinstance(lines, tuple) or not lines or tuple(sorted(set(lines))) != lines:
            raise ValueError("invalid line bundle")
        if any(type(x) is not int or x < 0 for x in lines):
            raise ValueError("invalid line identity")
        refs += len(lines)
        unique.update(lines)
        for line in lines:
            for (mode, capacity), cache in caches.items():
                if line in cache:
                    cache.move_to_end(line)
                else:
                    misses[(mode, capacity)] += 1
                    cache[line] = None
                    if len(cache) > capacity:
                        cache.popitem(last=False)
    return {
        "events": count, "unknown": unknown, "references": refs,
        "unique": len(unique), "streams": len(last),
        "misses": {mode: {str(c): misses[(mode, c)] for c in capacities} for mode in MODES}
    }


def independent_lru(lines, capacity, flush):
    # Intentionally different list-based implementation.
    recent = []
    misses = 0
    for bundle in lines:
        if bundle is None:
            if flush:
                recent.clear()
            continue
        for line in bundle:
            if line in recent:
                recent.remove(line)
            else:
                misses += 1
            recent.append(line)
            if len(recent) > capacity:
                del recent[0]
    return misses


def make_streams(*sequences):
    streams = OrderedDict()
    events = []
    for k, seq in enumerate(sequences):
        key = (k, 0, 0, 0)
        streams[key] = [(key, j, None if x is None else (x,))
                        for j, x in enumerate(seq)]
    for j in range(max(map(len, sequences), default=0)):
        for seq in streams.values():
            if j < len(seq):
                events.append(seq[j])
    return events, streams


def selftest():
    a, streams = make_streams((0, 1) * 3, (2, 3) * 3)
    serial = replay(schedule_events(a, streams, "serial"), (2, 4))
    rr = replay(schedule_events(a, streams, "round_robin"), (2, 4))
    assert serial["misses"]["skip"]["2"] == 4
    assert rr["misses"]["skip"]["2"] == 12
    assert serial["misses"]["skip"]["4"] == rr["misses"]["skip"]["4"] == 4

    # Countercontrol: sharing addresses reverses the direction.
    a, streams = make_streams((0, 1), (0, 1))
    assert replay(schedule_events(a, streams, "serial"), (1,))["misses"]["skip"]["1"] == 4
    assert replay(schedule_events(a, streams, "round_robin"), (1,))["misses"]["skip"]["1"] == 2

    rng = random.Random(309110)
    checked = 0
    for _ in range(512):
        w = rng.randrange(1, 5)
        sequences = [tuple(rng.choice((None, 0, 1, 2, 3, 4))
                           for _ in range(rng.randrange(1, 8))) for _ in range(w)]
        a, streams = make_streams(*sequences)
        for schedule in SCHEDULES:
            ordered = list(schedule_events(a, streams, schedule))
            for cap in (1, 2, 4):
                for mode in MODES:
                    got = replay(ordered, (cap,))["misses"][mode][str(cap)]
                    want = independent_lru(
                        [event[2] for event in ordered], cap, mode == "flush")
                    assert got == want, (schedule, cap, mode, got, want)
                    checked += 1
    # Exhaust all order-preserving interleavings of two streams (2 events each).
    for xs in itertools.product((0, 1), repeat=4):
        left, right = xs[:2], xs[2:]
        for slots in itertools.combinations(range(4), 2):
            merged = []
            li = ri = 0
            for i in range(4):
                if i in slots:
                    merged.append(left[li]); li += 1
                else:
                    merged.append(right[ri]); ri += 1
            for c in (1, 2):
                assert independent_lru([(x,) for x in merged], c, False) >= len(set(merged))
                checked += 1
    for bad in ((0,), (-1,), (True,), (2, 2)):
        try:
            replay([], bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid capacity accepted")
    for bad in ("-1 0 0 0", "a 0 0 0", "0 0 0"):
        try:
            stream_key(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid stream key accepted")
    return {"status": "PASS", "independent_lru_oracle_checks": checked,
            "frozen_high_regime": {"serial_C2": 4, "round_robin_C2": 12},
            "frozen_no_win_regime": {"serial_C4": 4, "round_robin_C4": 4},
            "shared_line_direction_reversal": True}


def parse_file(fp, filename):
    events = []
    streams = OrderedDict()
    records = []
    for lineno, raw in enumerate(fp, 1):
        line = raw.decode("utf-8", errors="replace").strip()
        if not line or not line[0].isdigit():
            continue
        try:
            rec = address_tail(line)
            if rec is None:
                continue
            records.append(rec)
            if rec[1].split(".", 1)[0] != "LDG":
                continue
            key = stream_key(line)
            addresses, _ = certified_addresses(rec)
            lines = None if addresses is None else tuple(sorted(
                instruction_lines(addresses, rec[2])))
            if key not in streams:
                streams[key] = []
            event = (key, len(streams[key]), lines)
            streams[key].append(event)
            events.append(event)
        except (ValueError, IndexError, AssertionError) as exc:
            raise ValueError(f"{filename}:{lineno}: {exc}") from exc
    return events, streams, records


def fraction(n, d):
    return str(Fraction(n, d)) if d else None


def scan(archive):
    with open(archive, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive size/digest mismatch")
    files = []
    totals = Counter()
    app_totals = defaultdict(Counter)
    app_misses = defaultdict(Counter)
    global_misses = Counter()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for member in tar:
            validate_name(member.name)
            if member.isdev():
                raise ValueError("unsafe archive member")
            if not member.isfile() or not member.name.endswith(".traceg"):
                continue
            if member.size < 0 or member.size > 2 * 1024**3:
                raise ValueError("oversized trace member")
            parts = PurePosixPath(member.name).parts
            if len(parts) < 5:
                raise ValueError("unexpected trace path")
            fp = tar.extractfile(member)
            if fp is None:
                raise ValueError("unreadable trace member")
            events, streams, records = parse_file(fp, member.name)
            old_counts, old_misses = previous_summarize(records)
            results = {schedule: replay(schedule_events(events, streams, schedule))
                       for schedule in SCHEDULES}
            base = results["recorded"]
            for schedule, res in results.items():
                if tuple(res[k] for k in ("events", "unknown", "references", "unique", "streams")) != tuple(
                    base[k] for k in ("events", "unknown", "references", "unique", "streams")):
                    raise AssertionError(f"{member.name}: event conservation failed for {schedule}")
            if (base["events"], base["unknown"], base["references"], base["unique"]) != (
                old_counts["ldg_rows"], old_counts["ldg_rows"] - old_counts["certified_rows"],
                old_counts["line_references"], old_counts["unique_lines"]):
                raise AssertionError(f"{member.name}: old/new parser mismatch")
            for mode in MODES:
                for c in CAPACITIES:
                    if base["misses"][mode][str(c)] != old_misses[mode][str(c)]:
                        raise AssertionError(f"{member.name}: recorded-order old/new mismatch {mode} C={c}")
            app = parts[2]
            app_totals[app].update(old_counts)
            totals.update(old_counts)
            for schedule, res in results.items():
                for mode in MODES:
                    for c in CAPACITIES:
                        key = (schedule, mode, c)
                        app_misses[app][key] += res["misses"][mode][str(c)]
                        global_misses[key] += res["misses"][mode][str(c)]
            files.append({"trace": member.name, "application": app,
                          "streams": base["streams"], "ldg_rows": base["events"],
                          "unknown": base["unknown"], "line_references": base["references"],
                          "unique_lines": base["unique"],
                          "misses": {s: results[s]["misses"] for s in SCHEDULES}})
    actual = (len(files), *(totals[k] for k in
              ("global_proxy", "ldg_rows", "certified_rows", "line_references", "unique_lines")))
    if actual != EXPECTED:
        raise AssertionError(f"authenticated corpus conservation failed: {actual}")
    if totals["ldg_rows"] - totals["certified_rows"] != 6978:
        raise AssertionError("unexpected unknown-row count")
    if global_misses[("recorded", "skip", 64)] != 175042 or global_misses[("recorded", "flush", 64)] != 202939:
        raise AssertionError("previous hosted 64-line replay not reproduced")
    def output_misses(c):
        return {s: {m: {str(k): c[(s, m, k)] for k in CAPACITIES}
                    for m in MODES} for s in SCHEDULES}
    def sensitivity(c):
        out = {}
        for mode in MODES:
            for cap in CAPACITIES:
                vals = [c[(s, mode, cap)] for s in SCHEDULES]
                out[f"{mode}_C{cap}"] = {"min": min(vals), "max": max(vals),
                    "max_over_min": fraction(max(vals), min(vals))}
        return out
    return {"status": "PASS", "archive_sha256": EXPECTED_SHA,
        "evidence_tier": "historical_source_conditional_order_preserving_interleaving_sensitivity_NOT_GPU_misses",
        "producer_identity_verified": False, "physical_schedule_validated": False,
        "hypothetical_line_bytes": 128, "capacities": list(CAPACITIES),
        "global": {**dict(totals), "misses": output_misses(global_misses),
                   "sensitivity": sensitivity(global_misses)},
        "applications": {a: {**dict(app_totals[a]), "misses": output_misses(app_misses[a]),
                            "sensitivity": sensitivity(app_misses[a])} for a in sorted(app_totals)},
        "files": sorted(files, key=lambda x: x["trace"]),
        "selftest": selftest(),
        "limitations": [
            "three orderings preserve within-stream LDG order but are not authenticated GPU schedules",
            "producer source identity is unverified",
            "omitted LDG and non-LDG operations prevent physical cache traffic inference",
            "SKIP/FLUSH are not physical upper/lower bounds",
            "hypothetical fully associative LRU is not a calibrated V100 cache hierarchy",
            "no RTL, measured GPU cycles, bandwidth, area, power, speedup or RTX 5090 equivalence"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--output", default="-")
    args = p.parse_args()
    if not args.archive and not args.selftest:
        p.error("archive or --selftest required")
    result = scan(args.archive) if args.archive else selftest()
    data = json.dumps(result, sort_keys=True, indent=2)
    if args.output == "-":
        print(data)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data + "\n")
