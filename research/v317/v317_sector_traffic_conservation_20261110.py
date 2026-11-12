#!/usr/bin/env python3
"""V317 traffic-conservation falsification, with reproducible synthetic controls.

An issue scheduler does not reduce DRAM traffic merely by pairing warp grants.
A traffic claim needs a changed cache/coalescer/memory transaction trace.
Input JSON: {"baseline":[{"op":"load","addresses":[0,4], "bytes":4},...],
             "candidate":[...]}.
Each event is one coalescer issue. Addresses are byte addresses for active lanes;
"bytes" is bytes per lane. Events with op="compute" contribute no traffic.
Model: distinct aligned sectors touched per event, summed over events; NO cache.
This is a deliberately pessimistic per-issue L1-sector proxy, not DRAM bytes.
"""
import argparse
import json
from collections import Counter

def sectors(events, sector_bytes=32):
    if sector_bytes <= 0 or sector_bytes & (sector_bytes - 1):
        raise ValueError("sector_bytes must be positive power of two")
    total = 0
    histogram = Counter()
    for event in events:
        op = event["op"]
        if op == "compute":
            continue
        if op not in ("load", "store"):
            raise ValueError("unknown op")
        width = event["bytes"]
        if not isinstance(width, int) or width <= 0:
            raise ValueError("invalid lane width")
        touched = set()
        for addr in event["addresses"]:
            if not isinstance(addr, int) or addr < 0:
                raise ValueError("invalid address")
            touched.update(range(addr // sector_bytes,
                                 (addr + width - 1) // sector_bytes + 1))
        histogram[op] += len(touched)
        total += len(touched)
    return total * sector_bytes, dict(histogram)

def audit(data, sector_bytes=32):
    baseline, candidate = data["baseline"], data["candidate"]
    b, bh = sectors(baseline, sector_bytes)
    c, ch = sectors(candidate, sector_bytes)
    # This tool cannot prove equivalence of useful operations or cache behavior.
    return {"baseline_sector_bytes": b, "candidate_sector_bytes": c,
            "ratio": c / b if b else None,
            "baseline_sectors_by_op": bh, "candidate_sectors_by_op": ch,
            "evidence_tier": "sector-proxy-only; not DRAM traffic or equivalence"}

def tests():
    a = {"op": "load", "addresses": [0, 4, 8, 12], "bytes": 4}
    b = {"op": "load", "addresses": [16, 20, 24, 28], "bytes": 4}
    # Pairing without coalescer modification: identical per-issue sectors.
    same = audit({"baseline": [a, b], "candidate": [b, a]})
    assert same["ratio"] == 1
    # An explicitly different transaction grouping can reduce sectors, but
    # ONLY if the hardware really supports cross-warp coalescing.
    split = {"op": "load", "addresses": [0, 4], "bytes": 4}
    split2 = {"op": "load", "addresses": [8, 12], "bytes": 4}
    merged = {"op": "load", "addresses": [0, 4, 8, 12], "bytes": 4}
    hypothetical = audit({"baseline": [split, split2], "candidate": [merged]})
    assert hypothetical["ratio"] == 0.5
    # Lane duplication in a single issue is counted once per sector.
    assert sectors([{"op":"store","addresses":[0,0],"bytes":4}])[0] == 32
    assert sectors([{"op":"compute"}])[0] == 0
    try:
        sectors([{"op":"load","addresses":[-1],"bytes":4}])
        raise AssertionError("negative address accepted")
    except ValueError:
        pass
    print("PASS: conservation, hypothetical regrouping, sectors, invalid input")
    print(json.dumps({"unchanged_grants": same,
                      "cross_warp_coalescer_hypothesis": hypothetical}, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", help="JSON trace containing baseline/candidate")
    parser.add_argument("--sector-bytes", type=int, default=32)
    args = parser.parse_args()
    if args.trace:
        with open(args.trace, encoding="utf-8") as f:
            print(json.dumps(audit(json.load(f), args.sector_bytes), indent=2))
    else:
        tests()
