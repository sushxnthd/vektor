#!/usr/bin/env python3
"""V309 read-counter collision certificate: retrospective published sample only."""
from __future__ import annotations
import argparse
from collections import defaultdict
from decimal import Decimal, getcontext
import json
from external_profiler_counter_audit import COLUMNS, URL, parse

getcontext().prec = 50
FEATURE_SETS = {
    "read_misses": ("L1_RM", "L2_RM"),
    "all_read_counters": ("L1_RH", "L1_RM", "L2_RH", "L2_RM"),
}

def analyze(rows: list[dict], features: tuple[str, ...]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[col] for col in features)].append(row)
    collisions = []
    for key, members in groups.items():
        positive = [r for r in members if r["DRAM_Rd"] > 0]
        if len(positive) < 2:
            continue
        ys = [r["DRAM_Rd"] for r in positive]
        low, high = min(ys), max(ys)
        if low == high:
            continue
        ratio = high / low
        collisions.append({
            "features": [str(v) for v in key],
            "members": sorted(r["Benchmark"] + " :: " + r["Kernel"] for r in positive),
            "rows": len(positive),
            "minimum_dram_read": str(low),
            "maximum_dram_read": str(high),
            "ratio_exact": str(ratio),
            "minimax_multiplicative_factor": format(ratio.sqrt(), ".12g"),
            "minimax_additive_error": str((high - low) / 2),
            "best_groupwise_constant": format((low * high).sqrt(), ".12g"),
        })
    collisions.sort(key=lambda x: Decimal(x["ratio_exact"]), reverse=True)
    return {
        "features": list(features),
        "rows": len(rows),
        "distinct_feature_vectors": len(groups),
        "ambiguous_feature_vectors": len(collisions),
        "impossible_exact_deterministic_reconstruction": bool(collisions),
        "strongest_collision": collisions[0] if collisions else None,
        "all_collisions": collisions,
    }

def independent_pairwise_oracle(rows: list[dict], features: tuple[str, ...]) -> Decimal:
    # Independent O(n^2) checker; does not use grouped calculation.
    best = Decimal(1)
    for i, a in enumerate(rows):
        if a["DRAM_Rd"] <= 0:
            continue
        for b in rows[i + 1:]:
            if b["DRAM_Rd"] <= 0 or not all(a[f] == b[f] for f in features):
                continue
            ratio = max(a["DRAM_Rd"], b["DRAM_Rd"]) / min(a["DRAM_Rd"], b["DRAM_Rd"])
            best = max(best, ratio)
    return best

def validate(rows: list[dict]) -> dict:
    result = {}
    for name, features in FEATURE_SETS.items():
        audit = analyze(rows, features)
        best = Decimal(audit["strongest_collision"]["ratio_exact"]) if audit["strongest_collision"] else Decimal(1)
        assert best == independent_pairwise_oracle(rows, features), name
        result[name] = audit
    return {
        "status": "PASS",
        "tier": "RETROSPECTIVE_PUBLISHED_UNMATCHED_COUNTER_IDENTIFIABILITY",
        "source": URL,
        "matched_to_v309_traces": False,
        "hardware_mechanism_promoted": False,
        "analyses": result,
    }

def selftest() -> dict:
    header = ",".join(COLUMNS)
    def fixture(name: str, y: str, l1rh="0", l1rm="0", l2rh="0", l2rm="0") -> bytes:
        values = ["0"] * (len(COLUMNS) - 2)
        for col, value in [("DRAM_Rd", y), ("L1_RH", l1rh), ("L1_RM", l1rm),
                           ("L2_RH", l2rh), ("L2_RM", l2rm)]:
            values[COLUMNS.index(col) - 2] = value
        return (name + ",k," + ",".join(values) + "\n").encode()
    def pack(*records):
        return (header + "\n").encode() + b"".join(records)
    rows = parse(pack(fixture("a", "2"), fixture("b", "18")), verify_blob=False)
    a = validate(rows)["analyses"]["all_read_counters"]
    assert a["ambiguous_feature_vectors"] == 1
    assert Decimal(a["strongest_collision"]["ratio_exact"]) == 9
    assert Decimal(a["strongest_collision"]["minimax_additive_error"]) == 8
    assert Decimal(a["strongest_collision"]["best_groupwise_constant"]) == 6
    assert not analyze(parse(pack(fixture("a", "2"), fixture("b", "2")), verify_blob=False),
                       FEATURE_SETS["all_read_counters"])["impossible_exact_deterministic_reconstruction"]
    assert not analyze(parse(pack(fixture("a", "2"), fixture("b", "18", l2rh="1")), verify_blob=False),
                       FEATURE_SETS["all_read_counters"])["impossible_exact_deterministic_reconstruction"]
    assert analyze(parse(pack(fixture("a", "2"), fixture("b", "18", l2rh="1")), verify_blob=False),
                   FEATURE_SETS["read_misses"])["impossible_exact_deterministic_reconstruction"]
    assert analyze(parse(pack(fixture("a", "0.2"), fixture("b", "0.20")), verify_blob=False),
                   FEATURE_SETS["all_read_counters"])["ambiguous_feature_vectors"] == 0
    invalids = ["NaN", "Infinity", "-1", "oops"]
    for value in invalids:
        try:
            parse(pack(fixture("a", value)), verify_blob=False)
        except ValueError:
            pass
        else:
            raise AssertionError("bad target accepted: " + value)
    assert not analyze(parse(pack(fixture("a", "0"), fixture("b", "2")), verify_blob=False),
                       FEATURE_SETS["all_read_counters"])["impossible_exact_deterministic_reconstruction"]
    return {"status": "PASS", "synthetic_cases": 7, "malformed_refusals": len(invalids),
            "independent_oracle": "pairwise O(n^2) exact Decimal ratio"}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--input", help="optional local pinned upstream CSV")
    args = parser.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), indent=2, sort_keys=True))
        return
    if args.input:
        with open(args.input, "rb") as f:
            data = f.read(100_001)
    else:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read(100_001)
    rows = parse(data)
    assert len(rows) == 25
    print(json.dumps(validate(rows), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
