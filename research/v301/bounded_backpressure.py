"""V301 bounded-backpressure workload sensitivity (not a frozen holdout rerun).

Four potential return lanes are shared across all policies. When the upstream
32-entry buffer is full, the source is stalled; no produced event is discarded.
The completion path is modeled, not GPU warp issue, IPC, or energy.
"""
import argparse
import json
import random
import statistics
from collections import deque

POLICIES = ("queue_merge", "set4", "banked")
CASES = {
    "S1_medium_skew": (.65, 64, .45, 37),
    "S2_uniform": (.82, 128, 0., 128),
    "S3_hot": (.80, 16, .80, 29),
    "S4_low_load": (.15, 32, .45, 37),
}


def attempts(seed, cycles, offered, warps, hot, epoch_period):
    rng = random.Random(seed)
    rows = []
    for t in range(cycles):
        row = []
        for _ in range(4):
            if rng.random() < offered:
                warp = 0 if rng.random() < hot else rng.randrange(warps)
                row.append((warp, t // epoch_period, 1 << rng.randrange(8)))
        rows.append(row)
    return rows


def simulate(rows, policy, capacity=8, upstream=32):
    assert policy in POLICIES
    q = []  # (warp, epoch, OR mask, merged-event count)
    pending = deque()
    offered = produced = stalled = completed = writes = 0
    peak_pending = occupancy = 0
    for row in rows:
        for event in row:
            offered += 1
            if len(pending) < upstream:
                pending.append(event)
                produced += 1
            else:
                stalled += 1  # backpressured at the source, not dropped
        if policy == "banked":
            drained = set()
            newq = []
            for w, e, mask, n in q:
                bank = w % 2
                if bank not in drained:
                    drained.add(bank)
                    completed += n
                    writes += 1
                else:
                    newq.append((w, e, mask, n))
            q = newq
        elif q:
            w, e, mask, n = q.pop(0)
            completed += n
            writes += 1
        count = 0
        while pending and count < 4:
            w, e, mask = pending[0]
            found = None
            if policy != "banked":
                found = next((j for j, (qw, qe, _, _) in enumerate(q)
                              if (qw, qe) == (w, e)), None)
            if found is not None:
                qw, qe, oldmask, n = q[found]
                q[found] = (qw, qe, oldmask | mask, n + 1)
            else:
                if len(q) >= capacity:
                    break
                if policy == "set4" and sum(1 for qw, _, _, _ in q if qw % 2 == w % 2) >= 4:
                    break
                q.append((w, e, mask, 1))
            pending.popleft()
            count += 1
        occupancy += len(q)
        peak_pending = max(peak_pending, len(pending))
    inflight = sum(n for _, _, _, n in q) + len(pending)
    assert produced == completed + inflight
    assert offered == produced + stalled
    cycles = len(rows)
    return dict(offered=offered, produced=produced, stalled=stalled,
                completed=completed, inflight=inflight, writes=writes,
                completed_rate=completed / cycles,
                source_stall_fraction=stalled / offered if offered else 0,
                mean_q_occupancy=occupancy / cycles, peak_pending=peak_pending)


def evaluate(cycles=40000, seeds=range(301, 309)):
    result = {}
    for name, args in CASES.items():
        runs = {p: [] for p in POLICIES}
        for seed in seeds:
            rows = attempts(seed, cycles, *args)
            for policy in POLICIES:
                runs[policy].append(simulate(rows, policy))
        means = {p: {key: statistics.mean(r[key] for r in runs[p])
                     for key in ("completed_rate", "source_stall_fraction",
                                 "mean_q_occupancy", "peak_pending")}
                 for p in POLICIES}
        means["set4_over_full"] = means["set4"]["completed_rate"] / means["queue_merge"]["completed_rate"]
        means["banked_over_full"] = means["banked"]["completed_rate"] / means["queue_merge"]["completed_rate"]
        result[name] = means
    return result


def selftest():
    rows = attempts(2, 300, .8, 16, .5, 13)
    for p in POLICIES:
        for upstream in (1, 2, 8, 32):
            r = simulate(rows, p, upstream=upstream)
            assert r["completed"] <= r["produced"] <= r["offered"]
            assert r["peak_pending"] <= upstream
    print("bounded conservation and backpressure selftest: 12 configurations passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--cycles", type=int, default=40000)
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        print(json.dumps(evaluate(cycles=args.cycles), indent=2, sort_keys=True))
