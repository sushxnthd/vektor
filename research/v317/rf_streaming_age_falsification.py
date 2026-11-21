"""V317 prospective streaming RF-bank issue falsification.

Synthetic bank-port service, NOT GPU IPC or matched physical timing.
Frozen before evaluation in FROZEN_STREAMING_AGE_TRANSFER_GATE_20261101.md.
"""
from collections import deque
from math import ceil
import json
import random

SLOTS = 4
PORTS = 2
CYCLES = 30_000
WARMUP = 3_000


def legal(mask, pairs):
    """Charge two physical operand reads, including same-bank operands."""
    demands = [0] * 16
    for i in range(SLOTS):
        if mask & (1 << i):
            a, b = pairs[i]
            demands[a] += 1
            demands[b] += 1
    return max(demands) <= PORTS


def priority(valid, pairs, ages=None):
    """Fixed-slot greedy order corresponding to rtl/vtile/rf_bank_arbiter.sv."""
    grant = 0
    for i in range(SLOTS):
        if valid & (1 << i) and legal(grant | (1 << i), pairs):
            grant |= 1 << i
    return grant


def exact(valid, pairs, ages=None):
    """Maximum cardinality; highest numeric mask breaks ties."""
    best = 0
    for mask in range(1 << SLOTS):
        if mask & ~valid or not legal(mask, pairs):
            continue
        if (mask.bit_count(), mask) > (best.bit_count(), best):
            best = mask
    return best


def age_aware(valid, pairs, ages):
    """Same maximum cardinality, then maximize total head waiting age."""
    best = 0
    best_score = (-1, -1, -1)
    for mask in range(1 << SLOTS):
        if mask & ~valid or not legal(mask, pairs):
            continue
        score = (
            mask.bit_count(),
            sum(ages[i] for i in range(SLOTS) if mask & (1 << i)),
            mask,
        )
        if score > best_score:
            best, best_score = mask, score
    return best


def arrivals(kind, p, seed):
    """Generate one common, deterministic arrival trace for all policies."""
    rng = random.Random(seed)
    streams = [[] for _ in range(CYCLES)]
    for cycle in range(CYCLES):
        for slot in range(SLOTS):
            if rng.random() >= p:
                continue
            if kind == "private":
                pair = (2 * slot, 2 * slot + 1)
            elif kind == "four_bank":
                pair = (rng.randrange(4), rng.randrange(4))
            elif kind == "mixture":
                offset = 0 if rng.random() < 0.70 else 4
                pair = (offset + rng.randrange(4), offset + rng.randrange(4))
            else:
                raise ValueError(kind)
            streams[cycle].append((slot, pair))
    return streams


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[ceil(q * len(ordered)) - 1]


def simulate(streams, selector):
    """FIFO per slot; arrivals before issue; no drops or hidden drains."""
    queues = [deque() for _ in range(SLOTS)]
    completed = [0] * SLOTS
    observed = []
    pending_peak = 0
    offered = 0
    served_after_warmup = 0
    max_wait_by_slot = [0] * SLOTS
    for cycle, events in enumerate(streams):
        for slot, pair in events:
            queues[slot].append((cycle, pair))
            offered += 1
        valid = sum(1 << i for i, q in enumerate(queues) if q)
        pairs = [q[0][1] if q else (0, 0) for q in queues]
        ages = [cycle - q[0][0] if q else 0 for q in queues]
        grant = selector(valid, pairs, ages)
        if grant & ~valid or not legal(grant, pairs):
            raise AssertionError("invalid bank grant")
        for i in range(SLOTS):
            if grant & (1 << i):
                arrival, _ = queues[i].popleft()
                completed[i] += 1
                if cycle >= WARMUP:
                    served_after_warmup += 1
                    latency = cycle - arrival + 1
                    observed.append(latency)
                    max_wait_by_slot[i] = max(max_wait_by_slot[i], latency)
        pending_peak = max(pending_peak, sum(map(len, queues)))
    backlog = [len(q) for q in queues]
    return {
        "offered": offered,
        "completed_total": sum(completed),
        "completed_after_warmup": served_after_warmup,
        "service_rate_after_warmup": round(
            served_after_warmup / (CYCLES - WARMUP), 6
        ),
        "backlog_final_by_slot": backlog,
        "backlog_total": sum(backlog),
        "backlog_peak": pending_peak,
        "completed_by_slot": completed,
        "latency_p50_cycles": percentile(observed, 0.50),
        "latency_p99_cycles": percentile(observed, 0.99),
        "latency_max_cycles": max(observed, default=None),
        "max_latency_by_slot": max_wait_by_slot,
    }


