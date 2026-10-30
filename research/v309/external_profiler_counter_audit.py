#!/usr/bin/env python3
"""V309 external profiler-counter audit. Exploratory evidence, NOT matched traces.

Fetches a single immutable Accel-Sim sample GV100 profiler CSV. No GPU speedup
or byte-traffic inference is made. Python standard library only.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, InvalidOperation, getcontext
import hashlib
import io
import json
import urllib.request

getcontext().prec = 50
UPSTREAM_COMMIT = "7ba54ded60c4ba0083410c37d22d719166acd6dc"
UPSTREAM_BLOB = "aa88bb2566ff3b3e012442cd20bc753127732cac"
UPSTREAM_PATH = "util/accelwattch/accelwattch_hw_profiler/hw_perf.csv"
URL = ("https://raw.githubusercontent.com/accel-sim/accel-sim-framework/"
       + UPSTREAM_COMMIT + "/" + UPSTREAM_PATH)
COLUMNS = ("Benchmark", "Kernel", "L1_RH", "L1_RM", "L1_WH", "L1_WM",
           "CC_ACC", "SHRD_ACC", "DRAM_Rd", "DRAM_Wr", "L2_RH", "L2_RM",
           "L2_WH", "L2_WM", "NOC", "Pipeline_Duty", "Num_Idle_SMs",
           "Elapsed_Cycles", "Chip Voltage")
ZERO = Decimal(0)
ONE = Decimal(1)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()


def parse(data: bytes, *, verify_blob: bool = True) -> list[dict]:
    if not data or len(data) > 100_000:
        raise ValueError("empty or oversized CSV")
    if verify_blob and blob_sha(data) != UPSTREAM_BLOB:
        raise ValueError("upstream Git blob mismatch; refusing unpinned counters")
    try:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8", errors="strict")))
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError("unexpected counter columns")
        rows = []
        keys = set()
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("malformed CSV row")
            key = (row["Benchmark"], row["Kernel"])
            if not all(key) or key in keys:
                raise ValueError("empty or duplicate benchmark/kernel")
            keys.add(key)
            record = {"Benchmark": key[0], "Kernel": key[1]}
            for col in COLUMNS[2:]:
                try:
                    v = Decimal(row[col])
                except InvalidOperation as exc:
                    raise ValueError("nonnumeric counter") from exc
                if not v.is_finite() or v < ZERO:
                    raise ValueError("nonfinite or negative counter")
                record[col] = v
            rows.append(record)
        if not rows:
            raise ValueError("no counter rows")
        return rows
    except UnicodeError as exc:
        raise ValueError("non-UTF8 CSV") from exc


def calculate(rows: list[dict]) -> dict:
    zero_l1 = [r for r in rows if r["L1_RM"] == ZERO and r["DRAM_Rd"] > ZERO]
    zero_l2 = [r for r in rows if r["L2_RM"] == ZERO and r["DRAM_Rd"] > ZERO]
    positive = [r for r in rows if r["L1_RM"] > ZERO and r["DRAM_Rd"] > ZERO]
    if not positive:
        raise ValueError("no positive denominator observations")
    ranked = sorted(positive, key=lambda r: r["DRAM_Rd"] / r["L1_RM"])
    lo, hi = ranked[0], ranked[-1]
    ratio_lo = lo["DRAM_Rd"] / lo["L1_RM"]
    ratio_hi = hi["DRAM_Rd"] / hi["L1_RM"]
    large_l2_mismatch = [
        r for r in rows if r["DRAM_Rd"] > ZERO and
        abs(r["DRAM_Rd"] - r["L2_RM"]) / r["DRAM_Rd"] > Decimal("0.01")
    ]
    def ident(r: dict) -> str:
        return r["Benchmark"] + " :: " + r["Kernel"]
    def dec(v: Decimal) -> str:
        return format(v, ".10g")
    return {
        "status": "PASS",
        "evidence_tier": "PUBLISHED_SAMPLE_PROFILER_COUNTERS_NOT_MATCHED_V309_TRACES",
        "upstream_repository": "accel-sim/accel-sim-framework",
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_blob": UPSTREAM_BLOB,
        "rows": len(rows),
        "benchmark_families": len({r["Benchmark"] for r in rows}),
        "positive_dram_with_zero_l1_read_misses": len(zero_l1),
        "positive_dram_with_zero_l2_read_misses": len(zero_l2),
        "zero_l1_counterexamples": [ident(r) for r in zero_l1],
        "zero_l2_counterexamples": [ident(r) for r in zero_l2],
        "positive_l1_and_dram_rows": len(positive),
        "dram_read_over_l1_read_miss_ratio_min": dec(ratio_lo),
        "dram_read_over_l1_read_miss_ratio_max": dec(ratio_hi),
        "ratio_spread_factor": dec(ratio_hi / ratio_lo),
        "min_ratio_kernel": ident(lo),
        "max_ratio_kernel": ident(hi),
        "l2_vs_dram_read_relative_difference_above_1pct_rows": len(large_l2_mismatch),
        "universal_zero_intercept_l1_proxy_falsified": bool(zero_l1),
        "universal_zero_intercept_l2_proxy_falsified": bool(zero_l2),
        "matched_to_v309_rodinia_2_0_ft_traces": False,
        "no_hardware_mechanism_promoted": True,
        "limitations": [
            "sample GV100 profiler counters; hardware provenance and units not independently verified",
            "the upstream CSV is not a per-kernel match to the V309 Rodinia 2.0-ft SASS archive",
            "ratios compare distinct counter domains; not cache hit rates or bytes",
            "no matched counters, physical RTL, measured throughput or unseen holdout",
        ],
    }


def independent_oracle(rows: list[dict], report: dict) -> None:
    # Independent arithmetic and count loops; does not reuse calculate's subsets.
    n_l1 = n_l2 = n_l2diff = 0
    mn = mx = None
    for row in rows:
        d = row["DRAM_Rd"]
        a = row["L1_RM"]
        b = row["L2_RM"]
        if d > 0 and a == 0:
            n_l1 += 1
        if d > 0 and b == 0:
            n_l2 += 1
        if d > 0 and 100 * abs(d - b) > d:
            n_l2diff += 1
        if d > 0 and a > 0:
            val = d / a
            mn = val if mn is None else min(mn, val)
            mx = val if mx is None else max(mx, val)
    assert report["positive_dram_with_zero_l1_read_misses"] == n_l1
    assert report["positive_dram_with_zero_l2_read_misses"] == n_l2
    assert report["l2_vs_dram_read_relative_difference_above_1pct_rows"] == n_l2diff
    assert report["dram_read_over_l1_read_miss_ratio_min"] == format(mn, ".10g")
    assert report["dram_read_over_l1_read_miss_ratio_max"] == format(mx, ".10g")


def selftest() -> dict:
    header = ",".join(COLUMNS)
    def fixture(x: str, y: str, a: str, b: str, c: str) -> bytes:
        nums = ["0"] * (len(COLUMNS) - 2)
        nums[COLUMNS.index("L1_RM") - 2] = a
        nums[COLUMNS.index("L2_RM") - 2] = b
        nums[COLUMNS.index("DRAM_Rd") - 2] = c
        return (header + "\\n" + x + "," + y + "," + ",".join(nums) + "\\n").encode()
    ok = parse(fixture("a", "k", "0", "0", "1"), verify_blob=False)
    assert len(ok) == 1 and ok[0]["DRAM_Rd"] == 1
    # calculate needs at least one positive-denominator row, so add a control.
    sample = (fixture("a", "k", "0", "0", "1") +
              fixture("b", "k", "2", "1", "2").split(b"\\n", 1)[1])
    report = calculate(parse(sample, verify_blob=False))
    independent_oracle(parse(sample, verify_blob=False), report)
    assert report["positive_dram_with_zero_l1_read_misses"] == 1
    assert report["positive_dram_with_zero_l2_read_misses"] == 1
    invalids = [
        fixture("a", "k", "-1", "0", "1"),
        fixture("a", "k", "NaN", "0", "1"),
        fixture("a", "k", "Infinity", "0", "1"),
        fixture("a", "k", "oops", "0", "1"),
        fixture("a", "k", "0", "0", "1") + fixture("a", "k", "0", "0", "1").split(b"\\n", 1)[1],
        b"broken\\n",
        b"\\xff\\xfe",
    ]
    for data in invalids:
        try:
            parse(data, verify_blob=False)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid CSV accepted")
    try:
        parse(sample, verify_blob=True)
    except ValueError:
        pass
    else:
        raise AssertionError("unpinned fixture accepted")
    return {"status": "PASS", "synthetic_oracle_cases": 1,
            "malformed_counter_refusals": len(invalids), "hash_refusal": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--input", help="optional local copy of pinned upstream CSV")
    args = parser.parse_args()
    if args.selftest:
        print(json.dumps(selftest(), indent=2, sort_keys=True))
        return
    if args.input:
        with open(args.input, "rb") as stream:
            data = stream.read(100_001)
    else:
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read(100_001)
    rows = parse(data)
    result = calculate(rows)
    independent_oracle(rows, result)
    assert result["rows"] == 25
    assert result["positive_dram_with_zero_l1_read_misses"] == 5
    assert result["positive_dram_with_zero_l2_read_misses"] == 3
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
