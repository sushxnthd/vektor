#!/usr/bin/env python3
"""Independent semantic-conservation prerequisite for V317 sector-traffic claims.

Compares byte-level load/store lane operations before accepting a sector proxy
difference. This is necessary, not sufficient, for program equivalence:
address order, memory values, atomicity, races, cache state and dependencies
remain unverified. Store ordering is conservatively preserved at issue level.
"""
import argparse
import json
from collections import Counter

def lane_signature(events):
    loads = Counter()
    stores = []
    for event in events:
        op = event.get("op")
        if op == "compute":
            continue
        if op not in ("load", "store"):
            raise ValueError("unknown memory operation")
        width = event.get("bytes")
        if type(width) is not int or width <= 0:
            raise ValueError("invalid width")
        lanes = event.get("addresses")
        if not isinstance(lanes, list):
            raise ValueError("missing addresses")
        keys = []
        for address in lanes:
            if type(address) is not int or address < 0:
                raise ValueError("invalid address")
            if address + width > (1 << 64):
                raise ValueError("address overflow")
            keys.append((address, width))
        if op == "load":
            loads.update(keys)
        else:
            # Preserve store issue boundaries and lane order; do not infer
            # that two overlapping writes can be freely reordered/merged.
            stores.append(tuple(keys))
    return loads, tuple(stores)

def audit(trace):
    baseline = lane_signature(trace["baseline"])
    candidate = lane_signature(trace["candidate"])
    return {
        "load_lane_multiset_equal": baseline[0] == candidate[0],
        "store_issue_sequence_equal": baseline[1] == candidate[1],
        "necessary_conservation_pass": baseline == candidate,
        "evidence_tier": "necessary trace-conservation only; not RTL equivalence or DRAM traffic",
    }

def tests():
    a = {"op": "load", "addresses": [0, 4], "bytes": 4}
    b = {"op": "load", "addresses": [8, 12], "bytes": 4}
    merged = {"op": "load", "addresses": [0, 4, 8, 12], "bytes": 4}
    assert audit({"baseline": [a, b], "candidate": [merged]})["necessary_conservation_pass"]
    assert not audit({"baseline": [a, b], "candidate": [a]})["necessary_conservation_pass"]
    assert not audit({"baseline": [a], "candidate": [a, a]})["necessary_conservation_pass"]
    s1 = {"op": "store", "addresses": [0], "bytes": 4}
    s2 = {"op": "store", "addresses": [4], "bytes": 4}
    assert not audit({"baseline": [s1, s2], "candidate": [s2, s1]})["necessary_conservation_pass"]
    for bad in (True, -1, 1 << 64):
        try:
            lane_signature([{"op": "load", "addresses": [bad], "bytes": 4}])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid address accepted")
    print("PASS: necessary lane conservation and conservative store ordering")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace")
    args = parser.parse_args()
    if args.trace:
        with open(args.trace, encoding="utf-8") as f:
            print(json.dumps(audit(json.load(f)), indent=2))
    else:
        tests()
