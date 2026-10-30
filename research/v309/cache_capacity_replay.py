#!/usr/bin/env python3
"""V309 finite-cache LRU replay of *certified-only* LDG line IDs.

NOT GPU cache misses/DRAM transactions: historical tracer producer, memory
scheduling, cache mapping and all omitted memory operations are unverified.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict, defaultdict
import hashlib
import io
import json
import random
import tarfile
from pathlib import PurePosixPath

from legacy_predicate_mask_provenance import address_tail
from trace_line_reuse import certified_addresses, instruction_lines
from v100_sass_profile import EXPECTED_SHA
from v100_trace_inventory import MAX_ARCHIVE, validate_name

CAPACITIES = (1, 4, 16, 64, 256, 1024)
EXPECTED = (210, 240465, 197197, 190219, 530930, 159345)


class Replay:
    def __init__(self, capacities=CAPACITIES):
        if not capacities or len(set(capacities)) != len(capacities) or any(
            not isinstance(c, int) or isinstance(c, bool) or c <= 0 for c in capacities
        ):
            raise ValueError("capacities must be distinct positive integers")
        self.capacities = tuple(capacities)
        self.caches = {(mode, c): OrderedDict()
                       for mode in ("skip", "flush") for c in self.capacities}
        self.misses = Counter()

    def unknown(self):
        for c in self.capacities:
            self.caches[("flush", c)].clear()

    def access(self, line):
        if not isinstance(line, int) or line < 0:
            raise ValueError("line identity must be nonnegative integer")
        for key, cache in self.caches.items():
            if line in cache:
                cache.move_to_end(line)
            else:
                self.misses[key] += 1
                cache[line] = None
                if len(cache) > key[1]:
                    cache.popitem(last=False)

    def snapshot(self):
        return {mode: {str(c): self.misses[(mode, c)] for c in self.capacities}
                for mode in ("skip", "flush")}


def summarize(records):
    r = Replay()
    counts = Counter()
    unique = set()
    for rec in records:
        counts["global_proxy"] += 1
        mask, op, width, fmt, data = rec
        if op.split(".", 1)[0] != "LDG":
            continue
        counts["ldg_rows"] += 1
        addresses, status = certified_addresses(rec)
        counts[status] += 1
        if addresses is None:
            r.unknown()
            continue
        counts["certified_rows"] += 1
        lines = sorted(instruction_lines(addresses, width))
        counts["line_references"] += len(lines)
        unique.update(lines)
        for line in lines:
            r.access(line)
    counts["unique_lines"] = len(unique)
    if counts["ldg_rows"] != (counts["certified_rows"] +
                             counts["excluded_format0_hidden_lanes"] +
                             counts["excluded_format1_shifted_start"]):
        raise AssertionError("LDG classification not conserved")
    if any(not counts["unique_lines"] <= r.misses[("skip", c)] <=
           r.misses[("flush", c)] <= counts["line_references"]
           for c in CAPACITIES):
        raise AssertionError("misses outside subset replay bounds")
    for mode in ("skip", "flush"):
        misses = [r.misses[(mode, c)] for c in CAPACITIES]
        if misses != sorted(misses, reverse=True):
            raise AssertionError("LRU stack monotonicity failed")
    return counts, r.snapshot()


def scan(path):
    with open(path, "rb") as f:
        blob = f.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA:
        raise ValueError("archive digest or size mismatch")
    apps = defaultdict(Counter)
    app_misses = defaultdict(Counter)
    files = []
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
                raise ValueError("unexpected trace path")
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
                counts, misses = summarize(records())
            except (ValueError, AssertionError, IndexError) as exc:
                raise ValueError(f"{member.name}: {exc}") from exc
            app = parts[2]
            apps[app].update(counts)
            for mode, cm in misses.items():
                for capacity, value in cm.items():
                    app_misses[app][(mode, capacity)] += value
            files.append({"trace": member.name, "application": app,
                          **dict(counts), "misses": misses})

    global_counts = Counter()
    global_misses = Counter()
    for app in apps:
        global_counts.update(apps[app])
        global_misses.update(app_misses[app])
    actual = (len(files), *(global_counts[k] for k in
              ("global_proxy", "ldg_rows", "certified_rows",
               "line_references", "unique_lines")))
    if actual != EXPECTED:
        raise AssertionError(f"authenticated corpus conservation failed: {actual}")
    for mode in ("skip", "flush"):
        for capacity in CAPACITIES:
            k = (mode, str(capacity))
            if sum(f["misses"][mode][str(capacity)] for f in files) != global_misses[k]:
                raise AssertionError("per-file cache-miss conservation failed")

    def nested_misses(counter):
        return {mode: {str(c): counter[(mode, str(c))] for c in CAPACITIES}
                for mode in ("skip", "flush")}

    return {
        "status": "PASS",
        "evidence_tier": "historical_source_conditional_ordered_LDG_subset_LRU_replay_NOT_GPU_cache_misses",
        "archive_sha256": EXPECTED_SHA, "producer_identity_verified": False,
        "line_bytes_assumed": 128, "capacities_in_lines": list(CAPACITIES),
        "global": {**dict(global_counts), "misses": nested_misses(global_misses)},
        "applications": {
            app: {**dict(apps[app]), "misses": nested_misses(app_misses[app])}
            for app in sorted(apps)
        },
        "files": sorted(files, key=lambda f: f["trace"]),
        "selftest": selftest(),
        "limitations": [
            "trace order is not authenticated GPU memory scheduling",
            "line ordering within an instruction is an arbitrary sorted tie-breaker",
            "source producer hypothesis is unverified",
            "excluded LDG rows and non-LDG memory operations can change actual cache behavior",
            "SKIP and FLUSH do not bracket physical GPU misses",
            "capacity is fully associative LRU lines, not a calibrated V100 cache model",
            "Rodinia workloads are retrospective, not unseen",
            "no GPU cycles, DRAM transactions, bandwidth, power or hardware mechanism validated",
        ],
    }


def oracle(seq, capacity, mode):
    """Independent list-based reference; None is an ambiguous instruction."""
    recent = []
    misses = 0
    for line in seq:
        if line is None:
            if mode == "flush":
                recent = []
            continue
        if line in recent:
            recent.remove(line)
        else:
            misses += 1
        recent.append(line)
        if len(recent) > capacity:
            recent.pop(0)
    return misses


def selftest():
    for invalid in ((), (0,), (-1,), (1, 1), (True,), (1, 1.5)):
        try:
            Replay(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid capacity accepted")
    hot = [0] * 64
    cold = list(range(64))
    thrash = list(range(8)) * 8
    order_a = [0, 1, 0, 1]
    order_b = [0, 0, 1, 1]
    assert [oracle(hot, c, "skip") for c in CAPACITIES] == [1] * len(CAPACITIES)
    assert [oracle(cold, c, "skip") for c in CAPACITIES] == [64] * len(CAPACITIES)
    assert oracle(thrash, 4, "skip") == 64
    assert oracle(thrash, 16, "skip") == 8
    assert oracle(order_a, 1, "skip") == 4 and oracle(order_b, 1, "skip") == 2
    rng = random.Random(3091030)
    checked = 0
    for _ in range(512):
        seq = [None if rng.randrange(9) == 0 else rng.randrange(12)
               for _ in range(rng.randrange(1, 50))]
        capacities = tuple(range(1, 9))
        r = Replay(capacities)
        for line in seq:
            r.unknown() if line is None else r.access(line)
        for mode in ("skip", "flush"):
            for c in capacities:
                if r.misses[(mode, c)] != oracle(seq, c, mode):
                    raise AssertionError("independent LRU oracle mismatch")
                checked += 1
    for bad in (-1, "0", None):
        try:
            Replay((1,)).access(bad)
        except ValueError:
            continue
        raise AssertionError("invalid line accepted")
    return {"status": "PASS", "independent_oracle_comparisons": checked,
            "synthetic_regimes": 4, "invalid_capacity_refusals": 6,
            "invalid_line_refusals": 3}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", nargs="?")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), sort_keys=True, indent=2))
    if args.archive:
        print(json.dumps(scan(args.archive), sort_keys=True, indent=2))
    elif not args.selftest:
        p.error("archive required")