def two_bank_closed_form(a, b, c):
    """Exact finite-batch drain cycles with two banks and two ports each."""
    return max(a, b) + (c + 1) // 2


def two_bank_priority_drain(pairs):
    """Independent arbitrary-length greedy drain, preserving input order."""
    pending = list(pairs)
    cycles = 0
    while pending:
        demands = [0, 0]
        retained = []
        granted = 0
        for a, b in pending:
            needs = [0, 0]
            needs[a] += 1
            needs[b] += 1
            if all(demands[k] + needs[k] <= 2 for k in range(2)):
                for k in range(2):
                    demands[k] += needs[k]
                granted += 1
            else:
                retained.append((a, b))
        if not granted:
            raise AssertionError("stalled")
        pending = retained
        cycles += 1
    return cycles


def theorem_audit():
    rng = random.Random(317114)
    checked = 0
    first = None
    for n in range(1, 65):
        for _ in range(100):
            pairs = [(rng.randrange(2), rng.randrange(2)) for _ in range(n)]
            a = sum(x == (0, 0) for x in pairs)
            b = sum(x == (1, 1) for x in pairs)
            c = n - a - b
            predicted = two_bank_closed_form(a, b, c)
            actual = two_bank_priority_drain(pairs)
            if predicted != actual:
                first = {
                    "n": n, "pairs": pairs,
                    "predicted": predicted, "actual": actual,
                }
                break
            checked += 1
        if first:
            break
    return {"checked": checked, "counterexample": first}


def persistent_fairness():
    """Always-backlogged adversary; age reset represents next FIFO head."""
    pairs = [(0, 1)] * 4
    counts = {}
    for name, policy in [
        ("priority", priority), ("exact", exact), ("age_aware", age_aware)
    ]:
        served = [0] * 4
        age = [0] * 4
        for _ in range(1000):
            grant = policy(15, pairs, age)
            for i in range(4):
                if grant & (1 << i):
                    served[i] += 1
                    age[i] = 0
                else:
                    age[i] += 1
        counts[name] = {"service_by_slot": served, "total": sum(served)}
    return counts


def sweep():
    regimes = [
        ("frozen_no_win", "private", 0.55, 317110),
        ("frozen_possible_win", "four_bank", 0.48, 317111),
        ("unseen_transfer", "mixture", 0.52, 317113),
    ]
    out = {}
    for label, kind, p, seed in regimes:
        stream = arrivals(kind, p, seed)
        results = {
            name: simulate(stream, policy)
            for name, policy in [
                ("priority", priority), ("exact", exact),
                ("age_aware", age_aware),
            ]
        }
        pcount = results["priority"]["completed_after_warmup"]
        ecount = results["exact"]["completed_after_warmup"]
        out[label] = {
            "arrival_kind": kind, "p_per_slot": p, "seed": seed,
            "exact_over_priority_completed_ratio": round(
                ecount / pcount, 8
            ),
            "results": results,
        }
    return {
        "evidence_tier": "SYNTHETIC_FOUR_SLOT_RF_SERVICE_NOT_GPU_IPC",
        "cycles": CYCLES, "warmup": WARMUP,
        "ports_per_bank": PORTS,
        "two_bank_boundary": theorem_audit(),
        "persistent_fairness": persistent_fairness(),
        "regimes": out,
    }


if __name__ == "__main__":
    print(json.dumps(sweep(), indent=2, sort_keys=True))
