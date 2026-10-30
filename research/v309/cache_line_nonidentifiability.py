#!/usr/bin/env python3
"""V309: falsify inference from sector-count reductions to cache-line traffic.

A deterministic counterexample under an EXPLICIT hypothetical 128-byte line-fill
LRU model, not an NVIDIA cache model, measured GPU data, or hardware speedup.
"""
from __future__ import annotations
import argparse
from collections import OrderedDict
from fractions import Fraction
from itertools import product
import json

SECTOR_BYTES = 32
LINE_BYTES = 128
I = 64
B = Fraction(8)
P = Fraction(1)
H = Fraction(1, 20)


def sectors(trace: tuple[tuple[int, ...], ...], sector_bytes: int = SECTOR_BYTES) -> int:
    return sum(len(set(warp)) for warp in trace)


def validate(trace: tuple[tuple[int, ...], ...], capacity: int, line_bytes: int) -> None:
    if not isinstance(capacity, int) or capacity <= 0:
        raise ValueError("capacity must be positive integer")
    if not isinstance(line_bytes, int) or line_bytes <= 0 or line_bytes % SECTOR_BYTES:
        raise ValueError("line size must be a positive multiple of 32")
    if not isinstance(trace, tuple) or not trace:
        raise ValueError("nonempty tuple trace required")
    for warp in trace:
        if not isinstance(warp, tuple) or not warp:
            raise ValueError("each instruction must have nonempty tuple of sectors")
        for addr in warp:
            if not isinstance(addr, int) or addr < 0 or addr % SECTOR_BYTES:
                raise ValueError("sector addresses must be nonnegative 32-byte aligned integers")


def lru_fills(trace: tuple[tuple[int, ...], ...], capacity: int = 4,
              line_bytes: int = LINE_BYTES) -> int:
    """Deterministic demand-only fully associative LRU line-fill count."""
    validate(trace, capacity, line_bytes)
    resident: OrderedDict[int, None] = OrderedDict()
    fills = 0
    for warp in trace:
        for addr in warp:
            line = addr // line_bytes
            if line in resident:
                resident.move_to_end(line)
            else:
                fills += 1
                if len(resident) == capacity:
                    resident.popitem(last=False)
                resident[line] = None
    return fills


def reference_fills(trace: tuple[tuple[int, ...], ...], capacity: int = 4,
                    line_bytes: int = LINE_BYTES) -> int:
    """Independent list-based recency oracle; does not call lru_fills."""
    validate(trace, capacity, line_bytes)
    recency: list[int] = []
    misses = 0
    for warp in trace:
        for addr in warp:
            tag = addr // line_bytes
            if tag in recency:
                recency.remove(tag)
            else:
                misses += 1
                if len(recency) == capacity:
                    del recency[0]
            recency.append(tag)
    return misses


def traces(family: str, n: int = I) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    if family == "same_line_reuse":
        original = (0, 32, 64, 96)
        changed = (0, 32, 64)
        return (tuple(original for _ in range(n)), tuple(changed for _ in range(n)))
    if family == "distinct_line_stream":
        return (tuple(tuple(512 * i + 128 * k for k in range(4)) for i in range(n)),
                tuple(tuple(512 * i + 128 * k for k in range(3)) for i in range(n)))
    raise ValueError("unknown family")


def throughput(instructions: int, fills: int, penalty: Fraction = Fraction(0),
               bandwidth: Fraction = B, issue: Fraction = P) -> Fraction:
    if instructions <= 0 or fills < 0 or penalty < 0 or bandwidth <= 0 or issue <= 0:
        raise ValueError("invalid service model")
    issue_time = Fraction(instructions) * (1 + penalty) / issue
    memory_time = Fraction(LINE_BYTES * fills) / bandwidth
    return Fraction(instructions) / max(issue_time, memory_time)


def sector_only_gain(n: int, before: int, after: int) -> Fraction:
    # Independent direct time-domain implementation of the old sector roofline.
    baseline_time = max(Fraction(n) / P, Fraction(SECTOR_BYTES * before) / B)
    changed_time = max(Fraction(n) * (1 + H) / P, Fraction(SECTOR_BYTES * after) / B)
    return baseline_time / changed_time - 1


def fstr(v: Fraction) -> str:
    return f"{v.numerator}/{v.denominator}"


