#!/usr/bin/env python3
"""Independent 32-lane original-mask enumeration oracle for V309.

This is intentionally NOT an antichain implementation. It directly enumerates
the hidden active lanes and maps each printed address token to its original
rank. Validates the exact DP only when the combinatorial oracle is tractable.
No physical GPU bank, memory-transaction or performance inference.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
from random import Random
import json

from sector_antichain_dp import exact_sector_extrema


def original_mask_oracle(mask, width, tokens, *, lanes=32, max_choices=1200):
    """Return sharp sector extrema by independently enumerating original masks."""
    visible = tuple(i for i in range(lanes) if (mask >> i) & 1)
    hidden_candidates = tuple(i for i in range(lanes) if not ((mask >> i) & 1))
    hidden_count = len(tokens) - len(visible)
    if not visible or hidden_count < 0 or hidden_count > len(hidden_candidates):
        raise ValueError("incompatible visible mask / token count")
    choices = comb(len(hidden_candidates), hidden_count)
    if choices > max_choices:
        return None
    counts = []
    for hidden in combinations(hidden_candidates, hidden_count):
        active = sorted((*visible, *hidden))
        rank = {lane: j for j, lane in enumerate(active)}
        sectors = set()
        for lane in visible:
            address = int(tokens[rank[lane]])
            if address < 0 or address + width - 1 > (1 << 64) - 1:
                raise ValueError("out of range address")
            first, last = address // 32, (address + width - 1) // 32
            sectors.update(range(first, last + 1))
        counts.append(len(sectors))
    return min(counts), max(counts), choices


def make_tokens(rng, n, mode):
    if mode == 0:  # repeated footprints, sometimes crossing sector boundaries
        return [0x10000 + 32 * (i % 4) + (0, 4, 16, 28)[i % 4] for i in range(n)]
    if mode == 1:  # predicted no-win, one sector per token
        return [0x20000 + 32 * i for i in range(n)]
    if mode == 2:  # randomized aliases and boundary crossings
        return [0x30000 + 32 * rng.randrange(8) + rng.choice((0, 4, 24, 28, 31))
                for _ in range(n)]
    if mode == 3:  # near 64-bit address boundary without overflow
        base = (1 << 64) - 32 * (n + 2)
        return [base + 32 * i + (i % 3) for i in range(n)]
    raise AssertionError("unknown mode")


def selftest():
    rng = Random(30920261030)
    checked = ambiguous = completions = capped = 0
    per_mode = {str(i): 0 for i in range(4)}
    for k in (1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 30):
        for h in (0, 1, 2, 3):
            if k + h > 32 or comb(32 - k, h) > 1200:
                continue
            for trial in range(3):
                visible = rng.sample(range(32), k)
                mask = sum(1 << lane for lane in visible)
                n = k + h
                for mode in range(4):
                    tokens = make_tokens(rng, n, mode)
                    width = (1, 4, 8, 16)[(trial + mode) % 4]
                    expected = original_mask_oracle(mask, width, tokens)
                    assert expected is not None
                    lo, hi, meta = exact_sector_extrema(
                        mask, width, tokens, max_states=20000,
                        max_transitions=300000)
                    if meta["status"] != "exact":
                        assert lo is None and hi is None
                        assert meta["status"] in ("state_cap", "transition_cap")
                        capped += 1
                        continue
                    assert (lo, hi) == expected[:2], (
                        "32-lane DP/oracle disagreement", k, h, mode, mask,
                        width, (lo, hi), expected, meta)
                    checked += 1
                    per_mode[str(mode)] += 1
                    completions += expected[2]
                    ambiguous += int(expected[0] != expected[1])
                    # Translation by an exact sector multiple preserves all
                    # sector-union cardinalities, including boundary crossings.
                    shifted = [x + 32 * 7 for x in tokens]
                    if shifted[-1] + width - 1 <= (1 << 64) - 1:
                        a, b, m = exact_sector_extrema(
                            mask, width, shifted, max_states=20000,
                            max_transitions=300000)
                        assert m["status"] == "exact" and (a, b) == (lo, hi)
    # Explicit hidden lanes before, between and after visible lanes.
    for mask, width, tokens in (
        (1 << 31, 8, [0x1001f, 0x10040]),
        ((1 << 0) | (1 << 31), 4, [0x2001f, 0x20020, 0x20040]),
        ((1 << 15) | (1 << 16), 16, [0x1001c, 0x10020, 0x10040, 0x1005f]),
    ):
        expected = original_mask_oracle(mask, width, tokens)
        got = exact_sector_extrema(mask, width, tokens, max_states=20000)
        assert expected is not None and got[:2] == expected[:2]
        checked += 1
    # Budget and overflow must fail closed, never be mislabeled exact.
    lo, hi, meta = exact_sector_extrema(
        0b101010, 4, [0x1000 + 32*j for j in range(5)],
        lanes=8, max_transitions=1)
    assert lo is None and hi is None and meta["status"] == "transition_cap"
    lo, hi, meta = exact_sector_extrema(
        0b10, 8, [(1 << 64) - 1, 0x1000], lanes=3)
    assert lo is None and hi is None and meta["status"] == "unknown_address_overflow"
    assert checked >= 200, checked
    assert completions >= 2000, completions
    assert all(v > 0 for v in per_mode.values()), per_mode
    return {
        "status": "PASS",
        "oracle": "direct original-mask enumeration, not antichain",
        "lanes": 32,
        "exact_cases": checked,
        "distinct_mask_completions_checked": completions,
        "nonpoint_cases": ambiguous,
        "resource_refusals": capped,
        "mode_exact_counts": per_mode,
        "overflow_and_budget_refusal": "PASS",
        "evidence_tier": "synthetic source-conditional oracle, NOT measured GPU traffic",
    }


if __name__ == "__main__":
    print(json.dumps(selftest(), sort_keys=True))
