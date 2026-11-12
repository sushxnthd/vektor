"""Independent standard-library oracle for V317 frozen rotating holdouts.

No imports from the candidate simulator. This is synthetic RF-bank service,
not measured GPU IPC. Keep this code and the primary model separate.
"""
from collections import deque
from math import ceil
import json
import random

SLOTS = 4
CYCLES = 30000
WARMUP = 3000
REGIMES = (
    ("unseen_stable_no_win", "four_bank", .52, 317952),
    ("unseen_stressed_possible_win", "four_bank", .60, 317960),
    ("unseen_private_negative_control", "private", .55, 317955),
)


def legal(mask, pairs):
    reads = [0] * 16
    for i in range(SLOTS):
        if (mask >> i) & 1:
            a, b = pairs[i]
            reads[a] += 1
            reads[b] += 1
    return max(reads) <= 2


def choose(name, valid, pairs, ages, cycle):
    if name in ("fixed_priority", "rotating_priority", "oldest_first_greedy"):
        if name == "fixed_priority":
            order = list(range(SLOTS))
        elif name == "rotating_priority":
            order = [(cycle + i) % SLOTS for i in range(SLOTS)]
        else:
            order = sorted(range(SLOTS), key=lambda i: (-ages[i], i))
        grant = 0
        for i in order:
            if (valid >> i) & 1 and legal(grant | (1 << i), pairs):
                grant |= 1 << i
        return grant
    if name != "age_aware_exact":
        raise ValueError(name)
    best = 0
    score_best = (-1, -1, -1)
    for mask in range(1 << SLOTS):
        if mask & ~valid or not legal(mask, pairs):
            continue
        score = (
            mask.bit_count(),
            sum(ages[i] for i in range(SLOTS) if (mask >> i) & 1),
            mask,
        )
        if score > score_best:
            best, score_best = mask, score
    return best


def make_stream(kind, p, seed):
    rng = random.Random(seed)
    events = []
    for _ in range(CYCLES):
        cycle_events = []
        for slot in range(SLOTS):
            if rng.random() >= p:
                continue
            if kind == "private":
                pair = (2 * slot, 2 * slot + 1)
            else:
                pair = (rng.randrange(4), rng.randrange(4))
            cycle_events.append((slot, pair))
        events.append(cycle_events)
    return events


def run(stream, policy):
    queues = [deque() for _ in range(SLOTS)]
    completed = 0
    latencies = []
    for cycle, events in enumerate(stream):
        for slot, pair in events:
            queues[slot].append((cycle, pair))
        valid = sum(1 << i for i in range(SLOTS) if queues[i])
        pairs = [q[0][1] if q else (0, 0) for q in queues]
        ages = [cycle - q[0][0] if q else 0 for q in queues]
        grant = choose(policy, valid, pairs, ages, cycle)
        if not legal(grant, pairs):
            raise AssertionError("bank port overflow")
        for slot in range(SLOTS):
            if (grant >> slot) & 1:
                arrival, _ = queues[slot].popleft()
                if cycle >= WARMUP:
                    completed += 1
                    latencies.append(cycle - arrival + 1)
    latencies.sort()
    return {
        "completed_after_warmup": completed,
        "backlog_total": sum(map(len, queues)),
        "latency_p99_cycles": latencies[ceil(.99 * len(latencies)) - 1],
    }


def audit():
    out = {}
    for label, kind, p, seed in REGIMES:
        stream = make_stream(kind, p, seed)
        out[label] = {
            name: run(stream, name)
            for name in (
                "fixed_priority", "rotating_priority",
                "oldest_first_greedy", "age_aware_exact",
            )
        }
    return out


def verify_primary(primary, independent):
    for regime, policies in independent.items():
        for name, row in policies.items():
            actual = primary["regimes"][regime]["results"][name]
            for metric, expected in row.items():
                if actual[metric] != expected:
                    raise AssertionError(
                        f"{regime}/{name}/{metric}: primary={actual[metric]} independent={expected}"
                    )


if __name__ == "__main__":
    import sys
    result = audit()
    if len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            verify_primary(json.load(f), result)
    print(json.dumps({"evidence_tier": "INDEPENDENT_SYNTHETIC_ORACLE",
                      "results": result}, indent=2, sort_keys=True))