def evaluate(family: str, capacity: int = 4) -> dict:
    before, after = traces(family)
    b_fills = lru_fills(before, capacity)
    a_fills = lru_fills(after, capacity)
    assert b_fills == reference_fills(before, capacity)
    assert a_fills == reference_fills(after, capacity)
    gain = throughput(I, a_fills, H) / throughput(I, b_fills) - 1
    same_addresses = lru_fills(before, capacity)
    return {
        "family": family, "instructions": I,
        "sector_count_before": sectors(before), "sector_count_after": sectors(after),
        "sector_reduction": fstr(1 - Fraction(sectors(after), sectors(before))),
        "cache_capacity_lines": capacity, "hypothetical_line_bytes": LINE_BYTES,
        "line_fills_before": b_fills, "line_fills_after": a_fills,
        "line_fill_reduction": fstr(1 - Fraction(a_fills, b_fills)),
        "sector_only_gain": fstr(sector_only_gain(I, sectors(before), sectors(after))),
        "line_fill_model_gain": fstr(gain),
        "equal_resource_unchanged_address_fill_reduction": fstr(
            1 - Fraction(same_addresses, b_fills)),
        "status": "WIN" if gain > 0 else "NO_WIN",
    }


def selftest() -> dict:
    templates = ((0,), (0, 32), (128,), (0, 128), (128, 256))
    comparisons = 0
    for length in range(1, 5):
        for seq in product(templates, repeat=length):
            trace = tuple(seq)
            for cap in (1, 2, 4, 8):
                assert lru_fills(trace, cap) == reference_fills(trace, cap)
                comparisons += 1
    # Frozen prediction and independent line-fill oracle at multiple capacities.
    for cap in (1, 2, 4, 8, 256):
        a = evaluate("same_line_reuse", cap)
        b = evaluate("distinct_line_stream", cap)
        assert (a["line_fills_before"], a["line_fills_after"]) == (1, 1)
        assert (b["line_fills_before"], b["line_fills_after"]) == (256, 192)
        assert a["line_fill_model_gain"] == "-1/21"
        assert b["line_fill_model_gain"] == "1/3"
        assert a["sector_only_gain"] == b["sector_only_gain"] == "1/3"
        assert a["equal_resource_unchanged_address_fill_reduction"] == "0"
        assert b["equal_resource_unchanged_address_fill_reduction"] == "0"
    invalids = 0
    for trace, cap, size in (
        (((-32,),), 4, 128), (((1,),), 4, 128), (((0,),), 0, 128),
        (((0,),), 4, 100), (tuple(), 4, 128), ((tuple(),), 4, 128),
        (((0,),), 4, 0),
    ):
        try:
            lru_fills(trace, cap, size)
        except ValueError:
            invalids += 1
        else:
            raise AssertionError("invalid cache input accepted")
    assert comparisons == 3120 and invalids == 7
    return {"status": "PASS", "independent_lru_oracle_cases": comparisons,
            "invalid_input_refusals": invalids, "cache_capacity_sensitivity_cases": 10}


def report() -> dict:
    a = evaluate("same_line_reuse")
    b = evaluate("distinct_line_stream")
    assert (a["instructions"], a["sector_count_before"], a["sector_count_after"]) == (
        b["instructions"], b["sector_count_before"], b["sector_count_after"])
    assert a["status"] == "NO_WIN" and b["status"] == "WIN"
    return {
        "status": "PASS",
        "evidence_tier": "SYNTHETIC_IDENTIFIABILITY_COUNTEREXAMPLE_NOT_GPU_MEASUREMENT",
        "gpu_hardware_mechanism_promoted": False,
        "historical_trace_producer_verified": False,
        "hypothetical_cache": {"line_bytes": LINE_BYTES, "capacity_lines": 4,
                               "policy": "fully_associative_demand_only_LRU_cold_start"},
        "service_assumptions": {"line_fill_bytes_per_cycle": fstr(B),
                                "issue_instructions_per_cycle": fstr(P),
                                "candidate_issue_time_penalty": fstr(H)},
        "cases": {"same_line_reuse": a, "distinct_line_stream": b},
        "conclusion": "identical_sector_counts_and_reduction_do_not_identify_memory_traffic_or_speedup_sign",
        "limitations": [
            "128-byte line fills are hypothetical, not authenticated V100 transactions",
            "synthetic traces are not unseen real workload holdouts",
            "candidate address changes are counterfactual and not functionally equivalent hardware",
            "no RTL, synthesis, timing, counters, or measured GPU throughput",
        ],
        "selftest": selftest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    print(json.dumps(selftest() if args.selftest else report(), indent=2, sort_keys=True))
